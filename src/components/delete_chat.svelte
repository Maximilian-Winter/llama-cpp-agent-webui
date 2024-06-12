<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import {Agent} from "../stores/app_store.js";

    const dispatch = createEventDispatcher();
    export let chatId: number;
    function delete_chat(id: number) {
        dispatch('delete_chat', {
            id
        });
    }

    function closePopup() {
        dispatch('close');
    }
</script>

<div class="popup">
    <div class="popup-content">
        <h2>Delete Chat</h2>
        <p>Are you sure you want to delete this chat?</p>
        <div class="button-group">
            <button on:click={() => delete_chat(chatId)} class="delete-btn">Delete</button>
            <button on:click={closePopup} class="cancel-btn">Cancel</button>
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
        background-color: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .popup-content {
        padding: 30px;
        width: 90%;
        max-width: 400px;
        background: #161b22;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }

    h2 {
        margin-top: 0;
        margin-bottom: 20px;
        color: #ffffff;
        font-size: 24px;
    }

    p {
        margin-bottom: 30px;
        color: #c9d1d9;
        font-size: 18px;
    }

    .button-group {
        display: flex;
        justify-content: center;
        gap: 20px;
    }

    .delete-btn,
    .cancel-btn {
        padding: 12px 24px;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .delete-btn {
        background-color: #ff4d4d;
        color: white;
    }

    .delete-btn:hover {
        background-color: #e60000;
    }

    .cancel-btn {
        background-color: #30363d;
        color: white;
    }

    .cancel-btn:hover {
        background-color: #484f58;
    }
</style>