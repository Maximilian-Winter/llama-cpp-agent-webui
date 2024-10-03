<script lang="ts">
    export let files: string[] = [];

    interface TreeNode {
        name: string;
        type: 'file' | 'folder';
        children: TreeNode[];
    }

    function buildTree(paths: string[]): TreeNode[] {
        const root: TreeNode[] = [];

        for (const path of paths) {
            const parts = path.split('/');
            let currentLevel = root;

            for (let i = 0; i < parts.length; i++) {
                const part = parts[i];
                const isFile = i === parts.length - 1;
                let existingNode = currentLevel.find(node => node.name === part);

                if (!existingNode) {
                    const newNode: TreeNode = {
                        name: part,
                        type: isFile ? 'file' : 'folder',
                        children: [],
                    };
                    currentLevel.push(newNode);
                    existingNode = newNode;
                }

                if (!isFile) {
                    currentLevel = existingNode.children;
                }
            }
        }

        return root;
    }

    $: tree = buildTree(files);

    function getFileIcon(name: string) {
        const extension = name.split('.').pop()?.toLowerCase();
        switch (extension) {
            case 'pdf':
                return 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z';
            case 'png':
            case 'jpg':
            case 'jpeg':
            case 'gif':
                return 'M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z';
            default:
                return 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z';
        }
    }
</script>

{#if tree.length > 0}
    <ul class="menu menu-xs bg-base-200 rounded-lg w-full max-w-xs">
        {#each tree as node}
            <svelte:self node={node} />
        {/each}
    </ul>
{:else}
    <li>
        {#if $$props.node}
            {#if $$props.node.type === 'file'}
                <a>
                    <svg
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke-width="1.5"
                            stroke="currentColor"
                            class="h-4 w-4">
                        <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                d={getFileIcon($$props.node.name)}
                        />
                    </svg>
                    {$$props.node.name}
                </a>
            {:else}
                <details open>
                    <summary>
                        <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke-width="1.5"
                                stroke="currentColor"
                                class="h-4 w-4">
                            <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z"
                            />
                        </svg>
                        {$$props.node.name}
                    </summary>
                    {#if $$props.node.children.length > 0}
                        <ul>
                            {#each $$props.node.children as childNode}
                                <svelte:self node={childNode} />
                            {/each}
                        </ul>
                    {/if}
                </details>
            {/if}
        {/if}
    </li>
{/if}