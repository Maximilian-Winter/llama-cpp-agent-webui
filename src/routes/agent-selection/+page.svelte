<script lang="ts">
    import { onMount } from "svelte";
    import {
        Agent,
        current_agent_description,
        current_agent_id,
        current_agent_instructions,
        current_agent_name,
        current_chat,
        Message,
    } from "$lib/stores/app_store";
    import DeleteAgent from "$lib/components/delete_agent.svelte";
    import { createChat } from "$lib/api/chats";
    import { deleteAgent, getAgents } from "$lib/api/agents";
    import { Trash2, Edit, MessageSquare } from 'lucide-svelte';
    import {goto} from "$app/navigation";

    let agents: Agent[] = [];

    async function update_agent(id: number, name: string, description: string, instructions: string): Promise<void> {
        current_agent_id.set(id)
        current_agent_name.set(name)
        current_agent_description.set(description)
        current_agent_instructions.set(instructions)
        await goto("/agent-update");
    }

    async function fetchAgents(): Promise<Agent[]> {
        return await getAgents();
    }

    let deletingAgent = false;
    let agentId = -1;

    async function delete_agent(id: number): Promise<void> {
        agentId = id;
        deletingAgent = true;
    }

    async function handleDeleteAgent(e: CustomEvent<{ id: number }>): Promise<void> {
        await deleteAgent(e.detail.id);
        deletingAgent = false;
        agents = await fetchAgents();
    }

    async function handleCancelDeleteAgent(): Promise<void> {
        deletingAgent = false;
    }

    async function start_chat(id: number): Promise<void> {
        current_agent_id.set(id)
        const response = await createChat("New Chat", id);
        const newMessage = new Message(-1, "system", response.agent.instructions, "Today");
        response.messages.push(newMessage);
        current_chat.set(response);
        await goto("/chat");
    }

    onMount(async () => {
        agents = await fetchAgents();
    });
</script>

<div class="min-h-screen w-full bg-[#0d1117] text-slate-300 px-4 py-8">
    <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold mb-8 text-center">Agent Selection</h1>

        {#if agents.length === 0}
            <p class="text-center text-slate-400">No agents available. Create a new agent to get started.</p>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {#each agents as { id, name, description, instructions }}
                    <div class="bg-[#1c2128] rounded-lg shadow-lg overflow-hidden transition-transform duration-300 hover:scale-105">
                        <div class="p-6">
                            <h2 class="text-xl font-semibold mb-2">{name}</h2>
                            <p class="text-slate-400 mb-4">{description}</p>
                            <div class="flex justify-between items-center">
                                <button
                                        class="flex items-center space-x-2 text-blue-400 hover:text-blue-300 transition-colors duration-200"
                                        on:click={() => start_chat(id)}
                                >
                                    <MessageSquare size={18} />
                                    <span>Start Chat</span>
                                </button>
                                <div class="flex space-x-2">
                                    <button
                                            class="p-2 text-slate-400 hover:text-blue-400 transition-colors duration-200"
                                            on:click={() => update_agent(id, name, description, instructions)}
                                            title="Edit Agent"
                                    >
                                        <Edit size={18} />
                                    </button>
                                    <button
                                            class="p-2 text-slate-400 hover:text-red-400 transition-colors duration-200"
                                            on:click={() => delete_agent(id)}
                                            title="Delete Agent"
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
</div>

{#if deletingAgent}
    <DeleteAgent agentId={agentId} on:delete_agent={handleDeleteAgent} on:close={handleCancelDeleteAgent}/>
{/if}

<style>
    :global(body) {
        @apply bg-[#0d1117] text-slate-300;
    }
</style>