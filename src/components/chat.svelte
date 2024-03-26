<script lang="ts">
    class Message {
        constructor(public role: string, public content: string) {
        }
    }

    class Chat {
        messages: Message[] = [];
    }

    let current_chat: Chat = new Chat();

    let configuration_sidebar_visible = false;
    let text = "";

    let max_tokens = 2048;
    let temperature = 0.7;
    let top_p = 1;
    let top_k = 0;
    let min_p = 0;
    let typ_p = 1;
    let tfsz = 1;
    let rep_pen = 1.2;
    let rep_pen_range = 512;

    function createChat() {
        current_chat = new Chat();
    }

    async function send_message() {

        current_chat.messages = [...current_chat.messages, new Message("user", text)];
        const payload = {
            messages: current_chat.messages,
            settings: {
                max_tokens,
                temperature,
                top_p,
                top_k,
                min_p,
                typ_p,
                tfsz,
                rep_pen,
                rep_pen_range,
            }
        };
        const response = await fetch('http://localhost:8000/llama/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        current_chat.messages = [...current_chat.messages, new Message("assistant", "")];
        text = "";
        if (response.ok) {
            subscribeToUpdates(current_chat.messages.length - 1);
        } else {
            console.error('Failed to start session');
        }

    }

    function subscribeToUpdates(message_id: number) {
        const source = new EventSource(`http://localhost:8000/llama/stream`);

        source.onmessage = function(event) {
            // Process the event data
            current_chat.messages[message_id].content += event.data;
            // Update your Svelte state here
        };

        source.onerror = function() {
            console.error('EventSource failed');
            source.close();
        };

        // Optionally listen for a custom event to close the source
        source.addEventListener('session-complete', () => {
            console.log('Session complete');
            source.close();
        });
    }

    function toggleSidebar() {
        configuration_sidebar_visible = !configuration_sidebar_visible;
    }
</script>

<div class="flex flex-row bg-[#05060a]">
    <!-- Sidebar -->
    <aside class="flex">
        <div
                class="flex h-[100svh] w-60 flex-col overflow-y-auto bg-slate-50 pt-8 dark:border-slate-700 dark:bg-[#05060a] sm:h-[100vh] sm:w-64"
        >
            <div class="flex px-4">
                <!-- Logo -->
                <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-7 w-7 text-blue-600"
                        fill="currentColor"
                        stroke-width="1"
                        viewBox="0 0 24 24"
                >
                    <path
                            d="M20.553 3.105l-6 3C11.225 7.77 9.274 9.953 8.755 12.6c-.738 3.751 1.992 7.958 2.861 8.321A.985.985 0 0012 21c6.682 0 11-3.532 11-9 0-6.691-.9-8.318-1.293-8.707a1 1 0 00-1.154-.188zm-7.6 15.86a8.594 8.594 0 015.44-8.046 1 1 0 10-.788-1.838 10.363 10.363 0 00-6.393 7.667 6.59 6.59 0 01-.494-3.777c.4-2 1.989-3.706 4.728-5.076l5.03-2.515A29.2 29.2 0 0121 12c0 4.063-3.06 6.67-8.046 6.965zM3.523 5.38A29.2 29.2 0 003 12a6.386 6.386 0 004.366 6.212 1 1 0 11-.732 1.861A8.377 8.377 0 011 12c0-6.691.9-8.318 1.293-8.707a1 1 0 011.154-.188l6 3A1 1 0 018.553 7.9z"
                    ></path>
                </svg>
                <h2 class="px-5 text-lg font-medium text-slate-800 dark:text-slate-200">
                    llama-cpp-agent WebUI
                </h2>
            </div>
            <div class="mx-2 mt-8">
                <button
                        class="flex w-full gap-x-4 rounded-lg border border-slate-300 p-4 text-left text-sm font-medium text-slate-700 transition-colors duration-200 hover:bg-slate-200 focus:outline-none dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
                        on:click={createChat}
                >
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
                        <path d="M12 5l0 14"></path>
                        <path d="M5 12l14 0"></path>
                    </svg>
                    New Chat
                </button>
            </div>
            <!-- Previous chats container -->
            <div
                    class="h-1/2 space-y-4 overflow-y-auto border-b border-slate-300 px-2 py-4 dark:border-slate-700"
            >
                <button
                        class="flex w-full flex-col gap-y-2 rounded-lg px-3 py-2 text-left transition-colors duration-200 hover:bg-slate-200 focus:outline-none dark:hover:bg-slate-800"
                >
                    <h1
                            class="text-sm font-medium capitalize text-slate-700 dark:text-slate-200"
                    >
                        Tailwind Classes
                    </h1>
                    <p class="text-xs text-slate-500 dark:text-slate-400">12 Mar</p>
                </button>
                <button
                        class="flex w-full flex-col gap-y-2 rounded-lg px-3 py-2 text-left transition-colors duration-200 hover:bg-slate-200 focus:outline-none dark:hover:bg-slate-800"
                >
                    <h1
                            class="text-sm font-medium capitalize text-slate-700 dark:text-slate-200"
                    >
                        How to use Tailwind components?
                    </h1>
                    <p class="text-xs text-slate-500 dark:text-slate-400">1 Jan</p>
                </button>
            </div>
            <div class="mt-auto w-full space-y-4 px-2 py-4">
                <button
                        class="flex w-full gap-x-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-700 transition-colors duration-200 hover:bg-slate-200 focus:outline-none dark:text-slate-200 dark:hover:bg-slate-800"
                >
                    <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-6 w-6"
                            viewBox="0 0 24 24"
                            stroke-width="2"
                            stroke="currentColor"
                            fill="none"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                    >
                        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                        <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"></path>
                        <path d="M12 10m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"></path>
                        <path
                                d="M6.168 18.849a4 4 0 0 1 3.832 -2.849h4a4 4 0 0 1 3.834 2.855"
                        ></path>
                    </svg>
                    User
                </button>
                <button
                        class="flex w-full gap-x-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-700 transition-colors duration-200 hover:bg-slate-200 focus:outline-none dark:text-slate-200 dark:hover:bg-slate-800"
                        on:click={toggleSidebar}
                >
                    <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-6 w-6"
                            viewBox="0 0 24 24"
                            stroke-width="2"
                            stroke="currentColor"
                            fill="none"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                    >
                        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                        <path
                                d="M19.875 6.27a2.225 2.225 0 0 1 1.125 1.948v7.284c0 .809 -.443 1.555 -1.158 1.948l-6.75 4.27a2.269 2.269 0 0 1 -2.184 0l-6.75 -4.27a2.225 2.225 0 0 1 -1.158 -1.948v-7.285c0 -.809 .443 -1.554 1.158 -1.947l6.75 -3.98a2.33 2.33 0 0 1 2.25 0l6.75 3.98h-.033z"
                        ></path>
                        <path d="M12 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"></path>
                    </svg>
                    Settings
                </button>
            </div>
        </div>
    </aside>
    <!-- Prompt Messages Container - Modify the height according to your need -->
    <div class="flex h-[97vh] w-full flex-col">
        <!-- Prompt Messages -->
        <div
                class="flex-1 overflow-y-auto bg-[#05060a] text-sm leading-6 text-slate-900 shadow-md dark:bg-[#060e19] dark:text-slate-300 sm:text-base sm:leading-7"
        >
            {#if current_chat}
                {#each current_chat.messages as message, index}
                    {#if message.role === "user"}
                        <div class="flex px-4 py-8 sm:px-6">
                            <img
                                    class="mr-2 flex h-8 w-8 rounded-full sm:mr-4"
                                    src="https://dummyimage.com/256x256/363536/ffffff&text=U"
                                    alt="User"
                            />

                            <div class="flex max-w-3xl items-center">
                                {message.content.trim()}
                            </div>
                        </div>
                    {:else}
                        <div class="flex bg-slate-100 px-4 py-8 dark:bg-slate-900 sm:px-6">
                            <img
                                    class="mr-2 flex h-8 w-8 rounded-full sm:mr-4"
                                    src="https://dummyimage.com/256x256/354ea1/ffffff&text=G"
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
                                </div>
                            </div>
                        </div>
                    {/if}
                {/each}
            {/if}
        </div>
        <!-- Prompt message input -->
        <form
                class="flex w-full items-center rounded-b-md border-t border-slate-300 bg-slate-200 p-8 pb-0 dark:border-slate-700 dark:bg-[#05060a]"
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
                    class="prompt-input mx-6 p-2 flex min-h-full w-full rounded-md border border-slate-300 bg-slate-50 text-base text-slate-900 placeholder-slate-400 focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:border-slate-700 dark:bg-[#060e19] dark:text-slate-50 dark:placeholder-slate-400 dark:focus:border-blue-600 dark:focus:ring-blue-600"
                    placeholder="Enter your prompt"
                    bind:value={text}
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
    {#if configuration_sidebar_visible}
        <aside class="flex">
            <div
                    class="relative h-screen w-60 overflow-y-auto border-l border-slate-300 bg-slate-50 py-8 dark:border-slate-700 dark:bg-[#05060a] sm:w-64"
            >
                <div
                        class="mb-4 flex items-center gap-x-2 px-2 text-slate-800 dark:text-slate-200"
                >
                    <button class="inline-flex rounded-lg p-1 hover:bg-slate-700" on:click={toggleSidebar}>
                        <svg
                                xmlns="http://www.w3.org/2000/svg"
                                class="h-6 w-6"
                                stroke-width="2"
                                stroke="currentColor"
                                fill="none"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                        >
                            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                            <path
                                    d="M4 4m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2z"
                            ></path>
                            <path d="M9 4v16"></path>
                            <path d="M14 10l2 2l-2 2"></path>
                        </svg>
                        <span class="sr-only">Close settings sidebar</span>
                    </button>
                    <h2 class="text-lg font-medium">Settings</h2>
                </div>

                <div
                        class="my-4 border-t border-slate-300 px-2 py-4 text-slate-800 dark:border-slate-700 dark:text-slate-200"
                >
                    <label
                            for="select-model"
                            class="mb-2 mt-4 block px-2 text-sm font-medium"
                    >Model</label
                    >
                    <select
                            name="select-model"
                            id="select-model"
                            class="block w-full cursor-pointer rounded-lg border-r-4 border-transparent bg-slate-200 py-3 pl-1 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 dark:bg-[#060e19] dark:placeholder-slate-400 dark:focus:ring-blue-600"
                    >
                        <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                        <option value="gpt-4">gpt-4</option>
                        <option value="gpt-4-0314">gpt-4-0314</option>
                        <option value="gpt-4-32k">gpt-4-32k</option>
                        <option value="gpt-4-32k-0314">gpt-4-32k-0314</option>
                        <option value="gpt-3.5-turbo-0301">gpt-3.5-turbo-0301</option>
                    </select>

                    <label for="max-tokens" class="mb-2 mt-4 block px-2 text-sm font-medium"
                    >Max tokens</label
                    >
                    <input
                            type="number"
                            id="max-tokens"
                            class="block w-full rounded-lg bg-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 dark:bg-[#060e19] dark:placeholder-slate-400 dark:focus:ring-blue-600"
                            placeholder="2048"
                            bind:value={max_tokens}
                    />

                    <label for="temperature" class="mb-2 mt-4 block px-2 text-sm font-medium"
                    >Temperature</label
                    >
                    <input
                            type="number"
                            id="temperature"
                            class="block w-full rounded-lg bg-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 dark:bg-[#060e19] dark:placeholder-slate-400 dark:focus:ring-blue-600"
                            placeholder="0.7"
                            bind:value={temperature}
                    />

                    <label for="top-p" class="mb-2 mt-4 block px-2 text-sm font-medium"
                    >Top P</label
                    >
                    <input
                            type="number"
                            id="top-p"
                            class="block w-full rounded-lg bg-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 dark:bg-[#060e19] dark:placeholder-slate-400 dark:focus:ring-blue-600"
                            placeholder="1"
                            bind:value={top_p}
                    />
                    <label for="top-k" class="mb-2 mt-4 block px-2 text-sm font-medium"
                    >Top K</label
                    >
                    <input
                            type="number"
                            id="top-k"
                            class="block w-full rounded-lg bg-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 dark:bg-[#060e19] dark:placeholder-slate-400 dark:focus:ring-blue-600"
                            placeholder="0"
                            bind:value={top_k}
                    />


                    <label for="min-p" class="mb-2 mt-4 block px-2 text-sm font-medium"
                    >Min P</label
                    >
                    <input
                            type="number"
                            id="min-p"
                            class="block w-full rounded-lg bg-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 dark:bg-[#060e19] dark:placeholder-slate-400 dark:focus:ring-blue-600"
                            placeholder="0"
                            bind:value={min_p}
                    />

                    <label for="typ-p" class="mb-2 mt-4 block px-2 text-sm font-medium"
                    >Typical P</label
                    >
                    <input
                            type="number"
                            id="typ-p"
                            class="block w-full rounded-lg bg-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 dark:bg-[#060e19] dark:placeholder-slate-400 dark:focus:ring-blue-600"
                            placeholder="1"
                            bind:value={typ_p}
                    />
                    <label for="tfsz" class="mb-2 mt-4 block px-2 text-sm font-medium"
                    >Tail Free Sampling</label
                    >
                    <input
                            type="number"
                            id="tfsz"
                            class="block w-full rounded-lg bg-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 dark:bg-[#060e19] dark:placeholder-slate-400 dark:focus:ring-blue-600"
                            placeholder="1"
                            bind:value={tfsz}
                    />

                    <label for="rep-pen" class="mb-2 mt-4 block px-2 text-sm font-medium"
                    >Repetition Penalty</label
                    >
                    <input
                            type="number"
                            id="rep-pen"
                            class="block w-full rounded-lg bg-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 dark:bg-[#060e19] dark:placeholder-slate-400 dark:focus:ring-blue-600"
                            placeholder="1.2"
                            bind:value={rep_pen}
                    />
                    <label for="rep-pen-range" class="mb-2 mt-4 block px-2 text-sm font-medium"
                    >Repetition Penalty Range</label
                    >
                    <input
                            type="number"
                            id="rep-pen-range"
                            class="block w-full rounded-lg bg-slate-200 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 dark:bg-[#060e19] dark:placeholder-slate-400 dark:focus:ring-blue-600"
                            placeholder="512"
                            bind:value={rep_pen_range}
                    />
                </div>
            </div>
        </aside>
    {:else}
        <div class="hidden">
            <!-- This is technically not visible, but you can place additional logic or styling here if needed. -->
        </div>
    {/if}
    <!-- Sidebar -->

</div>

<style>
    .hidden {
        transform: translateX(-100%);
    }
    .message {
        white-space: pre-wrap; /* Preserves whitespace and wraps text */
    }
    .prompt-input {
        resize: none;
    }
</style>