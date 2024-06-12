<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import {Chat} from "../stores/app_store.js";

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

<style>
    .popup {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000; /* Ensure it is above all other content */
    }

    .popup-content {
        padding: 20px;
        width: 90%;
        max-width: 500px;
        background: #0d1117; /* Dark background */
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .title-input {
        width: 100%;
        padding: 10px;
        margin-bottom: 20px;
        border: 2px solid #30363d;
        background: #171E28;
        color: #c9d1d9;
        border-radius: 6px;
        box-sizing: border-box; /* Avoids border and padding being added to the width */
    }

    .button-group {
        display: flex;
        justify-content: space-between;
    }

    .save-btn, .cancel-btn {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .save-btn {
        background-color: #238636; /* Green button for save */
        color: white;
    }

    .save-btn:hover {
        background-color: #2ea043;
    }

    .cancel-btn {
        background-color: #8b949e; /* Grey button for cancel */
        color: white;
    }

    .cancel-btn:hover {
        background-color: #b1bac4;
    }
</style>