<script lang="ts">
    import App_sidebar from "./app_sidebar.svelte"
    import Generation_sidebar from './generation_sidebar.svelte';
    import {app_mode, sidebarVisible} from '../stores/app_store.js';
    import Chat from './chat.svelte';
    import AgentCreation from './agent_creation.svelte';
    import AgentSelection from "./agent_selection.svelte"
    import AgentUpdate from "./agent_update.svelte";

    function newChat() {

        sidebar.handleNewChat();
    }

    let sidebar: App_sidebar;
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
        <Generation_sidebar/>
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