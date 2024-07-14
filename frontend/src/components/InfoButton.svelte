<!-- src/components/InfoModal.svelte -->
<script>
  let showModal = false;

  function toggleModal() {
    showModal = !showModal;
  }
</script>

<div class="fixed bottom-2 right-2">
  {#if !showModal}
    <button
      on:click={toggleModal}
      class="bg-indigo-600 text-white w-8 h-8 rounded-full shadow-md flex items-center justify-center"
    >
      <i class="ri-information-line text-xl"></i>
    </button>
  {/if}

  {#if showModal}
    <div class="fixed bottom-2 right-2 bg-white rounded-md shadow-lg p-4 w-72 relative">
      <button 
        class="absolute top-2 right-2 text-gray-500 hover:text-gray-700" 
        on:click={toggleModal}
      ><i class="ri-close-circle-line text-xl"></i></button>
      <slot></slot>
    </div>
  {/if}
</div>
