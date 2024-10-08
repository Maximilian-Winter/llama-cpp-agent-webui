<script lang="ts">
    import { chats, current_chat, text } from '$lib/stores/app_store.js';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import ChatComponent from '$lib/components/ChatComponent.svelte';

    onMount(async () => {
        if ($current_chat.id === -1) {
            // If there's no current chat, redirect to the home page or show a message
            await goto('/');
        }
    });

    $: {
        if ($current_chat.id !== -1) {
            goto(`/chat/${$current_chat.id}`, { replaceState: true });
        }
    }
</script>

{#if $current_chat.id !== -1}
    <ChatComponent />
{:else}
    <p>No chat selected. Please choose a chat from the sidebar or start a new one.</p>
{/if}