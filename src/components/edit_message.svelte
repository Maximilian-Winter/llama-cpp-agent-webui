<script lang="ts">
    import { createEventDispatcher } from 'svelte';

    export let message: string = '';
    export let id: number = 0;
    const dispatch = createEventDispatcher();

    function handleSave() {
        dispatch('save', { id: id, content: message });
    }

    function handleCancel() {
        dispatch('cancel');
    }
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="w-11/12 max-w-lg rounded-lg bg-[#161b22] p-6 shadow-lg">
        <h2 class="mb-4 text-xl font-bold text-slate-200">Edit Message</h2>
        <textarea
                class="mb-4 w-full rounded-md border border-slate-700 bg-[#0d1117] py-2 px-3 text-base text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                rows="4"
                placeholder="Enter your message"
                bind:value={message}
        ></textarea>
        <div class="flex justify-end space-x-2">
            <button
                    class="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition duration-200 ease-in-out hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    on:click={handleSave}
            >
                Save
            </button>
            <button
                    class="rounded-md bg-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition duration-200 ease-in-out hover:bg-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
                    on:click={handleCancel}
            >
                Cancel
            </button>
        </div>
    </div>
</div>