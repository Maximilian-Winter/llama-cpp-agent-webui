<script>
    import {
        current_agent_id,
        current_agent_name,
        current_agent_description,
        current_agent_instructions,
        app_mode
    } from "../stores/app_store.js";

    async function update_agent() {
        if ($current_agent_name === '') {
            return
        }

        if ($current_agent_id === -1)
        {
            return
        }
        const payload = {
            name: $current_agent_name,
            description: $current_agent_description,
            instructions: $current_agent_instructions
        };
        const response = await fetch('http://localhost:8042/agents/' + $current_agent_id, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (response.ok) {
            app_mode.update(() => 'agent_selection')
        }
    }

</script>

<div class="flex min-h-screen w-full flex-col bg-[#0d1117] text-slate-300">
    <div class="mx-auto w-full max-w-3xl px-4 py-8">
        <h1 class="mb-8 text-3xl font-bold">Update Agent</h1>
        <form class="space-y-6" on:submit|preventDefault={update_agent}>
            <div>
                <label for="new-agent-name-input" class="block text-sm font-medium">Agent Name</label>
                <input
                        id="new-agent-name-input"
                        type="text"
                        class="mt-1 block w-full rounded-md border-gray-300 bg-[#161b22] px-4 py-2 text-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="Enter agent name"
                        bind:value={$current_agent_name}
                        required
                />
            </div>

            <div>
                <label for="new-agent-description-input" class="block text-sm font-medium">Agent Description</label>
                <input
                        id="new-agent-description-input"
                        type="text"
                        class="mt-1 block w-full rounded-md border-gray-300 bg-[#161b22] px-4 py-2 text-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="Enter agent description"
                        bind:value={$current_agent_description}
                        required
                />
            </div>

            <div>
                <label for="new-agent-instructions-input" class="block text-sm font-medium">Agent Instructions</label>
                <textarea
                        id="new-agent-instructions-input"
                        class="mt-1 block w-full rounded-md border-gray-300 bg-[#161b22] px-4 py-2 text-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="Enter agent instructions"
                        rows="6"
                        bind:value={$current_agent_instructions}
                        required
                ></textarea>
            </div>

            <div>
                <button
                        type="submit"
                        class="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                    <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                    </svg>
                    Update Agent
                </button>
            </div>
        </form>
    </div>
</div>


<style>
    .agent-instructions {
        resize: none;
    }
</style>