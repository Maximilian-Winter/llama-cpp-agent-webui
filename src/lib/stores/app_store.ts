import { writable } from 'svelte/store';
import type {Agent, Chat, Chats, GenerationSettings, Message} from "$lib/types/api";


// Helper functions for creating objects with default values
export const createAgent = (
    id: number,
    name: string = "Helpful Assistant",
    description: string = "A helpful assistant.",
    instructions: string = "You are a helpful assistant."
): Agent => ({
    id,
    name,
    description,
    instructions
});

export const createMessage = (
    id: number,
    role: string,
    content: string,
    timestamp: string
): Message => ({
    id,
    role,
    content,
    timestamp
});

export const createGenerationSettings = (
    params: Partial<GenerationSettings> = {}
): GenerationSettings => ({
    max_tokens: 2048,
    temperature: 0.7,
    top_p: 1,
    top_k: 0,
    min_p: 0,
    typ_p: 1,
    tfsz: 1,
    rep_pen: 1.2,
    rep_pen_range: 512,
    show_agent_instructions: false,
    ...params
});

export const createChat = (
    id: number,
    title: string = "",
    agent: Agent = createAgent(1),
    messages: Message[] = [],
    timestamp: string = "Today",
    settings: GenerationSettings = createGenerationSettings()
): Chat => ({
    id,
    title,
    agent,
    messages,
    timestamp,
    settings
});

export const createChats = (chats: Chat[] = []): Chats => ({ chats });


export const cloneGenerationSettings = (settings: GenerationSettings): GenerationSettings =>
    createGenerationSettings(settings);

export const updateGenerationSettings = (
    settings: GenerationSettings,
    newSettings: Partial<GenerationSettings>
): GenerationSettings => ({
    ...settings,
    ...newSettings
});

// Svelte stores
export const sidebarVisible = writable<boolean>(false);
export const current_chat = writable<Chat>(createChat(-1));
export const text = writable<string>("");
export const current_agent_id = writable<number>(1);
export const current_agent_name = writable<string>("");
export const current_agent_instructions = writable<string>("");
export const current_agent_description = writable<string>("");
export const chats = writable<Chats>(createChats());

