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

        await tick();
        hljs.highlightAll();
    }

    function getLanguageIcon(language: string): string {
        switch (language.toLowerCase()) {
            case 'c':
                return `<svg xmlns="http://www.w3.org/2000/svg" width="3em" height="3em" viewBox="0 0 64 64"><path fill="#005f91" d="M23 19.418a6.971 6.971 0 1 1-.05-6.918l6.093-3.509a14 14 0 1 0 .036 13.95Z"/></svg>`;
            case 'cpp':
                return `<svg xmlns="http://www.w3.org/2000/svg" width="3em" height="3em" viewBox="0 0 64 64"><path fill="#005f91" d="M26.914 13.8v1.54h-1.542v1.543h1.542v1.543h1.543v-1.543H30V15.34h-1.543V13.8Zm-3.5 0H21.87v1.54h-1.543v1.543h1.543v1.543h1.543v-1.543h1.543V15.34h-1.543Zm-3.654 5.226a6.167 6.167 0 1 1-.04-6.118l5.39-3.1a12.384 12.384 0 1 0 .032 12.34Z"/></svg>`;
            case 'react':
                return `<svg xmlns="http://www.w3.org/2000/svg" width="3em" height="3em" viewBox="0 0 64 64"><circle cx="16" cy="15.974" r="2.5" fill="#007acc"/><path fill="#007acc" d="M16 21.706a28.4 28.4 0 0 1-8.88-1.2a11.3 11.3 0 0 1-3.657-1.958A3.54 3.54 0 0 1 2 15.974c0-1.653 1.816-3.273 4.858-4.333A28.8 28.8 0 0 1 16 10.293a28.7 28.7 0 0 1 9.022 1.324a11.4 11.4 0 0 1 3.538 1.866A3.4 3.4 0 0 1 30 15.974c0 1.718-2.03 3.459-5.3 4.541a28.8 28.8 0 0 1-8.7 1.191m0-10.217a28 28 0 0 0-8.749 1.282c-2.8.977-4.055 2.313-4.055 3.2c0 .928 1.349 2.387 4.311 3.4A27.2 27.2 0 0 0 16 20.51a27.6 27.6 0 0 0 8.325-1.13C27.4 18.361 28.8 16.9 28.8 15.974a2.33 2.33 0 0 0-1.01-1.573a10.2 10.2 0 0 0-3.161-1.654A27.5 27.5 0 0 0 16 11.489"/><path fill="#007acc" d="M10.32 28.443a2.64 2.64 0 0 1-1.336-.328c-1.432-.826-1.928-3.208-1.327-6.373a28.8 28.8 0 0 1 3.4-8.593a28.7 28.7 0 0 1 5.653-7.154a11.4 11.4 0 0 1 3.384-2.133a3.4 3.4 0 0 1 2.878 0c1.489.858 1.982 3.486 1.287 6.859a28.8 28.8 0 0 1-3.316 8.133a28.4 28.4 0 0 1-5.476 7.093a11.3 11.3 0 0 1-3.523 2.189a4.9 4.9 0 0 1-1.624.307m1.773-14.7a28 28 0 0 0-3.26 8.219c-.553 2.915-.022 4.668.75 5.114c.8.463 2.742.024 5.1-2.036a27.2 27.2 0 0 0 5.227-6.79a27.6 27.6 0 0 0 3.181-7.776c.654-3.175.089-5.119-.713-5.581a2.33 2.33 0 0 0-1.868.089A10.2 10.2 0 0 0 17.5 6.9a27.5 27.5 0 0 0-5.4 6.849Z"/><path fill="#007acc" d="M21.677 28.456c-1.355 0-3.076-.82-4.868-2.361a28.8 28.8 0 0 1-5.747-7.237a28.7 28.7 0 0 1-3.374-8.471a11.4 11.4 0 0 1-.158-4A3.4 3.4 0 0 1 8.964 3.9c1.487-.861 4.01.024 6.585 2.31a28.8 28.8 0 0 1 5.39 6.934a28.4 28.4 0 0 1 3.41 8.287a11.3 11.3 0 0 1 .137 4.146a3.54 3.54 0 0 1-1.494 2.555a2.6 2.6 0 0 1-1.315.324m-9.58-10.2a28 28 0 0 0 5.492 6.929c2.249 1.935 4.033 2.351 4.8 1.9c.8-.465 1.39-2.363.782-5.434A27.2 27.2 0 0 0 19.9 13.74a27.6 27.6 0 0 0-5.145-6.64c-2.424-2.152-4.39-2.633-5.191-2.169a2.33 2.33 0 0 0-.855 1.662a10.2 10.2 0 0 0 .153 3.565a27.5 27.5 0 0 0 3.236 8.1Z"/></svg>`;
            case 'javascript':
            case 'js':
                return `<svg xmlns="http://www.w3.org/2000/svg" width="3em" height="3em" viewBox="0 0 64 64"><path fill="#f5de19" d="M2 2h28v28H2z"/><path d="M20.809 23.875a2.87 2.87 0 0 0 2.6 1.6c1.09 0 1.787-.545 1.787-1.3c0-.9-.716-1.222-1.916-1.747l-.658-.282c-1.9-.809-3.16-1.822-3.16-3.964c0-1.973 1.5-3.476 3.853-3.476a3.89 3.89 0 0 1 3.742 2.107L25 18.128A1.79 1.79 0 0 0 23.311 17a1.145 1.145 0 0 0-1.259 1.128c0 .789.489 1.109 1.618 1.6l.658.282c2.236.959 3.5 1.936 3.5 4.133c0 2.369-1.861 3.667-4.36 3.667a5.06 5.06 0 0 1-4.795-2.691Zm-9.295.228c.413.733.789 1.353 1.693 1.353c.864 0 1.41-.338 1.41-1.653v-8.947h2.631v8.982c0 2.724-1.6 3.964-3.929 3.964a4.085 4.085 0 0 1-3.947-2.4Z"/></svg>`;
            case 'typescript':
            case 'ts':
                return `<svg xmlns="http://www.w3.org/2000/svg" width="3em" height="3em" viewBox="0 0 64 64"><rect width="28" height="28" x="2" y="2" fill="#3178c6" rx="1.312"/><path fill="#fff" fill-rule="evenodd" d="M18.245 23.759v3.068a6.5 6.5 0 0 0 1.764.575a11.6 11.6 0 0 0 2.146.192a10 10 0 0 0 2.088-.211a5.1 5.1 0 0 0 1.735-.7a3.54 3.54 0 0 0 1.181-1.266a4.47 4.47 0 0 0 .186-3.394a3.4 3.4 0 0 0-.717-1.117a5.2 5.2 0 0 0-1.123-.877a12 12 0 0 0-1.477-.734q-.6-.249-1.08-.484a5.5 5.5 0 0 1-.813-.479a2.1 2.1 0 0 1-.516-.518a1.1 1.1 0 0 1-.181-.618a1.04 1.04 0 0 1 .162-.571a1.4 1.4 0 0 1 .459-.436a2.4 2.4 0 0 1 .726-.283a4.2 4.2 0 0 1 .956-.1a6 6 0 0 1 .808.058a6 6 0 0 1 .856.177a6 6 0 0 1 .836.3a4.7 4.7 0 0 1 .751.422V13.9a7.5 7.5 0 0 0-1.525-.4a12.4 12.4 0 0 0-1.9-.129a8.8 8.8 0 0 0-2.064.235a5.2 5.2 0 0 0-1.716.733a3.66 3.66 0 0 0-1.171 1.271a3.73 3.73 0 0 0-.431 1.845a3.6 3.6 0 0 0 .789 2.34a6 6 0 0 0 2.395 1.639q.63.26 1.175.509a6.5 6.5 0 0 1 .942.517a2.5 2.5 0 0 1 .626.585a1.2 1.2 0 0 1 .23.719a1.1 1.1 0 0 1-.144.552a1.3 1.3 0 0 1-.435.441a2.4 2.4 0 0 1-.726.292a4.4 4.4 0 0 1-1.018.105a5.8 5.8 0 0 1-1.969-.35a5.9 5.9 0 0 1-1.805-1.045m-5.154-7.638h4v-2.527H5.938v2.527H9.92v11.254h3.171Z"/></svg>`;
            default:
                return `<svg xmlns="http://www.w3.org/2000/svg" width="3em" height="3em" viewBox="0 0 64 64"><path fill="#56b3b4" d="M21.714 8.571h1.143a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-1.143a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571"/><path fill="#ea5e5e" d="M4.571 26.857h5.714a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H4.571a.57.57 0 0 1-.571-.57a.57.57 0 0 1 .571-.572"/><path fill="#bf85bf" d="M18.286 17.714h3.429a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-3.429a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571"/><path fill="#ea5e5e" d="M11.429 17.714H16a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-4.571a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571"/><path fill="#56b3b4" d="M4.571 17.714h4.572a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H4.571a.57.57 0 0 1-.571-.57a.57.57 0 0 1 .571-.572"/><path fill="#bf85bf" d="M4.571 22.286h5.714a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H4.571A.57.57 0 0 1 4 22.857a.57.57 0 0 1 .571-.571m0-9.143h5.714a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H4.571A.57.57 0 0 1 4 13.714a.57.57 0 0 1 .571-.571"/><path fill="#f7ba3e" d="M10.286 6.286h11.428a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H10.286a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571"/><path fill="#ea5e5e" d="M4.571 6.286H8a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.572H4.571A.57.57 0 0 1 4 6.857a.57.57 0 0 1 .571-.571"/><path fill="#f7ba3e" d="M9.143 24.571h1.143a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H9.143a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571"/><path fill="#56b3b4" d="M9.143 10.857h1.143a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H9.143a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571M4.571 24.571h2.286a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H4.571a.57.57 0 0 1-.571-.57a.57.57 0 0 1 .571-.572"/><path fill="#f7ba3e" d="M4.571 10.857h2.286a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.572H4.571A.57.57 0 0 1 4 11.429a.57.57 0 0 1 .571-.572"/><path fill="#d0d4d8" d="M19.429 24.571h1.143a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-1.143a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571m-6.858 0h4.571a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-4.571a.57.57 0 0 1-.571-.57a.57.57 0 0 1 .571-.572m10.286 0h4.571a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-4.571a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571" opacity="0.5"/><path fill="#56b3b4" d="M13.714 15.429h9.143a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-9.143a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571"/><path fill="#f7ba3e" d="M8 15.429h3.429A.57.57 0 0 1 12 16a.57.57 0 0 1-.571.571H8A.57.57 0 0 1 7.429 16A.57.57 0 0 1 8 15.429"/><path fill="#ea5e5e" d="M4.571 15.429h1.143a.57.57 0 0 1 .572.571a.57.57 0 0 1-.571.571H4.571A.57.57 0 0 1 4 16a.57.57 0 0 1 .571-.571"/><path fill="#bf85bf" d="M14.857 8.571h4.571a.57.57 0 0 1 .572.572a.57.57 0 0 1-.571.571h-4.572a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.572"/><path fill="#56b3b4" d="M4.571 8.571h8a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-8A.57.57 0 0 1 4 9.143a.57.57 0 0 1 .571-.572"/><path fill="#f7ba3e" d="M8 20h10.286a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H8a.57.57 0 0 1-.571-.571A.57.57 0 0 1 8 20"/><path fill="#bf85bf" d="M4.571 20h1.143a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H4.571A.57.57 0 0 1 4 20.571A.57.57 0 0 1 4.571 20"/><path fill="#ea5e5e" d="M18.286 10.857H24a.57.57 0 0 1 .571.571A.57.57 0 0 1 24 12h-5.714a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.572"/><path fill="#f7ba3e" d="M18.286 13.143H24a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-5.714a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571"/><path fill="#56b3b4" d="M4.571 4h13.715a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H4.571A.57.57 0 0 1 4 4.571A.57.57 0 0 1 4.571 4"/><path fill="#d0d4d8" d="M20.571 4h6.857a.57.57 0 0 1 .572.571a.57.57 0 0 1-.571.571h-6.858A.57.57 0 0 1 20 4.571A.57.57 0 0 1 20.571 4m0 16h2.286a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-2.286a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571m4.572 0h2.286a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-2.286a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571M24 17.714h3.429a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H24a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571m0-11.428h3.429a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H24a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571m1.143 9.143h2.286A.57.57 0 0 1 28 16a.57.57 0 0 1-.571.571h-2.286a.57.57 0 0 1-.572-.571a.57.57 0 0 1 .572-.571m0-6.858h2.286a.57.57 0 0 1 .571.572a.57.57 0 0 1-.571.571h-2.286a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.572m1.143 2.286h1.143a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-1.143a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571m0 2.286h1.143a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-1.143a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571m-9.143 9.143h10.286a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571H17.143a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571m-4.572 0h2.286a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-2.286a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571m9.143 4.571h5.714a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-5.714a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571m-9.143 0h6.857a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-6.857a.57.57 0 0 1-.571-.57a.57.57 0 0 1 .571-.572m0-16H16a.57.57 0 0 1 .571.571A.57.57 0 0 1 16 12h-3.429a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.572m0 2.286H16a.57.57 0 0 1 .571.571a.57.57 0 0 1-.571.571h-3.429a.57.57 0 0 1-.571-.571a.57.57 0 0 1 .571-.571" opacity="0.5"/></svg>`;
        }
    }

    function wrapCodeBlocks() {
        console.log("Wrapping code blocks");

        const codeBlocks = markdownContainer.querySelectorAll('pre > code');
        console.log("Found code blocks:", codeBlocks.length);

        codeBlocks.forEach((block, index) => {
            const pre = block.parentElement;
            if (pre) {
                if (pre.parentElement?.classList.contains('code-block-wrapper')) {
                    const wrapper = pre.parentElement;
                    wrapper.remove();
                }

                console.log(`Wrapping code block ${index}`);
                wrapCodeBlock(block as HTMLElement, pre as HTMLElement, index);
            } else {
                console.log(`Code block ${index} is invalid (no pre parent)`);
            }
        });

        hljs.highlightAll();
    }

    function wrapCodeBlock(block: HTMLElement, pre: HTMLElement, index: number) {
        let language = block.className.split('-')[1]?.replace("hljs", "").trim() || 'plaintext';
        if (language === '') {
            language = 'plaintext';
        }
        const wrapper = document.createElement('div');
        wrapper.className = 'code-block-wrapper';

        const header = document.createElement('div');
        header.className = 'code-block-header';
        header.innerHTML = `
            <div class="language-info">
                <span class="language-icon">${getLanguageIcon(language)}</span>
                <span>${language}</span>
            </div>
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
        border: 2px solid #30363d;
    }

    .markdown-content :global(.code-block-header) {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 1rem;
        background-color: #161b22;
        color: #c9d1d9;
        font-family: monospace;
        border-bottom: 2px solid #30363d;
    }

    .markdown-content :global(.language-info) {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .markdown-content :global(.language-icon) {
        width: 16px;
        height: 16px;
        margin-bottom: 0.5rem;
        margin-right: 0.5rem;
    }

    .markdown-content :global(.copy-button) {
        background: none;
        border: none;
        cursor: pointer;
        color: #c9d1d9;
        display: flex;
        align-items: center;
    }

    .markdown-content :global(.copy-button:hover) {
        color: #58a6ff;
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