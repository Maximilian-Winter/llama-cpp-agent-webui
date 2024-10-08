<script lang="ts">
    import { onMount } from "svelte";
    import FileTree from '$lib/components/file_tree.svelte';
    import { reloadFileTree } from '$lib/stores/file_store';
    import { getFilePaths, createFile } from '$lib/api/files';
    import type { FilePathResponse } from "$lib/types/api";
    import { Upload, Plus, X } from 'lucide-svelte';

    let files: FilePathResponse[] = [];
    let newFilePath: string = '';
    let newFileContent: string = '';
    let fileInput: HTMLInputElement;
    let createMethod: 'upload' | 'manual' = 'upload';
    let showModal = false;
    let uploadedFile: File | null = null;
    let serverFilePath: string = '';

    onMount(async () => {
        await loadFiles();
    });

    async function loadFiles() {
        files = await getFilePaths();
    }

    function handleFileSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        const file = (target.files as FileList)[0];
        if (file) {
            uploadedFile = file;
            serverFilePath = file.name;
            showModal = true;
        }
    }

    async function uploadFile() {
        if (uploadedFile) {
            const reader = new FileReader();
            reader.onload = async (e: ProgressEvent<FileReader>) => {
                const content = e.target?.result as string;
                await saveFile(content);
            };
            reader.readAsText(uploadedFile);
        }
    }

    async function saveFile(content?: string) {
        try {
            await createFile(serverFilePath, content || newFileContent);
            alert('File created successfully.');
            newFilePath = '';
            newFileContent = '';
            if (fileInput) fileInput.value = ''; // Reset file input
            showModal = false;
            uploadedFile = null;
            await loadFiles();
            reloadFileTree.update(n => n + 1);
        } catch (error) {
            alert('Error creating file. Please try again.');
        }
    }
</script>

<div class="flex min-h-screen bg-[#0d1117] text-slate-300">
    <!-- Left Side: File Tree -->
    <div class="w-1/4 border-r border-gray-700 p-4 overflow-y-auto">
        <h2 class="text-xl font-bold mb-4 text-blue-400">File Explorer</h2>
        <FileTree {files} />
    </div>

    <!-- Right Side: File Upload/Creation -->
    <div class="w-3/4 p-8">
        <h1 class="mb-6 text-3xl font-bold text-blue-400">Create New File</h1>
        <div class="mb-6 flex space-x-4">
            <button
                    class={`px-4 py-2 rounded-md transition-colors duration-200 ${createMethod === 'upload' ? 'bg-blue-600 text-white' : 'bg-[#1c2128] text-slate-300 hover:bg-[#2c3138]'}`}
                    on:click={() => createMethod = 'upload'}
            >
                <Upload class="inline-block mr-2" size={18} />
                Upload File
            </button>
            <button
                    class={`px-4 py-2 rounded-md transition-colors duration-200 ${createMethod === 'manual' ? 'bg-blue-600 text-white' : 'bg-[#1c2128] text-slate-300 hover:bg-[#2c3138]'}`}
                    on:click={() => createMethod = 'manual'}
            >
                <Plus class="inline-block mr-2" size={18} />
                Create Manually
            </button>
        </div>
        {#if createMethod === 'upload'}
            <div class="bg-[#1c2128] p-6 rounded-lg">
                <label for="file-upload" class="block text-sm font-medium mb-2">Choose File</label>
                <input
                        id="file-upload"
                        type="file"
                        class="block w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
                        on:change={handleFileSelect}
                        bind:this={fileInput}
                />
            </div>
        {:else}
            <form class="space-y-6 bg-[#1c2128] p-6 rounded-lg" on:submit|preventDefault={() => saveFile()}>
                <div>
                    <label for="new-file-path-input" class="block text-sm font-medium mb-2">File Path</label>
                    <input
                            id="new-file-path-input"
                            type="text"
                            class="w-full rounded-md border-gray-700 bg-[#2c3138] px-4 py-2 text-slate-200 focus:border-blue-500 focus:ring-blue-500"
                            placeholder="Enter file path (e.g., /folder/file.txt)"
                            bind:value={newFilePath}
                            required
                    />
                </div>
                <div>
                    <label for="new-file-content-input" class="block text-sm font-medium mb-2">Content</label>
                    <textarea
                            id="new-file-content-input"
                            class="w-full rounded-md border-gray-700 bg-[#2c3138] px-4 py-2 text-slate-200 focus:border-blue-500 focus:ring-blue-500"
                            rows="15"
                            bind:value={newFileContent}
                            required
                    ></textarea>
                </div>
                <div>
                    <button
                            type="submit"
                            class="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                        <Plus class="mr-2" size={18} />
                        Create File
                    </button>
                </div>
            </form>
        {/if}
    </div>
</div>

{#if showModal}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-[#1c2128] p-6 rounded-lg shadow-xl w-96">
            <h3 class="text-lg font-medium text-slate-200 mb-4">Specify Server File Path</h3>
            <input
                    type="text"
                    class="w-full px-3 py-2 text-slate-200 border rounded-lg focus:outline-none bg-[#2c3138] mb-4"
                    bind:value={serverFilePath}
                    placeholder="Enter server file path"
            />
            <div class="flex justify-end space-x-3">
                <button
                        class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                        on:click={uploadFile}
                >
                    Upload
                </button>
                <button
                        class="px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                        on:click={() => showModal = false}
                >
                    Cancel
                </button>
            </div>
        </div>
    </div>
{/if}