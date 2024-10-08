<script lang="ts">
    import {
        current_chat,
        Message,
        sidebarVisible,
        text,
        chats
    } from '$lib/stores/app_store.js';
    import { createEventDispatcher } from 'svelte';
    import EditMessage from './edit_message.svelte';
    import CodeBlock from './code_block.svelte';
    import ConfirmationModal from "./ConfirmationModal.svelte";
    import { Send, Plus, Copy, Edit, Trash2, RotateCcw, Settings } from 'lucide-svelte';

    const dispatch = createEventDispatcher();

    let editingMessage = false;
    let messageToEdit = { id: -1, content: '' };
    let deleteModalEnabled = false;
    let currentDeleteModalMessageId = -1;

    async function handleKeydown(event: KeyboardEvent): Promise<void> {
        if (event.key === 'Enter' && !event.shiftKey) {
            await send_message();
            event.preventDefault();
        }
    }

    async function send_message() {
        if ($text === "") {
            return;
        }
        current_chat.update(chat => {
            const newMessage = new Message(-1, "user", $text, new Date().toISOString());
            chat.messages.push(newMessage);
            return chat;
        });

        text.set('');
        await getResponse();
    }

    async function getResponse(): Promise<void> {
        const payload = {
            chat_id: $current_chat.id,
            agent_id: $current_chat.agent.id,
            messages: $current_chat.messages,
            settings: $current_chat.settings.toJSON()
        };

        const response = await fetch('http://localhost:8042/llama/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        current_chat.update(chat => {
            const newMessage = new Message(-1, "assistant", "", new Date().toISOString());
            chat.messages.push(newMessage);
            return chat;
        });

        if (response.ok) {
            let data = await response.json();
            if ($current_chat.id === -1) {
                dispatch('newChat', data.chat_id);
            }
            subscribeToUpdates($current_chat.messages.length - 1, data.chat_id, data.messages);
        } else {
            console.error('Failed to start session');
        }
    }

    function subscribeToUpdates(last_message_index: number, chat_id: number, message_ids: number[]) {
        current_chat.update(chat => {
            chat.id = chat_id;
            let count = 0;
            for (const message_id of message_ids) {
                chat.messages[count].id = message_id;
                count++;
            }
            return chat;
        });

        const source = new EventSource(`http://localhost:8042/llama/stream`);

        source.onmessage = async function (event) {
            if (event.data === "GENERATION_STOPPED") {
                source.close();
                const payload = {
                    chat_id: $current_chat.id,
                    role: "assistant",
                    content: $current_chat.messages[last_message_index].content
                };
                let response = await fetch('http://localhost:8042/messages/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });
                let res = await response.json();
                current_chat.update(chat => {
                    chat.messages[last_message_index].id = res.id;
                    chat.messages[last_message_index].timestamp = res.timestamp;
                    return chat;
                });

                // Update chats store
                chats.update(chatz => {
                    const index = chatz.chats.findIndex(c => c.id === $current_chat.id);
                    if (index !== -1) {
                        chatz.chats[index] = $current_chat;
                    } else {
                        chatz.chats.push($current_chat);
                    }
                    return chatz;
                });
            } else {
                current_chat.update(chat => {
                    chat.messages[last_message_index].content += event.data;
                    return chat;
                });
            }
        };

        source.onerror = function () {
            console.error('EventSource failed');
            source.close();
        };
    }

    function edit_message(id: number, content: string): void {
        messageToEdit = { id, content };
        editingMessage = true;
    }

    async function handleEditMessage(e: CustomEvent<{id: number; content: string}>): Promise<void> {
        const payload = {
            id: e.detail.id,
            content: e.detail.content,
        };
        const response = await fetch('http://localhost:8042/messages/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        editingMessage = false;
        if(response.ok) {
            let responseMsgs = await fetch('http://localhost:8042/chats/'+ $current_chat.id + '/messages', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            let res = await responseMsgs.json();
            current_chat.update(chat => {
                chat.messages = res;
                return chat;
            });
        }
    }

    function handleCancelEditingMessage(): void {
        editingMessage = false;
    }

    async function copyToClipboard(text: string): Promise<void> {
        try {
            await navigator.clipboard.writeText(text);
        } catch (err) {
            console.error('Failed to copy text to clipboard:', err);
        }
    }

    async function deleteMessage(messageId: number) {
        const response = await fetch(`http://localhost:8042/messages/${messageId}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            const response = await fetch('http://localhost:8042/chats/' + $current_chat.id, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            let chat = await response.json();
            current_chat.update(chatz => {
                chatz.messages = chat.messages;
                return chatz;
            });
        } else {
            console.error('Failed to delete message');
        }
    }

    function isLastMessage(index: number) {
        return index === $current_chat.messages.length - 1;
    }

    async function regenerateMessage(messageId: number): Promise<void> {
        await deleteMessage(messageId);
        await getResponse();
    }

    async function resendUserMessage(): Promise<void> {
        await getResponse();
    }

    function toggleSidebar() {
        sidebarVisible.update((v) => !v);
    }

    function showDeleteModal(messageId: number) {
        deleteModalEnabled = true;
        currentDeleteModalMessageId = messageId;
    }

    function hideDeleteModal() {
        deleteModalEnabled = false;
        currentDeleteModalMessageId = -1;
    }

    function onDeleteModalConfirm() {
        deleteMessage(currentDeleteModalMessageId);
        hideDeleteModal();
    }
</script>

<div class="flex flex-col h-[calc(100vh-4rem)] bg-[#0d1117]">
    <div class="sticky top-0 z-10 w-full border-b border-slate-700 bg-[#161b22] p-4 flex justify-between items-center">
        <h2 class="text-lg font-bold text-slate-200">{$current_chat.title}</h2>
        <button class="flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={toggleSidebar}>
            <Settings size={20} />
            <span>Settings</span>
        </button>
    </div>

    <div class="flex-1 overflow-y-auto">
        <div class="max-w-4xl mx-auto px-4 py-8">
            {#each $current_chat.messages as message, index}
                {#if message.role === "system"}
                    <div>
                        {#if $current_chat.settings.show_agent_instructions === true}
                            <div class="mb-6 bg-[#1c2128] rounded-lg p-4">
                                <div class="flex items-center justify-between mb-2">
                                    <div class="flex items-center">
                                        <span class="font-bold text-slate-200">Agent Instructions (System Message)</span>
                                        <span class="text-xs text-slate-400 ml-2">{message.timestamp}</span>
                                    </div>
                                </div>
                                <p class="whitespace-pre-wrap">{message.content.trim()}</p>
                            </div>
                        {/if}
                    </div>
                {:else}
                    <div class="mb-6 {message.role === 'assistant' ? 'bg-[#1c2128] rounded-lg p-4' : ''}">
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center">
                                <img class="w-8 h-8 rounded-full mr-2" src={message.role === 'user' ? 'https://dummyimage.com/256x256/354ea1/ffffff&text=U' : 'https://dummyimage.com/256x256/354ea1/ffffff&text=AI'} alt={message.role === 'user' ? 'User' : 'AI'} />
                                <span class="font-bold text-slate-200">{message.role === 'user' ? 'You' : $current_chat.agent.name}</span>
                                <span class="text-xs text-slate-400 ml-2">{message.timestamp}</span>
                            </div>
                            <div class="flex space-x-2">
                                <button class="text-slate-400 hover:text-blue-500" on:click={() => copyToClipboard(message.content)}><Copy size={16} /></button>
                                <button class="text-slate-400 hover:text-blue-500" on:click={() => edit_message(message.id, message.content)}><Edit size={16} /></button>
                                {#if isLastMessage(index)}
                                    {#if message.role === 'user'}
                                        <button class="text-slate-400 hover:text-green-500" on:click={resendUserMessage}><RotateCcw size={16} /></button>
                                    {:else}
                                        <button class="text-slate-400 hover:text-green-500" on:click={() => regenerateMessage(message.id)}><RotateCcw size={16} /></button>
                                    {/if}
                                    <button class="text-slate-400 hover:text-red-500" on:click={() => showDeleteModal(message.id)}><Trash2 size={16} /></button>
                                {/if}
                            </div>
                        </div>
                        <div class="text-slate-200 {message.role === 'assistant' ? 'pl-10' : ''}">
                            {#if message.role === 'assistant'}
                                <CodeBlock content={message.content.trim()} />
                            {:else}
                                <p class="whitespace-pre-wrap">{message.content.trim()}</p>
                            {/if}
                        </div>
                    </div>
                {/if}
            {/each}
        </div>
    </div>

    {#if editingMessage}
        <EditMessage id={messageToEdit.id} message={messageToEdit.content} on:save={handleEditMessage} on:cancel={handleCancelEditingMessage}/>
    {/if}

    {#if deleteModalEnabled}
        <ConfirmationModal
                title="Delete message?"
                on:confirm={onDeleteModalConfirm}
                on:cancel={hideDeleteModal}
        />
    {/if}

    <div class="border-t border-slate-700 bg-[#0d1117] p-4">
        <div class="max-w-4xl mx-auto">
            <form class="flex items-center gap-4" on:submit|preventDefault={send_message}>
                <button type="button" class="text-slate-400 hover:text-blue-500" title="Add attachment">
                    <Plus size={24} />
                </button>
                <textarea
                        rows="1"
                        class="flex-grow resize-none rounded-md border border-slate-700 bg-[#1c2128] p-2 text-base text-slate-200 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        placeholder="Type your message..."
                        bind:value={$text}
                        on:keydown={handleKeydown}
                ></textarea>
                <button type="submit" class="text-slate-400 hover:text-blue-500" title="Send message">
                    <Send size={24} />
                </button>
            </form>
        </div>
    </div>
</div>

<style>
    textarea {
        min-height: 24px;
        max-height: 200px;
        overflow-y: auto;
    }
</style>