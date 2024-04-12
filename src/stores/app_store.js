import { writable } from 'svelte/store';

export class Agent {
    /**
     * @param {number} id
     * @param {string} name
     * @param {string} instructions
     */
    constructor(id, name, instructions) {
        this.id = id;
        this.name = name;
        this.instructions = instructions;
    }
}
export class Message {

    /**
     * @param {number} id
     * @param {string} role
     * @param {string} content
     */
    constructor(id, role, content) {
        this.id = id;
        this.role = role;
        this.content = content;
    }
}
export class Chat {
    /**
     * @param {number} id
     * @param {string} title
     * @param {Agent} agent
     * @param {Message[]} messages
     * @param {string} timestamp
     */
    constructor(id, title = "", agent= new Agent(1,"Helpful Assistant", "You are a helpful assistant."), messages=[], timestamp= "Today") {
        this.id = id;
        this.title = title;
        this.agent = agent;
        this.messages = messages;
        this.timestamp = timestamp;
    }
}

export class Chats {
    /**
     * @param {Chat[]} chats
     */
    constructor(chats= []) {
        this.chats = chats;
    }
}
export let app_mode = writable("chat");
export let sidebarVisible = writable(false);
export let current_chat =  writable(new Chat(-1));

export let max_tokens = writable(2048);
export let temperature = writable(0.7);
export let top_p = writable(1);
export let top_k = writable(0);
export let min_p = writable(0);
export let typ_p = writable(1);
export let tfsz = writable(1);
export let rep_pen = writable(1.2);
export let rep_pen_range = writable(512);
export let text = writable("");

export let new_agent_name = writable("");

export let new_agent_instructions = writable("");
export let chats = writable(new Chats());

