<script>
    import { onMount, onDestroy, createEventDispatcher } from "svelte";
    import { tick } from "svelte";

    export let gap = 10;
    export let maxColumnWidth = 250;
    export let hover = false;
    export let loading;

    const dispatch = createEventDispatcher();

    let slotHolder = null;
    let columns = [];
    let galleryWidth = 0;
    let columnCount = 0;
    let observer;

    $: columnCount = parseInt(galleryWidth / maxColumnWidth) || 1;
    $: columnCount && Draw();
    $: galleryStyle = `grid-template-columns: repeat(${columnCount}, 1fr); gap: ${gap}px`;

    onMount(() => {
        Draw();
        observer = new MutationObserver(Draw);
        observer.observe(slotHolder, { childList: true });
    });

    onDestroy(() => {
        observer.disconnect();
    });

    function HandleClick(e) {
        dispatch("click", { src: e.target.src, alt: e.target.alt, loading: e.target.loading, class: e.target.className });
    }

    async function Draw() {
        await tick();

        if (!slotHolder) {
            return;
        }

        const images = Array.from(slotHolder.childNodes).filter(
            (child) => child.tagName === "IMG"
        );
        columns = [];

        // Fill the columns with image URLs
        for (let i = 0; i < images.length; i++) {
            const idx = i % columnCount;
            columns[idx] = [
                ...(columns[idx] || []),
                { src: images[i].src, alt: images[i].alt, class: images[i].className },
            ];
        }
    }
</script>

<div
    id="slotHolder"
    bind:this={slotHolder}
    class="hidden"
>
    <slot />
</div>

{#if columns}
    <div id="gallery" bind:clientWidth={galleryWidth} class="grid w-full mt-4" style={galleryStyle}>
        {#each columns as column}
            <div class="flex flex-col">
                {#each column as img}
                    <img
                        src={img.src}
                        alt={img.alt}
                        on:click={HandleClick}
                        class="{img.class} w-full mb-4 rounded-md shadow-md"
                        loading={loading}
                    />
                {/each}
            </div>
        {/each}
    </div>
{/if}
