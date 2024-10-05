<script lang="ts">
    import { onMount } from "svelte";
    import FileTree from '$lib/components/file_tree.svelte';
    import { reloadFileTree } from '$lib/stores/file_store';
    import { getFilePaths, createFile } from '$lib/api/files';
    import type { FilePathResponse } from "$lib/types/api";

    // Local variables
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

    // Function to handle file selection
    function handleFileSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        const file = (target.files as FileList)[0];
        if (file) {
            uploadedFile = file;
            serverFilePath = file.name;
            showModal = true;
        }
    }

    // Function to handle file upload
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

    // Function to handle manual file creation or upload
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

<div class="flex min-h-screen w-full bg-[#0d1117] text-slate-300">
    <!-- Left Side: File Tree -->
    <div class="w-1/4 border-r border-gray-700 p-4">
        <h2 class="text-xl font-bold mb-4">File Explorer</h2>
        <FileTree {files} />
    </div>

    <!-- Right Side: File Upload/Creation -->
    <div class="w-3/4 p-8">
        <h1 class="mb-4 text-2xl font-bold">Create New File</h1>
        <div class="mb-4">
            <label class="inline-flex items-center mr-4">
                <input type="radio" class="form-radio" name="createMethod" value="upload" bind:group={createMethod}>
                <span class="ml-2">Upload File</span>
            </label>
            <label class="inline-flex items-center">
                <input type="radio" class="form-radio" name="createMethod" value="manual" bind:group={createMethod}>
                <span class="ml-2">Create Manually</span>
            </label>
        </div>
        {#if createMethod === 'upload'}
            <div>
                <label for="file-upload" class="block text-sm font-medium">Choose File</label>
                <input
                        id="file-upload"
                        type="file"
                        class="mt-1 block w-full text-slate-200"
                        on:change={handleFileSelect}
                        bind:this={fileInput}
                />
            </div>
        {:else}
            <form class="space-y-6" on:submit|preventDefault={() => saveFile()}>
                <div>
                    <label for="new-file-path-input" class="block text-sm font-medium">File Path</label>
                    <input
                            id="new-file-path-input"
                            type="text"
                            class="mt-1 block w-full rounded-md border-gray-300 bg-[#161b22] px-4 py-2 text-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            placeholder="Enter file path (e.g., /folder/file.txt)"
                            bind:value={newFilePath}
                            required
                    />
                </div>
                <div>
                    <label for="new-file-content-input" class="block text-sm font-medium">Content</label>
                    <textarea
                            id="new-file-content-input"
                            class="mt-1 block w-full rounded-md border-gray-300 bg-[#161b22] px-4 py-2 text-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            rows="15"
                            bind:value={newFileContent}
                            required
                    ></textarea>
                </div>
                <div>
                    <button
                            type="submit"
                            class="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                        Create File
                    </button>
                </div>
            </form>
        {/if}
    </div>
</div>

{#if showModal}
    <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full" id="my-modal">
        <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-[#161b22]">
            <div class="mt-3 text-center">
                <h3 class="text-lg leading-6 font-medium text-slate-200">Specify Server File Path</h3>
                <div class="mt-2 px-7 py-3">
                    <input
                            type="text"
                            class="w-full px-3 py-2 text-slate-200 border rounded-lg focus:outline-none bg-[#0d1117]"
                            bind:value={serverFilePath}
                            placeholder="Enter server file path"
                    />
                </div>
                <div class="items-center px-4 py-3">
                    <button
                            id="ok-btn"
                            class="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
                            on:click={uploadFile}
                    >
                        Upload
                    </button>
                    <button
                            id="cancel-btn"
                            class="mt-3 px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-300"
                            on:click={() => showModal = false}
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}