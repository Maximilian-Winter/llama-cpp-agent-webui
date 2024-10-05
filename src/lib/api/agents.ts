import type {Agent} from "$lib/stores/app_store";

export async function getAgents(): Promise<Agent[]> {
    const response = await fetch('http://localhost:8042/agents/');
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

export async function deleteAgent(id: number): Promise<void> {
    const response = await fetch('http://localhost:8042/agents/' + id, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
}

export async function addAgent(agent_name: string, agent_description: string, agent_instructions: string): Promise<void> {3
    let payload = {name: agent_name, description: agent_description, instructions: agent_instructions};
    const response = await fetch('http://localhost:8042/agents/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
}

export async function updateAgent(agent_id: number, agent_name: string, agent_description: string, agent_instructions: string): Promise<void> {3
    let payload = {name: agent_name, description: agent_description, instructions: agent_instructions};
    const response = await fetch('http://localhost:8042/agents/' + agent_id, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
}