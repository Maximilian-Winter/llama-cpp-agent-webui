<script lang="ts">
    import { goto } from '$app/navigation';
    import { updateAgent } from "$lib/api/agents";
    import UnifiedAgentForm from '$lib/components/UnifiedAgentForm.svelte';
    import { current_agent_id, current_agent_name, current_agent_description, current_agent_instructions } from "$lib/stores/app_store";

    async function handleSubmit(event: CustomEvent) {
        const { name, description, instructions } = event.detail;
        if ($current_agent_id !== -1) {
            await updateAgent($current_agent_id, name, description, instructions);
            await goto("/agent-selection");
        }
    }
</script>

<div class="min-h-screen bg-[#0d1117] text-slate-300 p-8">
    <div class="max-w-2xl mx-auto">
        <h1 class="text-3xl font-bold mb-8">Update Agent</h1>
        <UnifiedAgentForm
                agentId={$current_agent_id}
                name={$current_agent_name}
                description={$current_agent_description}
                instructions={$current_agent_instructions}
                on:submit={handleSubmit}
        />
    </div>
</div>