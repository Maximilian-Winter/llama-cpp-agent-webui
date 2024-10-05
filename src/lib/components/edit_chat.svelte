<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import {Chat} from "$lib/stores/app_store.js";

    const dispatch = createEventDispatcher();
    export let chat: Chat;
    function saveTitle(id: number, title: string) {
        dispatch('save', {
             id, title
        });
    }

    function closePopup() {
        dispatch('close');
    }
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="w-11/12 max-w-lg rounded-lg bg-[#161b22] p-6 shadow-lg">
        <h2 class="mb-4 text-xl font-bold text-slate-200">Edit Chat Title</h2>
        <input class="mb-6 w-full rounded-md border border-[#30363d] bg-[#0d1117] px-4 py-2 text-slate-200 focus:border-blue-500 focus:outline-none" bind:value={chat.title} placeholder="Enter chat title" />
        <div class="flex justify-end space-x-4">
            <button class="rounded-md bg-[#238636] px-4 py-2 font-semibold text-white transition duration-200 ease-in-out hover:bg-[#2ea043] focus:outline-none" on:click={() => saveTitle(chat.id, chat.title)}>Save</button>
            <button class="rounded-md bg-[#30363d] px-4 py-2 font-semibold text-slate-200 transition duration-200 ease-in-out hover:bg-[#484f58] focus:outline-none" on:click={closePopup}>Cancel</button>
        </div>
    </div>
</div>
