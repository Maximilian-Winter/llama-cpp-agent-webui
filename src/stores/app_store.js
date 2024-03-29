import { writable } from 'svelte/store';

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
     * @type {Message[]}
     */
    messages = [];
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
