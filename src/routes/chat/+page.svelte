<script lang="ts">
    import { chats, current_chat, text } from '$lib/stores/app_store';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    onMount(async () => {
        if ($current_chat.id === -1) {
            // If there's no current chat, redirect to the home page or show a message
            await goto('/');
        }
    });

    async function gotoChat(id: number) {
        await goto(`/chat/${id}`);
    }
</script>

{#if $current_chat.id !== -1}
    {gotoChat($current_chat.id)}
{:else}
    <p>No chat selected. Please choose a chat from the sidebar or start a new one.</p>
{/if}