import { writable } from 'svelte/store';

export const fileContent = writable<string>('');
export const selectedFilePath = writable<string>('');
export const reloadFileTree = writable<number>(0); // A simple counter to trigger reloads
