<script>
    import { onMount } from 'svelte';
    import ImageGallery from './ImageGallery.svelte';

    const resolutions = [
        '1-1.png',
        '9-7.png',
        '7-9.png',
        '19-13.png',
        '13-19.png',
        '7-4.png',
        '4-7.png',
        '12-5.png',
        '5-12.png'
    ];

    let images = [];

    function addTestImage() {
        const randomResolution = resolutions[Math.floor(Math.random() * resolutions.length)];
        const url = `${randomResolution}`;
        images = [...images, url];
    }
</script>

<main class="p-8 max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-4">Image Gallery Demo</h1>
    <button
        on:click={addTestImage}
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 mb-8"
    >
        Add Test Image
    </button>

    <ImageGallery gap={16} maxColumnWidth={200} hover={true} loading="lazy">
        {#each images as img}
            <img src={img} alt="Test Image" />
        {/each}
    </ImageGallery>
</main>

<style>
    main {
        font-family: 'Inter', sans-serif;
    }
</style>
