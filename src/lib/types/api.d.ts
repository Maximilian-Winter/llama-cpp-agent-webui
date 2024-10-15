export interface FileResponse {
    id: number;
    path: string;
    filename: string;
    content: string;
    created_at: string;
    updated_at: string;
}
export interface FilePathResponse {
    id: number;
    path: string;
}
export interface Agent {
    id: number;
    name: string;
    description: string;
    instructions: string;
}

export interface Message {
    id: number;
    role: string;
    content: string;
    timestamp: string;
}

export interface GenerationSettings {
    max_tokens: number;
    temperature: number;
    top_p: number;
    top_k: number;
    min_p: number;
    typ_p: number;
    tfsz: number;
    rep_pen: number;
    rep_pen_range: number;
    show_agent_instructions: boolean;
}

export interface Chat {
    id: number;
    title: string;
    agent: Agent;
    messages: Message[];
    timestamp: string;
    settings: GenerationSettings;
}

export interface Chats {
    chats: Chat[];
}