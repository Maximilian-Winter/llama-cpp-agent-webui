<script lang="ts">
    import { goto } from '$app/navigation';
    import {
        Chat,
        current_chat,
        Message,
        chats,
        current_agent_id
    } from '$lib/stores/app_store';
    import EditChatTitle from '$lib/components/edit_chat.svelte'
    import DeleteChat from '$lib/components/delete_chat.svelte'
    import { onMount } from "svelte";
    import { createChat, getChatById, updateChatTitle, deleteChat, getAllChats } from '$lib/api/chats';

    async function start_chat(): Promise<void> {
        try {
            let new_chat = await createChat("New Chat", $current_agent_id);
            current_chat.set(new_chat);
            current_chat.update(chat => {
                const newMessage = new Message(-1, "system", new_chat.agent.instructions, "Today");
                chat.messages.push(newMessage);
                return chat;
            });
            handleNewChat();
            await goto('/chat');
        } catch (error) {
            console.error('Failed to create chat:', error);
        }
    }

    export function handleNewChat() {
        getAllChats()
            .then(data => {
                chats.update(chatz => {
                    chatz.chats = data;
                    return chatz;
                });
            })
            .catch(error => {
                console.error('Failed to fetch chats:', error);
            });
    }

    async function setCurrentChat(chat: Chat): Promise<void> {
        try {
            const updatedChat = await getChatById(chat.id);
            current_chat.set(updatedChat);
            await goto('/chat');
        } catch (error) {
            console.error('Failed to fetch chat:', error);
        }
    }

    let editingChat = false;
    let editChat: Chat;

    function editCurrentChat(chat: Chat) {
        editingChat = true;
        editChat = chat;
    }

    interface SaveEventDetail {
        id?: number;
        title?: string;
    }

    async function handleSave(e: CustomEvent<SaveEventDetail>) {
        let id = e.detail.id;
        let title = e.detail.title;
        try {
            await updateChatTitle(id?? -1, title ?? "");
            await goto('/chat');
            handleNewChat();
        } catch (error) {
            console.error('Failed to update chat title:', error);
        }
        editingChat = false;
    }

    let deletingChat = false;
    let chatId = -1;

    async function delete_chat(id: number): Promise<void> {
        chatId = id;
        deletingChat = true;
    }

    interface ChatId {
        id: number;
    }

    async function handleDeleteChat(e: CustomEvent<ChatId>): Promise<void> {
        try {
            await deleteChat(e.detail.id);
            deletingChat = false;
            handleNewChat();
        } catch (error) {
            console.error('Failed to delete chat:', error);
        }
    }

    async function handleCancelDeleteChat(): Promise<void> {
        deletingChat = false;
    }

    function handleClose() {
        editingChat = false;
    }


    async function _goto(url: string): Promise<void> {
        await goto(url);
    }
    onMount(() => {
        getAllChats()
            .then(data => {
                chats.update(chatz => {
                    chatz.chats = data;
                    return chatz;
                });
            })
            .catch(error => {
                console.error('Failed to fetch chats:', error);
            });
    });


    $: sortedChats = $chats.chats.sort((a, b) => {
        const dateA = new Date(a.timestamp);
        const dateB = new Date(b.timestamp);
        return dateB.getTime() - dateA.getTime();
    });
</script>

<aside class="flex overflow-y-auto">
    <div class="flex h-[100svh] border-r border-slate-700 w-100 flex-col overflow-y-auto bg-[#0d1117] pt-8 sm:h-[100vh]">
        <div class="flex items-center px-4 pb-6">
            <!-- Logo -->
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="currentColor" stroke-width="1" viewBox="0 0 24 24">
                <path d="M20.553 3.105l-6 3C11.225 7.77 9.274 9.953 8.755 12.6c-.738 3.751 1.992 7.958 2.861 8.321A.985.985 0 0012 21c6.682 0 11-3.532 11-9 0-6.691-.9-8.318-1.293-8.707a1 1 0 00-1.154-.188zm-7.6 15.86a8.594 8.594 0 015.44-8.046 1 1 0 10-.788-1.838 10.363 10.363 0 00-6.393 7.667 6.59 6.59 0 01-.494-3.777c.4-2 1.989-3.706 4.728-5.076l5.03-2.515A29.2 29.2 0 0121 12c0 4.063-3.06 6.67-8.046 6.965zM3.523 5.38A29.2 29.2 0 003 12a6.386 6.386 0 004.366 6.212 1 1 0 11-.732 1.861A8.377 8.377 0 011 12c0-6.691.9-8.318 1.293-8.707a1 1 0 011.154-.188l6 3A1 1 0 018.553 7.9z"></path>
            </svg>
            <h2 class="ml-4 text-xl font-semibold text-slate-200">OpenAgent-WebUI</h2>
        </div>
        <!-- Previous chats container -->
        <div class="flex-grow space-y-2 overflow-y-auto border-b border-slate-700 px-2 py-4">
            {#each sortedChats as chat}
                <div class="flex items-center space-x-2">
                    <button class="flex-grow rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={() => setCurrentChat(chat)}>
                        <h3 class="truncate">{chat.title}</h3>
                        <p class="mt-1 text-xs text-slate-400">{chat.timestamp}</p>
                    </button>
                    <button class="rounded-lg p-2 text-slate-400 transition-colors duration-200 hover:bg-red-700 hover:text-white focus:outline-none" on:click={() => delete_chat(chat.id)}>
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd" />
                        </svg>
                    </button>
                    <button class="rounded-lg px-3 py-1 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-green-700 focus:outline-none" on:click={() => editCurrentChat(chat)}>
                        Edit
                    </button>
                </div>
            {/each}
        </div>
        {#if editingChat}
            <EditChatTitle chat={editChat} on:save={handleSave} on:close={handleClose}/>
        {/if}
        {#if deletingChat}
            <DeleteChat chatId={chatId} on:delete_chat={handleDeleteChat} on:close={handleCancelDeleteChat}/>
        {/if}
        <div class="mt-auto space-y-2 px-2 py-4">
            <button class="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={() => _goto('/')}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M11.47 3.841a.75.75 0 0 1 1.06 0l8.69 8.69a.75.75 0 1 0 1.06-1.061l-8.689-8.69a2.25 2.25 0 0 0-3.182 0l-8.69 8.69a.75.75 0 1 0 1.061 1.06l8.69-8.689Z" />
                    <path d="m12 5.432 8.159 8.159c.03.03.06.058.091.086v6.198c0 1.035-.84 1.875-1.875 1.875H15a.75.75 0 0 1-.75-.75v-4.5a.75.75 0 0 0-.75-.75h-3a.75.75 0 0 0-.75.75V21a.75.75 0 0 1-.75.75H5.625a1.875 1.875 0 0 1-1.875-1.875v-6.198a2.29 2.29 0 0 0 .091-.086L12 5.432Z" />
                </svg>
                <span>Home</span>
            </button>
            <button class="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={start_chat}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                </svg>
                <span>New Chat</span>
            </button>
            <button class="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={() => _goto('/agent-selection')}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                </svg>
                <span>All Agents</span>
            </button>
            <button class="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={() => _goto('/agent-creation')}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                <span>Agent Creation</span>
            </button>
            <button class="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={() => _goto('/file-management')}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
                </svg>
                <span>File Management</span>
            </button>
        </div>
    </div>
</aside>

<style lang="scss">
  /* Custom scrollbar styles */
  ::-webkit-scrollbar {
    width: 10px;
  }

  ::-webkit-scrollbar-track {
    background-color: transparent;
  }

  ::-webkit-scrollbar-thumb {
    background-color: rgba(128, 127, 127, 0.3);
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background-color: rgba(96, 96, 96, 0.5);
  }

  /* Dark mode scrollbar styles */
  .dark ::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.3);
  }

  .dark ::-webkit-scrollbar-thumb:hover {
    background-color: rgba(255, 255, 255, 0.5);
  }
</style>