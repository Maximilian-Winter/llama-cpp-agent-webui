<script lang="ts">
    import {
        chats,
        current_chat,
        Message, sidebarVisible,
        text
    } from '$lib/stores/app_store.js';
    import { createEventDispatcher } from 'svelte';
    import EditMessage from '$lib/components/edit_message.svelte';
    import CodeBlock from '$lib/components/code_block.svelte';

    const dispatch = createEventDispatcher();
    async function handleKeydown(event: KeyboardEvent): Promise<void> {
        if (event.key === 'Enter' && !event.shiftKey ) {
            await send_message()
            event.preventDefault(); // Prevent the default action if it's the Enter key
        }
    }

    async function send_message() {
        if ($text === "")
        {
            return
        }
        current_chat.update(chat => {
            const newMessage = new Message(-1, "user", $text, "Today");
            chat.messages.push(newMessage);
            return chat;
        });

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
            const newMessage = new Message(-1, "assistant", "", "Today");
            chat.messages.push(newMessage);
            return chat;
        });

        text.update(() => '');
        if (response.ok) {
            if( $current_chat.id == -1)
            {
                dispatch('newChat');
            }
            let data = await response.json()
            subscribeToUpdates($current_chat.messages.length - 1, data.chat_id, data.messages);
        } else {
            console.error('Failed to start session');
        }
    }
    function subscribeToUpdates(last_message_index: number, chat_id: number, message_ids: [number]) {
        current_chat.update(chat => {
            if (chat_id === -1) {
                chat.id = chat_id
                chats.update(chatz => {chatz.chats.push(chat)
                    return chatz});
            }
            else {
                chat.id = chat_id
            }
            let count = 0;
            for (const message_id of message_ids) {
                chat.messages[count].id = message_id;
                count++
            }
            return chat;
        });

        const source = new EventSource(`http://localhost:8042/llama/stream`);


        source.onmessage = async function (event) {
            // Process the event data
            if (event.data === "GENERATION_STOPPED") {
                source.close()
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
                await response.json().then((res) => {
                    current_chat.update(chat => {
                        chat.messages[last_message_index].id = res.id;
                        chat.messages[last_message_index].timestamp = res.timestamp;
                        return chat;
                    });
                })

                let responseMsgs = await fetch('http://localhost:8042/chats/'+ $current_chat.id + '/messages', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                await responseMsgs.json().then((res) => {
                    current_chat.update(chat => {
                        chat.messages = res;
                        return chat;
                    });
                })
                return
            }else {
                current_chat.update(chat => {
                    chat.messages[last_message_index].content += event.data;
                    return chat;
                });

                // Force a re-render of the CodeBlock component
                current_chat.update(chat => chat);
            }
        };

        source.onerror = function () {
            console.error('EventSource failed');
            source.close();
        };

        // Optionally listen for a custom event to close the source
        source.addEventListener('session-complete', () => {
            console.log('Session complete');
            source.close();

        });
    }

    let editingMessage = false;
    let message = -1;
    let message_content = '';
    async function edit_message(id: number, content: string): Promise<void> {
        message = id;
        message_content = content;
        editingMessage = true;
    }

    interface MessageId
    {
        id: number;
        content: string;
    }
    async function handleEditMessage(e: CustomEvent<MessageId>): Promise<void> {

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
        if(response.ok)
        {
            let responseMsgs = await fetch('http://localhost:8042/chats/'+ $current_chat.id + '/messages', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            await responseMsgs.json().then((res) => {
                current_chat.update(chat => {
                    chat.messages = res;
                    return chat;
                });
            })
        }
    }

    async function handleCancelEditingMessage(): Promise<void> {
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
        console.log('Attempting to delete message:', messageId);
        const response = await fetch(`http://localhost:8042/messages/${messageId}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            console.log('Message deleted successfully');
            const response = await fetch('http://localhost:8042/chats/' + $current_chat.id, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            let chat = await response.json();
            current_chat.update(chatz => {
                chatz.messages = chat.messages
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
        await deleteMessage(messageId)
        await getResponse();
    }

    async function resendUserMessage(): Promise<void> {
        await getResponse();
    }
    function toggleSidebar() {
        sidebarVisible.update((v) => !v);
    }

</script>

<!-- Prompt Messages Container - Modify the height according to your need -->
<div class="flex h-[97vh] w-full flex-col">
    <div class="flex-1 overflow-y-auto bg-[#0d1117] text-sm leading-6 text-slate-300 shadow-md sm:text-base sm:leading-7">
        <div class="sticky top-0 z-10 w-full border-b border-slate-700 bg-[#161b22] p-4 flex justify-between items-center">
            <h2 class="text-lg font-bold text-slate-200">{$current_chat.agent.name}</h2>
            <button class="flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition-colors duration-200 hover:bg-slate-800 focus:outline-none" on:click={toggleSidebar}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                </svg>
                <span>Settings</span>
            </button>
        </div>

        {#key $current_chat}
            {#if $current_chat}
            {#each $current_chat.messages as message, index}
                {#if message.role === "user"}
                    <div class="flex gap-4 px-4 py-6 sm:px-6">
                        <img class="h-10 w-10 flex-shrink-0 rounded-full" src="https://dummyimage.com/256x256/354ea1/ffffff&text=U" alt="User" />
                        <div class="flex w-full flex-col gap-2">
                            <div class="flex justify-between">
                                <div class="flex items-center gap-2">
                                    <span class="font-bold text-slate-200">User</span>
                                    <span class="text-xs text-slate-400">{message.timestamp}</span>
                                </div>
                                <div class="flex gap-2">
                                    <button class="text-slate-400 hover:text-blue-500" title="Copy" on:click={() => copyToClipboard(message.content)}>
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                        </svg>
                                    </button>
                                    <button class="text-slate-400 hover:text-blue-500" title="Edit" on:click={() => edit_message(message.id, message.content)}>
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                        </svg>
                                    </button>
                                    {#if isLastMessage(index)}
                                        <button class="text-slate-400 hover:text-green-500" title="Resend" on:click={() => resendUserMessage()}>
                                            <svg class="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                                                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 9H8a5 5 0 0 0 0 10h9m4-10-4-4m4 4-4 4"/>
                                            </svg>
                                        </button>
                                        <button class="text-slate-400 hover:text-red-500" title="Delete" on:click={() => deleteMessage(message.id)}>
                                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd" />
                                            </svg>
                                        </button>
                                    {/if}
                                </div>
                            </div>
                            <div class="message text-slate-200">{message.content.trim()}</div>
                        </div>
                    </div>
                {:else if message.role === "system"}
                    <div></div>
                {:else}
                    <div class="flex gap-4 bg-[#1c2128] px-4 py-6 sm:px-6">
                        <img class="h-10 w-10 flex-shrink-0 rounded-full" src="https://dummyimage.com/256x256/354ea1/ffffff&text=AI" alt="AI" />
                        <div class="flex w-full flex-col gap-2">
                            <div class="flex justify-between">
                                <div class="flex items-center gap-2">
                                    <span class="font-bold text-slate-200">{$current_chat.agent.name}</span>
                                    <span class="text-xs text-slate-400">{message.timestamp}</span>
                                </div>
                                <div class="flex gap-2">
                                    <button class="text-slate-400 hover:text-blue-500" title="Copy" on:click={() => copyToClipboard(message.content)}>
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                        </svg>
                                    </button>
                                    <button class="text-slate-400 hover:text-blue-500" title="Edit" on:click={() => edit_message(message.id, message.content)}>
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                        </svg>
                                    </button>
                                    {#if isLastMessage(index)}
                                        <button class="text-slate-400 hover:text-green-500" title="Regenerate" on:click={() => regenerateMessage(message.id)}>
                                            <svg class="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                                                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.651 7.65a7.131 7.131 0 0 0-12.68 3.15M18.001 4v4h-4m-7.652 8.35a7.13 7.13 0 0 0 12.68-3.15M6 20v-4h4"/>
                                            </svg>
                                        </button>
                                        <button class="text-slate-400 hover:text-red-500" title="Delete" on:click={() => deleteMessage(message.id)}>
                                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd" />
                                            </svg>
                                        </button>
                                    {/if}
                                </div>
                            </div>
                            <div class="message text-slate-200">
                                <CodeBlock content={message.content.trim()} />
                            </div>
                        </div>
                    </div>
                {/if}
            {/each}
        {/if}
        {/key}
    </div>
    {#if editingMessage}
        <EditMessage id={message} message={message_content} on:save={handleEditMessage} on:cancel={handleCancelEditingMessage}/>
    {/if}
    <form class="flex items-center gap-4 border-t border-slate-700 bg-[#0d1117] p-4">
        <button class="text-slate-400 hover:text-blue-500" type="button" title="Add">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
        </button>
        <textarea id="chat-input" rows="3" class="prompt-input w-full flex-grow resize-none rounded-md border border-slate-700 bg-[#1c2128] p-2 text-base text-slate-200 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="Enter your prompt" bind:value={$text} on:keydown={handleKeydown}></textarea>
        <button class="text-slate-400 hover:text-blue-500" on:click={send_message} title="Send">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
        </button>
    </form>
</div>


<style>
    .message {
        white-space: pre-wrap; /* Preserves whitespace and wraps text */
    }

    .prompt-input {
        resize: none;
    }
</style>