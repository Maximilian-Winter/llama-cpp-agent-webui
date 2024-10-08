<script lang="ts">
    import { createEventDispatcher } from 'svelte';

    export let agentId: number | null = null;
    export let name: string = '';
    export let description: string = '';
    export let instructions: string = '';

    const dispatch = createEventDispatcher();

    function handleSubmit() {
        dispatch('submit', { agentId, name, description, instructions });
    }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6">
    <div>
        <label for="agent-name" class="block text-sm font-medium text-slate-300 mb-1">Agent Name</label>
        <input
                id="agent-name"
                type="text"
                class="w-full px-3 py-2 bg-[#1c2128] border border-slate-600 rounded-md text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter agent name"
                bind:value={name}
                required
        />
    </div>

    <div>
        <label for="agent-description" class="block text-sm font-medium text-slate-300 mb-1">Agent Description</label>
        <input
                id="agent-description"
                type="text"
                class="w-full px-3 py-2 bg-[#1c2128] border border-slate-600 rounded-md text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter agent description"
                bind:value={description}
                required
        />
    </div>

    <div>
        <label for="agent-instructions" class="block text-sm font-medium text-slate-300 mb-1">Agent Instructions</label>
        <textarea
                id="agent-instructions"
                class="w-full px-3 py-2 bg-[#1c2128] border border-slate-600 rounded-md text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter agent instructions"
                rows="6"
                bind:value={instructions}
                required
        ></textarea>
    </div>

    <button
            type="submit"
            class="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800"
    >
        {agentId ? 'Update Agent' : 'Create Agent'}
    </button>
</form>