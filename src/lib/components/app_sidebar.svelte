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
    import {Home, MessageSquare, Users, UserPlus, Folder, Settings, Trash2} from 'lucide-svelte';

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

    async function handleSave(e: CustomEvent<{id?: number; title?: string}>) {
        let id = e.detail.id;
        let title = e.detail.title;
        try {
            await updateChatTitle(id ?? -1, title ?? "");
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

    async function handleDeleteChat(e: CustomEvent<{id: number}>): Promise<void> {
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

<aside class="flex h-screen w-64 flex-col bg-[#161b22] text-slate-300 border-r border-slate-700">
    <div class="flex items-center p-4 border-b border-slate-700">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20.553 3.105l-6 3C11.225 7.77 9.274 9.953 8.755 12.6c-.738 3.751 1.992 7.958 2.861 8.321A.985.985 0 0012 21c6.682 0 11-3.532 11-9 0-6.691-.9-8.318-1.293-8.707a1 1 0 00-1.154-.188zm-7.6 15.86a8.594 8.594 0 015.44-8.046 1 1 0 10-.788-1.838 10.363 10.363 0 00-6.393 7.667 6.59 6.59 0 01-.494-3.777c.4-2 1.989-3.706 4.728-5.076l5.03-2.515A29.2 29.2 0 0121 12c0 4.063-3.06 6.67-8.046 6.965zM3.523 5.38A29.2 29.2 0 003 12a6.386 6.386 0 004.366 6.212 1 1 0 11-.732 1.861A8.377 8.377 0 011 12c0-6.691.9-8.318 1.293-8.707a1 1 0 011.154-.188l6 3A1 1 0 018.553 7.9z"></path>
        </svg>
        <h2 class="ml-2 text-xl font-semibold text-slate-200">OpenAgent WebUI</h2>
    </div>

    <nav class="flex-1 overflow-y-auto py-4">
        <ul class="space-y-2 px-3">
            <li>
                <button class="flex w-full items-center rounded-lg px-3 py-2 text-slate-300 transition-colors duration-200 hover:bg-slate-700 hover:text-white" on:click={() => _goto('/')}>
                    <Home size={18} class="mr-3" />
                    <span>Home</span>
                </button>
            </li>
            <li>
                <button class="flex w-full items-center rounded-lg px-3 py-2 text-slate-300 transition-colors duration-200 hover:bg-slate-700 hover:text-white" on:click={start_chat}>
                    <MessageSquare size={18} class="mr-3" />
                    <span>New Chat</span>
                </button>
            </li>
            <li>
                <button class="flex w-full items-center rounded-lg px-3 py-2 text-slate-300 transition-colors duration-200 hover:bg-slate-700 hover:text-white" on:click={() => _goto('/agent-selection')}>
                    <Users size={18} class="mr-3" />
                    <span>All Agents</span>
                </button>
            </li>
            <li>
                <button class="flex w-full items-center rounded-lg px-3 py-2 text-slate-300 transition-colors duration-200 hover:bg-slate-700 hover:text-white" on:click={() => _goto('/agent-creation')}>
                    <UserPlus size={18} class="mr-3" />
                    <span>Agent Creation</span>
                </button>
            </li>
            <li>
                <button class="flex w-full items-center rounded-lg px-3 py-2 text-slate-300 transition-colors duration-200 hover:bg-slate-700 hover:text-white" on:click={() => _goto('/file-management')}>
                    <Folder size={18} class="mr-3" />
                    <span>File Management</span>
                </button>
            </li>
            <li>
                <button class="flex w-full items-center rounded-lg px-3 py-2 text-slate-300 transition-colors duration-200 hover:bg-slate-700 hover:text-white" on:click={() => _goto('/bulk-delete')}>
                    <Trash2 size={18} class="mr-3" />
                    <span>Bulk Delete</span>
                </button>
            </li>
        </ul>
    </nav>

    <div class="flex-1 overflow-y-auto border-t border-slate-700 py-4">
        <h3 class="mb-2 px-4 text-sm font-semibold text-slate-400">Recent Chats</h3>
        <ul class="space-y-1 px-3">
            {#each sortedChats as chat}
                <li class="rounded-lg transition-colors duration-200 hover:bg-slate-700">
                    <div class="flex items-center justify-between p-2">
                        <button class="flex-grow text-left text-sm text-slate-300 hover:text-white" on:click={() => setCurrentChat(chat)}>
                            <span class="block truncate">{chat.title}</span>
                            <span class="text-xs text-slate-400">{chat.timestamp}</span>
                        </button>
                        <div class="flex space-x-1">
                            <button class="p-1 text-slate-400 hover:text-white" on:click={() => editCurrentChat(chat)} title="Edit">
                                <Settings size={14} />
                            </button>
                            <button class="p-1 text-slate-400 hover:text-red-400" on:click={() => delete_chat(chat.id)} title="Delete">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </li>
            {/each}
        </ul>
    </div>

    {#if editingChat}
        <EditChatTitle chat={editChat} on:save={handleSave} on:close={handleClose}/>
    {/if}
    {#if deletingChat}
        <DeleteChat chatId={chatId} on:delete_chat={handleDeleteChat} on:close={handleCancelDeleteChat}/>
    {/if}
</aside>

<style lang="scss">
  /* Custom scrollbar styles */
  ::-webkit-scrollbar {
    width: 8px;
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