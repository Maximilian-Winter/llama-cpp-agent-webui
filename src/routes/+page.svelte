<script lang="ts">
    import { goto } from '$app/navigation';
    import { ChevronRight } from 'lucide-svelte';

    async function _goto(url: string): Promise<void> {
        await goto(url);
    }

    const features = [
        { title: 'Start Chatting', description: 'Begin a conversation with an AI agent', url: '/chat', icon: '💬' },
        { title: 'Select an Agent', description: 'Choose from a variety of specialized AI agents', url: '/agent-selection', icon: '🤖' },
        { title: 'Create a New Agent', description: 'Design and configure your own custom AI agent', url: '/agent-creation', icon: '🛠️' },
        { title: 'File Management', description: 'Organize and manage your documents and files', url: '/file-management', icon: '📁' },
    ];
</script>

<div class="flex min-h-screen w-full bg-[#0d1117] text-slate-300">
    <div class="max-w-4xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
        <div class="text-center">
            <h1 class="text-4xl font-extrabold sm:text-5xl md:text-6xl">
                Welcome to <span class="text-blue-500">OpenAgent WebUI</span>
            </h1>
            <p class="mt-3 text-xl text-slate-400 sm:mt-4">
                Your gateway to intelligent conversations and AI-powered assistance
            </p>
        </div>

        <div class="mt-16 grid gap-8 sm:grid-cols-2">
            {#each features as feature}
                <div class="relative group">
                    <div class="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg blur opacity-25 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
                    <button
                            class="relative flex items-center space-x-4 px-7 py-4 bg-[#1c2128] rounded-lg leading-none w-full transition duration-200 hover:text-white hover:bg-[#2c3138]"
                            on:click={() => _goto(feature.url)}
                    >
                        <span class="flex items-center justify-center w-14 h-14 bg-[#0d1117] rounded-full text-3xl">
                            {feature.icon}
                        </span>
                        <span class="flex flex-col items-start text-left">
                            <span class="text-xl font-semibold">{feature.title}</span>
                            <span class="text-slate-400 group-hover:text-slate-300">{feature.description}</span>
                        </span>
                        <ChevronRight class="ml-auto" size={24} />
                    </button>
                </div>
            {/each}
        </div>

        <div class="mt-16 text-center">
            <p class="text-slate-400">
                Powered by advanced language models and cutting-edge AI technology
            </p>
        </div>
    </div>
</div>

<style>
    :global(body) {
        @apply bg-[#0d1117] text-slate-300;
    }
</style>