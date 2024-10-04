<script lang="ts">
    import FileTree from './FileTree.svelte';
    import { fileContent, selectedFilePath, reloadFileTree } from '../stores/file_store';
    import { createFile, updateFile, getFileByPath } from '../api/files';


    // Local variables
    let newFilePath: string = '';
    let newFileContent: string = '';
    let isEditing: boolean = false;

    // Fetch file content when a file is selected
    $: if ($selectedFilePath) {
        getFileByPath($selectedFilePath).then((file) => {
            fileContent.set(file.content);
            isEditing = true;
        }).catch(() => {
            fileContent.set('');
            isEditing = false;
        });
    } else {
        fileContent.set('');
        isEditing = false;
    }

    // Function to handle file upload or update
    async function saveFile() {
        if (isEditing) {
            // Update existing file
            try {
                const file = await getFileByPath($selectedFilePath);
                await updateFile(file.id, $fileContent);
                alert('File updated successfully.');

            } catch (error) {
                alert('Error updating file.');
            }
        } else {
            // Create new file
            if (newFilePath.trim() === '') {
                alert('Please specify a file path.');
                return;
            }
            try {
                await createFile(newFilePath, newFileContent);
                alert('File created successfully.');
                newFilePath = '';
                newFileContent = '';
            } catch (error) {
                alert('Error creating file. File path may already exist.');
            }
        }
    }
</script>

<style>
    /* Add any additional custom styles here */
</style>

<div class="flex min-h-screen w-full bg-[#0d1117] text-slate-300">
    <!-- Left Side: File Tree -->
    <div class="w-1/4 border-r border-gray-700 p-4">
        <FileTree {reloadFileTree} />
    </div>

    <!-- Right Side: File Editor -->
    <div class="w-3/4 p-8">
        <h1 class="mb-4 text-2xl font-bold">
            {isEditing ? 'Edit File' : 'Upload New File'}
        </h1>
        <form class="space-y-6" on:submit|preventDefault={saveFile}>
            {#if isEditing}
                <!-- Editing Existing File -->
                <div>
                    <label for="file-path-input" class="block text-sm font-medium">Agent Description</label>
                    <input
                            id="file-path-input"
                            type="text"
                            class="mt-1 block w-full rounded-md border-gray-300 bg-[#161b22] px-4 py-2 text-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            placeholder="Enter agent description"
                            bind:value={$selectedFilePath}
                            required
                    />
                </div>
                <div>
                    <label for="file-content-edit" class="block text-sm font-medium">Content</label>
                    <textarea
                            id="file-content-edit"
                            class="mt-1 block w-full rounded-md border-gray-300 bg-[#161b22] px-4 py-2 text-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            rows="15"
                            bind:value={$fileContent}
                            required
                    ></textarea>
                </div>
            {:else}
                <!-- Uploading New File -->
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
            {/if}
            <div>
                <button
                        type="submit"
                        class="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                    {#if isEditing}
                        Save Changes
                    {:else}
                        Upload File
                    {/if}
                </button>
            </div>
        </form>
    </div>
</div>
