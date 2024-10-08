<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { getChatById } from '$lib/api/chats';
    import { current_chat } from '$lib/stores/app_store';
    import ChatComponent from '$lib/components/ChatComponent.svelte';

    let chatId: number;

    onMount(async () => {
        chatId = parseInt($page.params.id);
        try {
            const chat = await getChatById(chatId);
            current_chat.set(chat);
        } catch (error) {
            console.error('Failed to fetch chat:', error);
            // Handle error (e.g., show error message or redirect)
        }
    });
</script>

<ChatComponent />