<script lang="ts">
    import { goto } from '$app/navigation';
    import { addAgent } from "$lib/api/agents";
    import UnifiedAgentForm from '$lib/components/UnifiedAgentForm.svelte';

    async function handleSubmit(event: CustomEvent) {
        const { name, description, instructions } = event.detail;
        await addAgent(name, description, instructions);
        await goto("/agent-selection");
    }
</script>

<div class="min-h-screen bg-[#0d1117] text-slate-300 p-8">
    <div class="max-w-2xl mx-auto">
        <h1 class="text-3xl font-bold mb-8">Create New Agent</h1>
        <UnifiedAgentForm on:submit={handleSubmit} />
    </div>
</div>