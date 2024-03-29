<script>

</script>

<div class="flex h-[97vh] w-full flex-col">
    <!-- Prompt Messages -->
    <div
            class="mt-20 ml-20 mr-20 flex-1 overflow-y-auto bg-[#0d1117] text-sm leading-6 text-slate-900 shadow-md dark:bg-[#0d1117] dark:text-slate-300 sm:text-base sm:leading-7"
    >
        <form class="">
            <label for="chat-input" class="sr-only">Enter agent name</label>
            <div class="flex gap-x-2">
                <input
                        id="chat-input"
                        type="text"
                        class="w-full rounded-lg border border-slate-300 bg-slate-200 p-3 text-sm text-slate-800 shadow-md focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:border-slate-200/10 dark:bg-[#171E28] dark:text-slate-200 dark:placeholder-slate-400 dark:focus:border-blue-600 sm:text-base"
                        placeholder="Enter agent name"

                        required
                />

            </div>
            <label for="chat-input" class="sr-only">Enter agent instructions</label>
            <div class="flex gap-x-2">
                <textarea
                        id="chat-input"
                        class="w-full agent-instructions rounded-lg border border-slate-300 bg-slate-200 p-3 text-sm text-slate-800 shadow-md focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:border-slate-200/10 dark:bg-[#171E28] dark:text-slate-200 dark:placeholder-slate-400 dark:focus:border-blue-600 sm:text-base"
                        placeholder="Enter agent instructions"
                        rows="30"
                        required
                />

            </div>

            <button
                    type="submit"
                    class="rounded-lg border border-transparent bg-blue-600 px-3 py-1 text-slate-200 hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300"
            >
                <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-10 w-1/4 align-middle "
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
                <span class="sr-only">Enter prompt</span>
            </button>
        </form>
    </div>
    <!-- Prompt message input -->

</div>


<style>
    .agent-instructions {
        resize: none;
    }
</style>