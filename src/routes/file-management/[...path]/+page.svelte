<script lang="ts">
    import { page } from '$app/stores';
    import {onMount, tick} from 'svelte';
    import FileTree from '$lib/components/file_tree.svelte';
    import { getFilePaths, getFileByPath, updateFile, deleteFile } from '$lib/api/files';
    import type { FilePathResponse, FileResponse } from "$lib/types/api";
    import { selectedFilePath, reloadFileTree } from "$lib/stores/file_store";
    import { Pencil, Save, X, Delete } from 'lucide-svelte';
    import {goto} from "$app/navigation";
    import hljs from 'highlight.js';

    let files: FilePathResponse[] = [];
    let currentFilePath = '';
    let currentFileName = '';
    let fileContent = '';
    let isEditing = false;
    let currentFileId: number | null = null;

    onMount(async () => {
        await loadFiles();
        currentFilePath = $page.params.path;
        await handleFile();

    });

    async function loadFiles() {
        files = await getFilePaths();
    }

    selectedFilePath.subscribe((filePath) => {
        if (filePath !== '') {
            currentFilePath = filePath;

        }
    });
    async function _goto(url: string): Promise<void> {
        await goto(url);
    }
    async function handleFile() {
        if (currentFilePath) {
            try {
                const file: FileResponse = await getFileByPath(currentFilePath);
                fileContent = file.content;
                currentFileName = file.filename;
                currentFileId = file.id;
                isEditing = false;

            } catch (error) {
                console.error('Error fetching file:', error);
                fileContent = 'Error: File not found or couldn\'t be loaded.';
            }
        }
    }

    async function toggleEdit() {
        isEditing = !isEditing;
    }
    async function handleDeleteFile()
    {
        await deleteFile(currentFileId ?? -1)
        await _goto("/file-management")
    }

    async function saveFile() {
        if (currentFileId !== null) {
            try {
                await updateFile(currentFileId, fileContent);
                alert('File updated successfully.');
                isEditing = false;
                await loadFiles();
                reloadFileTree.update(n => n + 1);
            } catch (error) {
                alert('Error updating file. Please try again.');
            }
        }
    }
</script>

<div class="flex min-h-screen w-full bg-[#0d1117] text-slate-300">
    <!-- Left Side: File Tree -->
    <div class="w-1/4 border-r border-gray-700 p-4">
        <h2 class="text-xl font-bold mb-4">File Explorer</h2>
        <FileTree {files} />
    </div>

    <!-- Right Side: File Viewer or Editor -->
    <div class="w-3/4 p-8">
        {#if currentFilePath}
            <div class="flex justify-between items-center mb-6">
                <div>
                    <h1 class="text-2xl font-bold">{currentFileName}</h1>
                    <h2 class="text-sm text-slate-400 mt-1">Path: {currentFilePath.replace(currentFileName, '')}</h2>
                </div>
                <button
                        class="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-300"
                        on:click={toggleEdit}
                >
                    {#if isEditing}
                        <X size={18} />
                        Cancel
                    {:else}
                        <Pencil size={18} />
                        Edit
                    {/if}
                </button>
                {#if !isEditing}
                <button
                        class="flex items-center gap-2 bg-red-600 hover:bg-red-950 text-white font-bold py-2 px-4 rounded transition duration-300"
                        on:click={handleDeleteFile}
                >
                    <Delete size={18} />
                    Delete File
                </button>
                {/if}
            </div>
            <div class="relative">
                <textarea
                        class="w-full h-[calc(100vh-12rem)] bg-[#161b22] p-4 rounded-md text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-mono"
                        bind:value={fileContent}
                        disabled={!isEditing}
                ></textarea>

                {#if isEditing}
                    <button
                            class="absolute bottom-4 right-4 flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition duration-300"
                            on:click={saveFile}
                    >
                        <Save size={18} />
                        Save Changes
                    </button>
                {/if}
            </div>
        {:else}
            <div class="flex items-center justify-center h-[calc(100vh-8rem)]">
                <h1 class="text-2xl font-bold">Select a file to view</h1>
            </div>
        {/if}
    </div>
</div>