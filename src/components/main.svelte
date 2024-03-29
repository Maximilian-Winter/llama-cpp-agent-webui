<script lang="ts">
    import App_sidebar from "./app_sidebar.svelte"
    import Generation_sidebar from './generation_sidebar.svelte';
    import {sidebarVisible, current_chat, max_tokens, min_p, rep_pen, rep_pen_range, text, tfsz, temperature, top_k , top_p, typ_p} from '../stores/app_store.js';
    import Chat from './chat.svelte';
</script>


<div class="flex flex-row bg-[#05060a]">
    <!-- Sidebar -->
    <App_sidebar/>
    <Chat/>
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