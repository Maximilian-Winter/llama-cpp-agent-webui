import { writable } from 'svelte/store';

export class Agent {
    /**
     * @param {string} name
     * @param {string} instructions
     */
    constructor(name, instructions) {
        this.name = name;
        this.instructions = instructions;
    }
}
export class Message {

    /**
     * @param {string} role
     * @param {string} content
     */
    constructor(role, content) {
        this.role = role;
        this.content = content;
    }
}
export class Chat {
    /**
     * @param {string} title
     * @param {Agent} agent
     * @param {Message[]} messages
     */
    constructor(title = "", agent= new Agent("Jack", "You are a helpful assistant."), messages=[]) {
        this.title = title;
        this.agent = agent;
        this.messages = messages;
    }
}

export let app_mode = writable("chat");
export let sidebarVisible = writable(false);
export let current_chat =  writable(new Chat());

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
