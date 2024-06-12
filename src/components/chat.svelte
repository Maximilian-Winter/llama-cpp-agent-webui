<script lang="ts">
    import {
        current_chat,
        max_tokens,
        Message,
        Chat,
        min_p, rep_pen, rep_pen_range,
        temperature,
        text, tfsz,
        top_k,
        top_p,
        typ_p,
        chats
    } from "../stores/app_store.js";
    import { createEventDispatcher } from 'svelte';
    import EditMessage from "./edit_message.svelte";
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
        console.log($max_tokens, $temperature, $top_p, $top_k, $min_p, $typ_p, $tfsz, $rep_pen, $rep_pen_range)
        const payload = {
            chat_id: $current_chat.id,
            agent_id: $current_chat.agent.id,
            messages: $current_chat.messages,
            settings: {
                "max_tokens": $max_tokens,
                "temperature": $temperature,
                "top_p": $top_p,
                "top_k": $top_k,
                "min_p": $min_p,
                "typ_p": $typ_p,
                "tfsz": $tfsz,
                "rep_pen": $rep_pen,
                "rep_pen_range": $rep_pen_range,
            }
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

    function subscribeToUpdates(message_id: number, chat_id: number, message_ids: [number]) {
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
                    content: $current_chat.messages[message_id].content
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
                        chat.messages[message_id].id = res.id;
                        chat.messages[message_id].timestamp = res.timestamp;
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
            }
            current_chat.update(chat => {
                chat.messages[message_id].content += event.data;
                return chat;
            });
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
</script>

<!-- Prompt Messages Container - Modify the height according to your need -->
<div class="flex h-[97vh] w-full flex-col">
    <div class="flex-1 overflow-y-auto bg-[#0d1117] text-sm leading-6 text-slate-300 shadow-md sm:text-base sm:leading-7">
        <div class="sticky top-0 z-10 w-full border-b border-slate-700 bg-[#161b22] p-4 text-lg font-bold text-slate-200">
            <h2>{$current_chat.agent.name}</h2>
        </div>
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
                                    <span class="font-bold text-slate-200">AI</span>
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
                                </div>
                            </div>
                            <div class="message text-slate-200">{message.content.trim()}</div>
                        </div>
                    </div>
                {/if}
            {/each}
        {/if}
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