<script lang="ts">
    // Define the type for individual panels
    import {onMount} from "svelte";

    type Panel = {
        id: number;
        name: string;
        instructions: string;
    };

    // Sample data for panels
    let panels: Panel[] = [];

    async function fetchPanelData(): Promise<Panel[]> {
        const response = await fetch('http://localhost:8000/agents/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    onMount(() => {
        fetchPanelData()
            .then(data => {
                panels = data;
            })
            .catch(error => {
                console.error('Failed to fetch panels:', error);
            });
    });
</script>

<style>
    .panel {
        border: 1px solid #767575;
        padding: 15px;
        background-color: #2b2929; /* Light grey background */
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); /* Subtle shadow for depth */
    }
</style>
<div class="flex h-[97vh] w-full flex-col">
    <div
            class="mt-20 ml-20 mr-20 flex-1 overflow-y-auto bg-[#0d1117] text-sm leading-6 text-slate-900 shadow-md dark:bg-[#0d1117] dark:text-slate-300 sm:text-base sm:leading-7"
    >
        <div class="grid grid-cols-4 gap-4">
            {#each panels as { id, name, instructions }}
                <div class="panel">
                    <h2>{name}</h2>
                    <p>{instructions}</p>
                </div>
            {/each}
        </div>
    </div>
</div>