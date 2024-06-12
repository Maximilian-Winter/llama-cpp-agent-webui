<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import {Agent} from "../stores/app_store.js";

    const dispatch = createEventDispatcher();
    export let agentId: number;
    function delete_agent(id: number) {
        dispatch('delete_agent', {
             id
        });
    }

    function closePopup() {
        dispatch('close');
    }
</script>

<div class="popup">
    <div class="popup-content">
        <p>Are you sure you want to delete the agent?</p>
        <div class="button-group">
            <button on:click={() => delete_agent(agentId)} class="save-btn">Delete</button>
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
        background-color: #740404; /* Green button for save */
        color: white;
    }

    .save-btn:hover {
        background-color: #a02e2e;
    }

    .cancel-btn {
        background-color: #8b949e; /* Grey button for cancel */
        color: white;
    }

    .cancel-btn:hover {
        background-color: #b1bac4;
    }
</style>