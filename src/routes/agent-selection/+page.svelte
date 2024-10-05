<script lang="ts">
    // Define the type for individual panels
    import {createEventDispatcher, onMount} from "svelte";
    import {
        Agent,
        app_mode,
        current_agent_description,
        current_agent_id,
        current_agent_instructions,
        current_agent_name,
        current_chat,
        Message,
    } from "$lib/stores/app_store";
    import DeleteAgent from "$lib/components/delete_agent.svelte";
    import {createChat} from "$lib/api/chats";
    import {deleteAgent, getAgents} from "$lib/api/agents";

    const dispatch = createEventDispatcher();

    let agents: Agent[] = [];
    async function update_agent(id: number, name:string, description:string, instructions:string): Promise<void> {
        current_agent_id.set(id)
        current_agent_name.set(name)
        current_agent_description.set(description)
        current_agent_instructions.set(instructions)
        app_mode.set("agent_update")
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

    interface AgentId
    {
        id: number;
    }
    async function handleDeleteAgent(e: CustomEvent<AgentId>): Promise<void> {
        await deleteAgent(e.detail.id);
        deletingAgent = false;
        fetchAgents()
            .then(data => {
                agents = data;
            })
            .catch(error => {
                console.error('Failed to fetch panels:', error);
            });
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

        dispatch('newChat');
    }
    onMount(() => {
        fetchAgents()
            .then(data => {
                agents = data;
            })
            .catch(error => {
                console.error('Failed to fetch panels:', error);
            });
    });

</script>

<div class="flex min-h-screen w-full flex-col bg-[#0d1117] text-slate-300">
    <div class="mx-auto my-8 w-full max-w-7xl px-4">
        <h1 class="mb-8 text-3xl font-bold">Agent Selection</h1>
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {#each agents as { id, name, description, instructions }}
                <div class="overflow-hidden rounded-lg bg-[#161b22] shadow-md">
                    <div class="p-4">
                        <h2 class="mb-2 text-xl font-bold">{name}</h2>
                        <p class="mb-4 text-sm text-slate-400">{description}</p>
                        <div class="flex justify-end space-x-2">
                            <button class="rounded-md p-2 text-slate-400 transition duration-200 ease-in-out hover:bg-blue-600 hover:text-white focus:outline-none" title="Start Chat" on:click={() => start_chat(id)}>
                                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                                    <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
                                </svg>
                            </button>
                            <button class="rounded-md p-2 text-slate-400 transition duration-200 ease-in-out hover:bg-blue-600 hover:text-white focus:outline-none" title="Edit Agent" on:click={() => update_agent(id, name, description, instructions)}>
                                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                </svg>
                            </button>
                            <button class="rounded-md p-2 text-slate-400 transition duration-200 ease-in-out hover:bg-red-600 hover:text-white focus:outline-none" title="Delete Agent" on:click={() => delete_agent(id)}>
                                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            {/each}
            {#if deletingAgent}
                <DeleteAgent agentId={agentId} on:delete_agent={handleDeleteAgent} on:close={handleCancelDeleteAgent}/>
            {/if}
        </div>
    </div>
</div>