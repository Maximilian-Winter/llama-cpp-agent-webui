<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { fade } from 'svelte/transition';
    import { X } from 'lucide-svelte';

    export let title = 'Confirm Action';
    export let message = 'Are you sure you want to perform this action?';
    export let confirmText = 'Confirm';
    export let cancelText = 'Cancel';
    export let confirmButtonClass = 'bg-red-600 hover:bg-red-700';

    const dispatch = createEventDispatcher();

    function confirm() {
        dispatch('confirm');
        close();
    }

    function cancel() {
        dispatch('cancel');
        close();
    }

</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" transition:fade>
    <div class="bg-[#1c2128] rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="flex justify-between items-center border-b border-gray-700 p-4">
            <h2 class="text-xl font-semibold text-slate-200">{title}</h2>
            <button on:click={close} class="text-slate-400 hover:text-slate-200">
                <X size={24} />
            </button>
        </div>
        <div class="p-4">
            <p class="text-slate-300 mb-4">{message}</p>
            <div class="flex justify-end space-x-3">
                <button
                        on:click={cancel}
                        class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                >
                    {cancelText}
                </button>
                <button
                        on:click={confirm}
                        class="px-4 py-2 text-white rounded transition-colors {confirmButtonClass}"
                >
                    {confirmText}
                </button>
            </div>
        </div>
    </div>
</div>