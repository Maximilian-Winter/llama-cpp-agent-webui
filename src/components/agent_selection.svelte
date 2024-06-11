<script lang="ts">
    // Define the type for individual panels
    import {onMount} from "svelte";
    import {
        app_mode,
        Chat, current_agent_description,
        current_agent_id, current_agent_instructions,
        current_agent_name,
        current_chat,
        Message,
        text
    } from "../stores/app_store";
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();
    type Panel = {
        id: number;
        name: string;
        description: string;
        instructions: string;
    };

    let panels: Panel[] = [];
    async function update_agent(id: number, name:string, description:string, instructions:string): Promise<void> {
        current_agent_id.set(id)
        current_agent_name.set(name)
        current_agent_description.set(description)
        current_agent_instructions.set(instructions)
        app_mode.set("agent_update")
    }
    async function fetchPanelData(): Promise<Panel[]> {
        const response = await fetch('http://localhost:8042/agents/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }
    async function start_chat(id: number): Promise<void> {
        const payload = {
            title: "New Chat",
            agent_id: id
        };
        current_agent_id.set(id)
        const response = await fetch('http://localhost:8042/chats/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        if (response.ok) {
            let new_chat = await response.json()
            current_chat.set(new Chat(new_chat.id, new_chat.title, new_chat.agent, new_chat.instructions));
            current_chat.update(chat => {
                const newMessage = new Message(-1, "system", new_chat.agent.instructions);
                chat.messages.push(newMessage);
                return chat;
            });
            dispatch('newChat');
            app_mode.set("chat");
        }

    }
    onMount(() => {
        fetchPanelData()
            .then(data => {
                panels = data;
            })
            .catch(error => {
                console.error('Failed to fetch panels:', error);
            });
    });
</script>

<style>
    .panel {
        border: 1px solid #c2c2c2;
        padding: 15px;
        box-shadow: 0 2px 5px rgb(0, 0, 0); /* Subtle shadow for depth */
    }
</style>
<div class="flex h-[97vh] w-full flex-col">
    <div
            class="mt-20 ml-20 mr-20 flex-1 overflow-y-auto bg-[#0d1117] text-sm leading-6 text-slate-900 shadow-md dark:bg-[#0d1117] dark:text-slate-300 sm:text-base sm:leading-7"
    >
        <div class="grid grid-cols-4 gap-2">
            {#each panels as { id, name, description, instructions }}
                <div class="panel w-72 h-72 bg-slate-800 p-5 items-center overflow-y-auto">
                    <button class="m-1 hover:text-blue-600 dark:hover:text-blue-600" on:click={() => start_chat(id)}>
                        <svg class="w-8 h-8" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                            <path fill-rule="evenodd" d="M3.559 4.544c.355-.35.834-.544 1.33-.544H19.11c.496 0 .975.194 1.33.544.356.35.559.829.559 1.331v9.25c0 .502-.203.981-.559 1.331-.355.35-.834.544-1.33.544H15.5l-2.7 3.6a1 1 0 0 1-1.6 0L8.5 17H4.889c-.496 0-.975-.194-1.33-.544A1.868 1.868 0 0 1 3 15.125v-9.25c0-.502.203-.981.559-1.331ZM7.556 7.5a1 1 0 1 0 0 2h8a1 1 0 0 0 0-2h-8Zm0 3.5a1 1 0 1 0 0 2H12a1 1 0 1 0 0-2H7.556Z" clip-rule="evenodd"/>
                        </svg>

                    </button>
                    <button class="m-1 hover:text-blue-600 dark:hover:text-blue-600" on:click={() => update_agent(id, name, description, instructions)}>
                        <svg class="w-8 h-8" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m14.304 4.844 2.852 2.852M7 7H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-4.5m2.409-9.91a2.017 2.017 0 0 1 0 2.853l-6.844 6.844L8 14l.713-3.565 6.844-6.844a2.015 2.015 0 0 1 2.852 0Z"/>
                        </svg>

                    </button>


                    <h2 class="font-bold">{name}</h2>
                    <p>{description}</p>
                </div>


            {/each}
        </div>
    </div>
</div>