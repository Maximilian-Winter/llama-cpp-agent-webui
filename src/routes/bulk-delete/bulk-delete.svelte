<script lang="ts">
    import { onMount } from 'svelte';
    import { getAllChats, deleteChat } from '$lib/api/chats';
    import { getFilePaths, deleteFile } from '$lib/api/files';
    import { Chat } from '$lib/stores/app_store';
    import type { FilePathResponse } from "$lib/types/api";
    import { Trash2 } from 'lucide-svelte';

    let chat_items: Chat[] = [];
    let files: FilePathResponse[] = [];
    let selectedItems: Set<number> = new Set();
    let itemType: 'chats' | 'files' = 'chats';
    let isLoading = true;
    let isDeleting = false;

    onMount(async () => {
        await loadItems();
    });

    async function loadItems() {
        isLoading = true;
        if (itemType === 'chats') {
            chat_items = await getAllChats();
        } else {
            files = await getFilePaths();
        }
        isLoading = false;
        selectedItems.clear();
    }

    function toggleSelectAll(event: Event) {
        const target = event.target as HTMLInputElement;
        if (target.checked) {
            if(itemType == "chats") {
                selectedItems = new Set(chat_items.map(item => item.id));
            }
            else {
                selectedItems = new Set(files.map(item => item.id));
            }
        } else {
            selectedItems.clear();
        }
        selectedItems = selectedItems; // Trigger reactivity
    }

    function toggleSelectItem(id: number) {
        if (selectedItems.has(id)) {
            selectedItems.delete(id);
        } else {
            selectedItems.add(id);
        }
        selectedItems = selectedItems; // Trigger reactivity
    }

    async function handleDelete() {
        if (selectedItems.size === 0) return;

        isDeleting = true;
        const deletePromises = Array.from(selectedItems).map(id => {
            if (itemType === 'chats') {
                return deleteChat(id);
            } else {
                return deleteFile(id);
            }
        });

        try {
            await Promise.all(deletePromises);
            await loadItems();
        } catch (error) {
            console.error('Error deleting items:', error);
            alert('An error occurred while deleting items. Please try again.');
        } finally {
            isDeleting = false;
        }
    }
</script>

<div class="min-h-screen w-full bg-[#0d1117] text-slate-300 p-8">
    <h1 class="text-3xl font-bold mb-8">Bulk Delete {itemType === 'chats' ? 'Chats' : 'Files'}</h1>

    <div class="mb-6">
        <label class="inline-flex items-center mr-4">
            <input type="radio" class="form-radio" name="itemType" value="chats" bind:group={itemType} on:change={loadItems}>
            <span class="ml-2">Chats</span>
        </label>
        <label class="inline-flex items-center">
            <input type="radio" class="form-radio" name="itemType" value="files" bind:group={itemType} on:change={loadItems}>
            <span class="ml-2">Files</span>
        </label>
    </div>

    {#if isLoading}
        <p class="text-center">Loading...</p>
    {:else}
        <div class="bg-[#1c2128] rounded-lg shadow-lg overflow-hidden">
            <div class="p-4 border-b border-slate-700 flex justify-between items-center">
                <label class="inline-flex items-center">
                    <input type="checkbox" class="form-checkbox" on:change={toggleSelectAll}>
                    <span class="ml-2">Select All</span>
                </label>
                <button
                        class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded inline-flex items-center transition duration-300 disabled:opacity-50"
                        on:click={handleDelete}
                        disabled={selectedItems.size === 0 || isDeleting}
                >
                    <Trash2 size={18} class="mr-2" />
                    Delete Selected
                </button>
            </div>
            <ul class="divide-y divide-slate-700">
                {#if itemType === 'files'}

                    {#each files as item (item.id)}
                        <li class="p-4 hover:bg-[#2c3138] transition duration-300">
                            <label class="inline-flex items-center w-full cursor-pointer">
                                <input
                                        type="checkbox"
                                        class="form-checkbox"
                                        checked={selectedItems.has(item.id)}
                                        on:change={() => toggleSelectItem(item.id)}
                                >
                                <span class="ml-2">
                                    {(item).path}
                                </span>

                            </label>
                        </li>
                    {/each}
                {:else}
                    {#each chat_items as item (item.id)}
                        <li class="p-4 hover:bg-[#2c3138] transition duration-300">
                            <label class="inline-flex items-center w-full cursor-pointer">
                                <input
                                        type="checkbox"
                                        class="form-checkbox"
                                        checked={selectedItems.has(item.id)}
                                        on:change={() => toggleSelectItem(item.id)}
                                >
                                <span class="ml-2">
                                    {(item).title}

                                </span>
                                <span class="ml-2">
                                    {(item).timestamp}

                                </span>

                            </label>
                        </li>
                    {/each}
                {/if}
            </ul>
        </div>
    {/if}
</div>