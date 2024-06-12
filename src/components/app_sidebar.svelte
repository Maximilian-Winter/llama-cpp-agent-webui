<script lang="ts">
    import {
        Chat,
        app_mode,
        current_chat,
        sidebarVisible,
        Message,
        chats,
        current_agent_name, current_agent_description, current_agent_instructions, current_agent_id
    } from "../stores/app_store";
    import EditChatTitle from './edit_chat.svelte'
    import DeleteChat from './delete_chat.svelte'
    import {onMount} from "svelte";
    function enableAgentCreationMode() {
        app_mode.set("agent_creation");
    }

    function enableAgentSelectionMode() {
        app_mode.set("agent_selection");
    }
    async function start_chat(): Promise<void> {

        const payload = {
            title: "New Chat",
            agent_id: $current_agent_id
        };
        const response = await fetch('http://localhost:8042/chats/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        if (response.ok) {
            let new_chat = await response.json()
            current_chat.set(new Chat(new_chat.id, new_chat.title, new_chat.agent, new_chat.instructions));
            current_chat.update(chat => {
                const newMessage = new Message(-1, "system", new_chat.agent.instructions);
                chat.messages.push(newMessage);
                return chat;
            });
            handleNewChat();
            app_mode.set("chat");
        }

    }
    function enableChatMode() {
        if($current_chat.messages.length != 0 || $current_agent_id != $current_chat.agent.id)
        {
            start_chat();
        }
    }
    function toggleSidebar() {
        sidebarVisible.update((v) => !v);
    }

    export function handleNewChat() {
        fetchChats()
            .then(data => {
            chats.update(chatz => {
                chatz.chats = data;
                return chatz;
                });
            })
            .catch(error => {
                console.error('Failed to fetch panels:', error);
            });
    }

    async function setCurrentChat(chat: Chat): Promise<void> {
        const response = await fetch('http://localhost:8042/chats/' + chat.id, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        chat = await response.json();
        current_chat.set(chat);
        app_mode.set("chat");
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
        const payload = {};
        const response = await fetch('http://localhost:8042/chats/' + id + '/' + title, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (response.ok) {
            app_mode.update(() => 'chat')
        }

        fetchChats()
            .then(data => {
                chats.update(chatz => {
                    chatz.chats = data;
                    return chatz;
                });
            })
            .catch(error => {
                console.error('Failed to fetch panels:', error);
            });
        editingChat = false;
    }

    function handleClose() {
        editingChat = false;
    }
    let deletingChat = false;
    let chatId = -1;

    async function delete_chat(id: number): Promise<void> {
        chatId = id;
        deletingChat = true;
    }

    interface ChatId
    {
        id: number;
    }
    async function handleDeleteChat(e: CustomEvent<ChatId>): Promise<void> {
        const response = await fetch('http://localhost:8042/chats/' + e.detail.id, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        deletingChat = false;
        fetchChats()
            .then(data => {
                chats.update(chatz => {
                    chatz.chats = data;
                    return chatz;
                });
            })
            .catch(error => {
                console.error('Failed to fetch panels:', error);
            });
    }

    async function handleCancelDeleteChat(): Promise<void> {
        deletingChat = false;
    }
    async function fetchChats(): Promise<Chat[]> {
        const response = await fetch('http://localhost:8042/chats/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    onMount(() => {
        fetchChats()
            .then(data => {
                chats.update(chatz => {
                    chatz.chats = data;
                    return chatz;
                });
            })
            .catch(error => {
                console.error('Failed to fetch panels:', error);
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
            <h2 class="ml-4 text-xl font-semibold text-slate-200">llama-cpp-agent WebUI</h2>
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
            <button class="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={enableChatMode}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                </svg>
                <span>Chat</span>
            </button>
            <button class="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={enableAgentSelectionMode}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                </svg>
                <span>All Agents</span>
            </button>
            <button class="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={enableAgentCreationMode}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                <span>Agent Creation</span>
            </button>
            <button class="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={toggleSidebar}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                </svg>
                <span>Settings</span>
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