import { writable } from 'svelte/store';

export class Agent {
    /**
     * @param {number} id
     * @param {string} name
     * @param {string} description
     * @param {string} instructions
     */
    constructor(id, name, description, instructions) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.instructions = instructions;
    }
}
export class Message {

    /**
     * @param {number} id
     * @param {string} role
     * @param {string} content
     * @param {string} timestamp
     */
    constructor(id, role, content, timestamp) {
        this.id = id;
        this.role = role;
        this.content = content;
        this.timestamp = timestamp;
    }
}
/**
 * Represents the settings for text generation.
 */
export class GenerationSettings {
    /**
     * Creates a new GenerationSettings instance.
     * @param {Object} params - The parameters for generation settings
     * @param {number} [params.max_tokens=2048] - Maximum number of tokens to generate
     * @param {number} [params.temperature=0.7] - Temperature for text generation
     * @param {number} [params.top_p=1] - Top-p sampling threshold
     * @param {number} [params.top_k=0] - Top-k sampling threshold
     * @param {number} [params.min_p=0] - Minimum probability for token consideration
     * @param {number} [params.typ_p=1] - Typical sampling parameter
     * @param {number} [params.tfsz=1] - Tail free sampling parameter
     * @param {number} [params.rep_pen=1.2] - Repetition penalty factor
     * @param {number} [params.rep_pen_range=512] - Repetition penalty range
     */
    constructor({
                    max_tokens = 2048,
                    temperature = 0.7,
                    top_p = 1,
                    top_k = 0,
                    min_p = 0,
                    typ_p = 1,
                    tfsz = 1,
                    rep_pen = 1.2,
                    rep_pen_range = 512
                } = {}) {
        this.max_tokens = max_tokens;
        this.temperature = temperature;
        this.top_p = top_p;
        this.top_k = top_k;
        this.min_p = min_p;
        this.typ_p = typ_p;
        this.tfsz = tfsz;
        this.rep_pen = rep_pen;
        this.rep_pen_range = rep_pen_range;
    }

    /**
     * Converts the settings to a plain JavaScript object.
     * @returns {Object} Plain object representation of the settings
     */
    toJSON() {
        return {
            max_tokens: this.max_tokens,
            temperature: this.temperature,
            top_p: this.top_p,
            top_k: this.top_k,
            min_p: this.min_p,
            typ_p: this.typ_p,
            tfsz: this.tfsz,
            rep_pen: this.rep_pen,
            rep_pen_range: this.rep_pen_range
        };
    }

    /**
     * Creates a GenerationSettings instance from a plain JavaScript object.
     * @param {Object} json - Plain object containing generation settings
     * @returns {GenerationSettings} New GenerationSettings instance
     */
    static fromJSON(json) {
        return new GenerationSettings(json);
    }

    /**
     * Creates a deep copy of the current settings.
     * @returns {GenerationSettings} A new GenerationSettings instance with the same values
     */
    clone() {
        return new GenerationSettings(this.toJSON());
    }

    /**
     * Updates the current settings with new values.
     * @param {Partial<GenerationSettings>} newSettings - Object containing the settings to update
     */
    update(newSettings) {
        Object.assign(this, newSettings);
    }
}

/**
 * Represents a chat session.
 */
export class Chat {

    /**
     * Creates a new Chat instance.
     * @param {number} id - Unique identifier for the chat
     * @param {string} [title=""] - Title of the chat
     * @param {Agent} [agent=new Agent(1, "Helpful Assistant", "You are a helpful assistant.")] - Agent for the chat
     * @param {Message[]} [messages=[]] - Initial messages in the chat
     * @param {string} [timestamp="Today"] - Timestamp for the chat
     * @param {GenerationSettings} [settings=new GenerationSettings()] - Generation settings for the chat
     */
    constructor(id, title = "", agent = new Agent(1, "Helpful Assistant", "A helpful assistant.", "You are a helpful assistant."), messages = [], timestamp = "Today", settings = new GenerationSettings()) {
        this.id = id;
        this.title = title;
        this.agent = agent;
        this.messages = messages;
        this.timestamp = timestamp;
        this.settings = settings;
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

export let sidebarVisible = writable(false);
export let current_chat =  writable(new Chat(-1));

export let text = writable("");

export let new_agent_name = writable("");

export let new_agent_instructions = writable("");

export let new_agent_description = writable("");

export let current_agent_id = writable(1);

export let current_agent_name = writable("");

export let current_agent_instructions = writable("");

export let current_agent_description = writable("");

export let chats = writable(new Chats());

