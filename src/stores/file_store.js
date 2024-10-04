import { writable } from 'svelte/store';

export const fileContent = writable('');
export const selectedFilePath = writable('');
export const reloadFileTree = writable(0); // A simple counter to trigger reloads
