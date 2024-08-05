<script lang="ts">
    import App_sidebar from "./app_sidebar.svelte"
    import Generation_sidebar from './generation_sidebar.svelte';
    import { app_mode, current_chat, sidebarVisible } from '../stores/app_store.js';
    import Chat from './chat.svelte';
    import AgentCreation from './agent_creation.svelte';
    import AgentSelection from "./agent_selection.svelte"
    import AgentUpdate from "./agent_update.svelte";
    import 'highlight.js/styles/github-dark.css';
    function newChat() {

        sidebar.handleNewChat();
    }

    let sidebar: App_sidebar;

    async function handleUpdateSettings(event: CustomEvent) {
        const newSettings = event.detail;
        const response = await fetch(`http://localhost:8042/chats/${$current_chat.id}/settings`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newSettings),
        });

        if (!response.ok) {
            console.error('Failed to update settings on backend');
        }
    }
</script>


<div class="flex flex-row bg-[#0d1117]">
    <!-- Sidebar -->
    <App_sidebar bind:this={sidebar}/>
    {#if $app_mode === 'agent_creation'}
        <AgentCreation/>
    {:else if $app_mode === 'chat'}
        <Chat on:newChat={newChat}/>
    {:else if $app_mode === 'agent_update'}
        <AgentUpdate/>
    {:else if $app_mode === 'agent_selection'}
        <AgentSelection on:newChat={newChat}/>
    {/if}

    {#if $sidebarVisible}
        <Generation_sidebar on:updateSettings={handleUpdateSettings} />
    {:else}
        <div class="hidden">
            <!-- This is technically not visible, but you can place additional logic or styling here if needed. -->
        </div>
    {/if}
    <!-- Sidebar -->

</div>

<style>
    .hidden {
        transform: translateX(-100%);
    }

</style>