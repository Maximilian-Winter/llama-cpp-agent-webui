<script lang="ts">
    import "../app.scss";
    import AppSidebar from "$lib/components/app_sidebar.svelte";
    import GenerationSidebar from '$lib/components/generation_sidebar.svelte';
    import { sidebarVisible, current_chat } from '$lib/stores/app_store.js';
    import 'highlight.js/styles/github-dark.css';
    import {updateChatSettings} from "$lib/api/chats";

    async function handleUpdateSettings(event: CustomEvent) {
        const newSettings = event.detail;
        await updateChatSettings($current_chat.id, newSettings);
    }
</script>

<div class="flex flex-row bg-[#0d1117]">
    <AppSidebar />
    <main class="flex-grow">
        <slot />
    </main>
    {#if $sidebarVisible}
        <GenerationSidebar on:updateSettings={handleUpdateSettings} />
    {:else}
    <div class="hidden">
        <!-- This is technically not visible, but you can place additional logic or styling here if needed. -->
    </div>
    {/if}
</div>

<style>
    :global(body) {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .hidden {
        transform: translateX(-100%);
    }

</style>