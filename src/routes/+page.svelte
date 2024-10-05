<script lang="ts">
    import { goto } from '$app/navigation';
    async function _goto(url: string): Promise<void> {
        await goto(url);
    }
</script>
<div class="flex min-h-screen w-full bg-[#0d1117] text-slate-300">
    <div class="min-h-screen flex-col items-center justify-center bg-[#0d1117] text-slate-300">
        <h1 class="mb-8 text-4xl font-bold">Welcome to OpenAgent WebUI</h1>
        <div class="space-y-4">
            <button
                    class="w-full rounded-md bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-700"
                    on:click={() => _goto('/chat')}
            >
                Start Chatting
            </button>
            <button
                    class="w-full rounded-md bg-green-600 px-4 py-2 text-white transition-colors hover:bg-green-700"
                    on:click={() => _goto('/agent-selection')}
            >
                Select an Agent
            </button>
            <button
                    class="w-full rounded-md bg-purple-600 px-4 py-2 text-white transition-colors hover:bg-purple-700"
                    on:click={() => _goto('/agent-creation')}
            >
                Create a New Agent
            </button>
            <button
                    class="w-full rounded-md bg-yellow-600 px-4 py-2 text-white transition-colors hover:bg-yellow-700"
                    on:click={() => _goto('/file-management')}
            >
                File Management
            </button>
        </div>
    </div>
</div>

