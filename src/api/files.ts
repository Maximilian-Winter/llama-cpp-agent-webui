import type {FilePathResponse, FileResponse} from '../types/api';

const API_BASE_URL = 'http://localhost:8042';

export async function getFiles(): Promise<FileResponse[]> {
    const response = await fetch(`${API_BASE_URL}/files/`);
    if (!response.ok) {
        throw new Error('Failed to fetch files.');
    }
    return response.json();
}

export async function getFilePaths(): Promise<FilePathResponse[]> {
    const response = await fetch(`${API_BASE_URL}/file-paths/`);
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
    console.log('Sending payload:', payload);

    try {
        const response = await fetch(`${API_BASE_URL}/files/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const responseText = await response.text();
        console.log('Response status:', response.status);
        console.log('Response text:', responseText);

        if (!response.ok) {
            throw new Error(`Failed to create file. Status: ${response.status}, Response: ${responseText}`);
        }

        // Only parse as JSON if the response is OK
        return JSON.parse(responseText);
    } catch (error) {
        console.error('Error in createFile:', error);
        throw error;
    }
}

export async function updateFile(id: number, content: string): Promise<FileResponse> {
    const payload = { content: content };
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
