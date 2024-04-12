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
            const newMessage = new Message(-1, "user", $text);
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
        const response = await fetch('http://localhost:8000/llama/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        current_chat.update(chat => {
            const newMessage = new Message(-1, "assistant", "");
            chat.messages.push(newMessage);
            return chat;
        });

        text.update(() => '');
        if (response.ok) {
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

        const source = new EventSource(`http://localhost:8000/llama/stream`);


        source.onmessage = async function (event) {
            // Process the event data
            if (event.data === "GENERATION_STOPPED") {
                source.close()
                const payload = {
                    chat_id: $current_chat.id,
                    role: "assistant",
                    content: $current_chat.messages[message_id].content
                };
                let response = await fetch('http://localhost:8000/messages/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });
                await response.json().then((res) => {
                    current_chat.update(chat => {
                        chat.messages[message_id].id = res.id;
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
</script>

<!-- Prompt Messages Container - Modify the height according to your need -->
<div class="flex h-[97vh] w-full flex-col">
    <!-- Prompt Messages -->
    <div
            class="flex-1 overflow-y-auto bg-[#0d1117] text-sm leading-6 text-slate-900 shadow-md dark:bg-[#0d1117] dark:text-slate-300 sm:text-base sm:leading-7"
    >
        <div class="p-10 w-full h-fit font-bold text-stone-300 border-b-2 border-gray-400">
            <h2 class="text-2xl">{$current_chat.agent.name}</h2>
        </div>
        {#if $current_chat}
            {#each $current_chat.messages as message, index}
                {#if message.role === "user"}
                    <div class="flex px-4 py-8 sm:px-6">
                        <img
                                class="mr-2 flex h-8 w-8 rounded-full sm:mr-4"
                                src="https://dummyimage.com/256x256/354ea1/ffffff&text=U"
                                alt="User"
                        />

                        <div
                                class="flex w-full flex-col items-start lg:flex-row lg:justify-between"
                        >

                            <div class="flex max-w-3xl items-center message">
                                {message.content.trim()}
                            </div>

                            <div
                                    class="mt-4 flex flex-row justify-start gap-x-2 text-slate-500 lg:mt-0"
                            >
                                <button class="hover:text-blue-600" type="button">
                                    <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            class="h-5 w-5"
                                            viewBox="0 0 24 24"
                                            stroke-width="2"
                                            stroke="currentColor"
                                            fill="none"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                    >
                                        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                                        <path
                                                d="M8 8m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z"
                                        ></path>
                                        <path
                                                d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2"
                                        ></path>
                                    </svg>

                                </button>
                                <button class="hover:text-blue-600" type="button">
                                    <svg class="w-6 h-6" aria-hidden="true"
                                         xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
                                         viewBox="0 0 24 24">
                                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"
                                              stroke-width="2" fill="none"
                                              d="m14.304 4.844 2.852 2.852M7 7H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-4.5m2.409-9.91a2.017 2.017 0 0 1 0 2.853l-6.844 6.844L8 14l.713-3.565 6.844-6.844a2.015 2.015 0 0 1 2.852 0Z"/>
                                    </svg>

                                </button>

                            </div>
                        </div>
                    </div>

                {:else if message.role === "system"}
                    <div></div>
                {:else}
                    <div class="flex bg-slate-100 px-4 py-8 dark:bg-slate-900 sm:px-6">
                        <img
                                class="mr-2 flex h-8 w-8 rounded-full sm:mr-4"
                                src="https://dummyimage.com/256x256/354ea1/ffffff&text=AI"
                                alt="AI"
                        />

                        <div
                                class="flex w-full flex-col items-start lg:flex-row lg:justify-between"
                        >

                            <div class="flex max-w-3xl items-center message">
                                {message.content.trim()}
                            </div>

                            <div
                                    class="mt-4 flex flex-row justify-start gap-x-2 text-slate-500 lg:mt-0"
                            >
                                <button class="hover:text-blue-600" type="button">
                                    <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            class="h-5 w-5"
                                            viewBox="0 0 24 24"
                                            stroke-width="2"
                                            stroke="currentColor"
                                            fill="none"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                    >
                                        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                                        <path
                                                d="M8 8m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z"
                                        ></path>
                                        <path
                                                d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2"
                                        ></path>
                                    </svg>

                                </button>
                                <button class="hover:text-blue-600" type="button">
                                    <svg class="w-6 h-6" aria-hidden="true"
                                         xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
                                         viewBox="0 0 24 24">
                                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"
                                              stroke-width="2" fill="none"
                                              d="m14.304 4.844 2.852 2.852M7 7H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-4.5m2.409-9.91a2.017 2.017 0 0 1 0 2.853l-6.844 6.844L8 14l.713-3.565 6.844-6.844a2.015 2.015 0 0 1 2.852 0Z"/>
                                    </svg>

                                </button>

                            </div>
                        </div>
                    </div>
                {/if}
            {/each}
        {/if}
    </div>
    <!-- Prompt message input -->
    <form
            class="flex w-full items-center rounded-b-md border-t border-slate-300 bg-slate-200 p-8 pb-0 dark:border-[#30363d] dark:bg-[#05060a]"
    >
        <label for="chat-input" class="sr-only">Enter your prompt</label>
        <div>
            <button
                    class="hover:text-blue-600 dark:text-slate-200 dark:hover:text-blue-600 sm:p-2"
                    type="button"
            >
                <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-6 w-6"
                        aria-hidden="true"
                        viewBox="0 0 24 24"
                        stroke-width="2"
                        stroke="currentColor"
                        fill="none"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                    <path d="M12 5l0 14"></path>
                    <path d="M5 12l14 0"></path>
                </svg>
                <span class="sr-only">Add</span>
            </button>
        </div>
        <textarea
                id="chat-input"
                rows="3"
                class="prompt-input mx-6 p-2 flex min-h-full w-full rounded-md border border-slate-300 bg-slate-50 text-base text-slate-900 placeholder-slate-400 focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:border-[#30363d] dark:bg-[#171E28] dark:text-slate-50 dark:placeholder-slate-400 dark:focus:border-blue-600 dark:focus:ring-blue-600"
                placeholder="Enter your prompt"
                bind:value={$text}
                on:keydown={handleKeydown}
        ></textarea>
        <div>
            <button
                    class="inline-flex hover:text-blue-600 dark:text-slate-200 dark:hover:text-blue-600 sm:p-2"
                    on:click={send_message}
            >
                <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-6 w-6"
                        aria-hidden="true"
                        viewBox="0 0 24 24"
                        stroke-width="2"
                        stroke="currentColor"
                        fill="none"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                    <path d="M10 14l11 -11"></path>
                    <path
                            d="M21 3l-6.5 18a.55 .55 0 0 1 -1 0l-3.5 -7l-7 -3.5a.55 .55 0 0 1 0 -1l18 -6.5"
                    ></path>
                </svg>
                <span class="sr-only">Send message</span>
            </button>
        </div>
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