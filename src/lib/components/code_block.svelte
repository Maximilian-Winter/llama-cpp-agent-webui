<script lang="ts">
    import { onMount, afterUpdate, tick } from 'svelte';
    import DOMPurify from 'dompurify';
    import { marked } from 'marked';
    import hljs from 'highlight.js';


    export let content: string;

    let markdownContainer: HTMLElement;
    let processedContent = '';

    $: if (content) {
        console.log("Content changed, length:", content.length);
        processContent();
    }

    async function processContent() {
        console.log("Processing content");
        const markedContent = await marked(content);
        processedContent = DOMPurify.sanitize(markedContent);
        console.log("Processed content length:", processedContent.length);

        // We need to wait for the next tick to ensure the DOM is updated
        await tick();
        hljs.highlightAll();
    }


    function wrapCodeBlocks() {
        console.log("Wrapping code blocks");

        const codeBlocks = markdownContainer.querySelectorAll('pre > code');
        console.log("Found code blocks:", codeBlocks.length);

        codeBlocks.forEach((block, index) => {
            const pre = block.parentElement;
            if (pre) {
                // If the pre is already wrapped, unwrap it
                if (pre.parentElement?.classList.contains('code-block-wrapper')) {
                    const wrapper = pre.parentElement;
                    wrapper.remove();
                }

                // Always wrap the code block
                console.log(`Wrapping code block ${index}`);
                wrapCodeBlock(block as HTMLElement, pre as HTMLElement, index);
            } else {
                console.log(`Code block ${index} is invalid (no pre parent)`);
            }
        });

        hljs.highlightAll();
    }

    function wrapCodeBlock(block: HTMLElement, pre: HTMLElement, index: number) {
        let language = block.className.split('-')[1].replace("hljs", "") || 'plaintext';
        if (language === '') {
            language = 'plaintext';
        }
        const wrapper = document.createElement('div');
        wrapper.className = 'code-block-wrapper';

        const header = document.createElement('div');
        header.className = 'code-block-header';
        header.innerHTML = `
            <span>${language}</span>
            <button class="copy-button" data-index="${index}">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M8 2a1 1 0 000 2h2a1 1 0 100-2H8z" />
                    <path d="M3 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v6h-4.586l1.293-1.293a1 1 0 00-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L10.414 13H15v3a2 2 0 01-2 2H5a2 2 0 01-2-2V5zM15 11h2a1 1 0 110 2h-2v-2z" />
                </svg>
            </button>
        `;

        wrapper.appendChild(header);
        pre.parentNode?.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);

        const copyButton = header.querySelector('.copy-button');
        if (copyButton) {
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(block.textContent || '');
                copyButton.textContent = 'Copied!';
                setTimeout(() => {
                    copyButton.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M8 2a1 1 0 000 2h2a1 1 0 100-2H8z" />
                            <path d="M3 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v6h-4.586l1.293-1.293a1 1 0 00-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L10.414 13H15v3a2 2 0 01-2 2H5a2 2 0 01-2-2V5zM15 11h2a1 1 0 110 2h-2v-2z" />
                        </svg>
                    `;
                }, 2000);
            });
        }
    }

    onMount(() => {
        wrapCodeBlocks();
    });

    afterUpdate(() => {
        wrapCodeBlocks();
    });
</script>

<div class="markdown-content" bind:this={markdownContainer}>
    {@html processedContent}
</div>

<style>

    .markdown-content :global(.code-block-wrapper) {
        margin: 1rem 0;
        border-radius: 0.375rem;
        overflow: hidden;
        background-color: #0d1117;
    }

    .markdown-content :global(.code-block-header) {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 1rem;
        background-color: #374151;
        color: #e5e7eb;
        font-family: monospace;
    }

    .markdown-content :global(.copy-button) {
        background: none;
        border: none;
        cursor: pointer;
        color: #e5e7eb;
        display: flex;
        align-items: center;
    }

    .markdown-content :global(.copy-button:hover) {
        color: #60a5fa;
    }

    .markdown-content :global(pre) {
        margin: 0;
        padding: 1rem;
        overflow-x: auto;
    }

    .markdown-content :global(code) {
        font-family: monospace;
        font-size: 0.875rem;
        line-height: 1.25rem;
    }
</style>