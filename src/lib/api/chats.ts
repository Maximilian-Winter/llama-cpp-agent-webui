import type {Chat} from "$lib/types/api";


const API_BASE_URL = 'http://localhost:8042';

export async function createChat(title: string, agentId: number): Promise<Chat> {
    const payload = { title, agent_id: agentId };
    const response = await fetch(`${API_BASE_URL}/chats/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error('Failed to create chat.');
    }
    return await response.json();
}

export async function getChatById(id: number): Promise<Chat> {
    const response = await fetch(`${API_BASE_URL}/chats/${id}`);
    if (!response.ok) {
        throw new Error('Failed to fetch chat.');
    }

    return await response.json();
}

export async function updateChatTitle(id: number, title: string): Promise<Chat> {
    const response = await fetch(`${API_BASE_URL}/chats/${id}/${title}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
    });
    if (!response.ok) {
        throw new Error('Failed to update chat title.');
    }
    return await response.json();
}

export async function deleteChat(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chats/${id}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        throw new Error('Failed to delete chat.');
    }
}

export async function getAllChats(): Promise<Chat[]> {
    const response = await fetch(`${API_BASE_URL}/chats/`);
    if (!response.ok) {
        throw new Error('Failed to fetch chats.');
    }
    return await response.json();
}

export async function updateChatSettings(id: number, settings: any): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chats/${id}/settings`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
    });

    if (!response.ok) {
        console.error('Failed to update settings on backend');
    }

}
