import type { FileResponse } from '../types/api';

const API_BASE_URL = 'http://localhost:8042';

export async function getFiles(): Promise<FileResponse[]> {
    const response = await fetch(`${API_BASE_URL}/files/`);
    if (!response.ok) {
        throw new Error('Failed to fetch files.');
    }
    return response.json();
}

export async function getFileByPath(path: string): Promise<FileResponse> {
    const encodedPath = encodeURIComponent(path);
    const response = await fetch(`${API_BASE_URL}/files/path/${encodedPath}`);
    if (!response.ok) {
        throw new Error('File not found.');
    }
    return response.json();
}

export async function createFile(path: string, content: string): Promise<FileResponse> {
    const payload = { path, content };
    const response = await fetch(`${API_BASE_URL}/files/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error('Failed to create file.');
    }
    return response.json();
}

export async function updateFile(id: number, content: string): Promise<FileResponse> {
    const payload = { content };
    const response = await fetch(`${API_BASE_URL}/files/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error('Failed to update file.');
    }
    return response.json();
}
