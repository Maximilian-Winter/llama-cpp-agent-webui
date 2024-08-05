<script lang="ts">
    import { current_chat, sidebarVisible, GenerationSettings } from "../stores/app_store";
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    function toggleSidebar() {
        sidebarVisible.update((v) => !v);
    }

    function updateSettings(key: keyof GenerationSettings, value: number) {
        current_chat.update(chat => {
            chat.settings.update({ [key]: value });
            return chat;
        });
        dispatch('updateSettings', $current_chat.settings);
    }
</script>

<aside class="flex">
    <div class="relative h-screen w-64 overflow-y-auto border-l border-slate-700 bg-[#161b22] py-8">
        <div class="mb-6 flex items-center justify-between px-4">
            <h2 class="text-lg font-semibold text-slate-200">Settings</h2>
            <button class="rounded-md p-1 text-slate-400 transition duration-200 ease-in-out hover:bg-slate-700 hover:text-slate-200 focus:outline-none" on:click={toggleSidebar}>
                <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span class="sr-only">Close settings sidebar</span>
            </button>
        </div>

        <div class="space-y-6 px-4">
            <div>
                <label for="max-tokens" class="block text-sm font-medium text-slate-400">Max tokens</label>
                <input type="number" id="max-tokens" class="mt-1 block w-full rounded-md border-slate-700 bg-[#0d1117] py-2 pl-3 pr-10 text-base text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm" placeholder="2048"
                       bind:value={$current_chat.settings.max_tokens}
                       on:change={(e) => updateSettings('max_tokens', +e.currentTarget.value)}>
            </div>

            <div>
                <label for="temperature" class="block text-sm font-medium text-slate-400">Temperature</label>
                <input type="number" id="temperature" class="mt-1 block w-full rounded-md border-slate-700 bg-[#0d1117] py-2 pl-3 pr-10 text-base text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm" placeholder="0.7"
                       bind:value={$current_chat.settings.temperature}
                       on:change={(e) => updateSettings('temperature', +e.currentTarget.value)}>
            </div>

            <div>
                <label for="top-p" class="block text-sm font-medium text-slate-400">Top P</label>
                <input type="number" id="top-p" class="mt-1 block w-full rounded-md border-slate-700 bg-[#0d1117] py-2 pl-3 pr-10 text-base text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm" placeholder="1"
                       bind:value={$current_chat.settings.top_p}
                       on:change={(e) => updateSettings('top_p', +e.currentTarget.value)}>
            </div>

            <div>
                <label for="top-k" class="block text-sm font-medium text-slate-400">Top K</label>
                <input type="number" id="top-k" class="mt-1 block w-full rounded-md border-slate-700 bg-[#0d1117] py-2 pl-3 pr-10 text-base text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm" placeholder="0"
                       bind:value={$current_chat.settings.top_k}
                       on:change={(e) => updateSettings('top_k', +e.currentTarget.value)}>
            </div>

            <div>
                <label for="min-p" class="block text-sm font-medium text-slate-400">Min P</label>
                <input type="number" id="min-p" class="mt-1 block w-full rounded-md border-slate-700 bg-[#0d1117] py-2 pl-3 pr-10 text-base text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm" placeholder="0"
                       bind:value={$current_chat.settings.min_p}
                       on:change={(e) => updateSettings('min_p', +e.currentTarget.value)}>
            </div>

            <div>
                <label for="typ-p" class="block text-sm font-medium text-slate-400">Typical P</label>
                <input type="number" id="typ-p" class="mt-1 block w-full rounded-md border-slate-700 bg-[#0d1117] py-2 pl-3 pr-10 text-base text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm" placeholder="1"
                       bind:value={$current_chat.settings.typ_p}
                       on:change={(e) => updateSettings('typ_p', +e.currentTarget.value)}>
            </div>

            <div>
                <label for="tfsz" class="block text-sm font-medium text-slate-400">Tail Free Sampling</label>
                <input type="number" id="tfsz" class="mt-1 block w-full rounded-md border-slate-700 bg-[#0d1117] py-2 pl-3 pr-10 text-base text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm" placeholder="1"
                       bind:value={$current_chat.settings.tfsz}
                       on:change={(e) => updateSettings('tfsz', +e.currentTarget.value)}>
            </div>

            <div>
                <label for="rep-pen" class="block text-sm font-medium text-slate-400">Repetition Penalty</label>
                <input type="number" id="rep-pen" class="mt-1 block w-full rounded-md border-slate-700 bg-[#0d1117] py-2 pl-3 pr-10 text-base text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm" placeholder="1.2"
                       bind:value={$current_chat.settings.rep_pen}
                       on:change={(e) => updateSettings('rep_pen', +e.currentTarget.value)}>
            </div>

            <div>
                <label for="rep-pen-range" class="block text-sm font-medium text-slate-400">Repetition Penalty Range</label>
                <input type="number" id="rep-pen-range" class="mt-1 block w-full rounded-md border-slate-700 bg-[#0d1117] py-2 pl-3 pr-10 text-base text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm" placeholder="512"
                       bind:value={$current_chat.settings.rep_pen_range}
                       on:change={(e) => updateSettings('rep_pen_range', +e.currentTarget.value)}>
            </div>
        </div>
    </div>
</aside>