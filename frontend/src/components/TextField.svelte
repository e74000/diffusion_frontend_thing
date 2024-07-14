<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';

  export let label = '';
  export let value = '';
  export let placeholder = '';
  export let id = '';
  export let autocompleteFunction;

  let suggestions = writable([]);
  let textarea;

  async function handleInput(event) {
    resizeTextarea(textarea);
    const query = event.target.value.split(',').pop().trim();
    if (query.length > 0) {
      const data = await autocompleteFunction(query);
      suggestions.set(data.suggestions);
    } else {
      suggestions.set([]);
    }
  }

  function selectSuggestion(suggestion) {
    const tags = value.split(',').map(tag => tag.trim());
    tags[tags.length - 1] = suggestion;
    value = tags.join(', ') + ', ';
    resizeTextarea(textarea);
    suggestions.set([]);
  }

  function resizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' && $suggestions.length > 0) {
      event.preventDefault();
      selectSuggestion($suggestions[0]);
    }
  }

  function handleBlur() {
    // Hide suggestions on blur after a short delay to allow click events to process
    setTimeout(() => suggestions.set([]), 100);
  }

  onMount(() => {
    resizeTextarea(textarea);
  });

  $: if (textarea) {
    resizeTextarea(textarea);
  }
</script>

<div>
  <label for={id} class="block text-sm font-medium text-gray-700">{label}</label>
  <textarea 
    bind:this={textarea} 
    id={id} 
    bind:value={value} 
    rows="1" 
    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2 resize-none overflow-hidden" 
    placeholder={placeholder} 
    on:input={handleInput} 
    on:keydown={handleKeyDown}
    on:blur={handleBlur}/>
  {#if $suggestions.length > 0}
    <ul class="border border-solid border-gray-300 rounded-md absolute z-10 max-h-48 overflow-y-auto max-w-xl bg-white my-1 mx-0 w-full">
      {#each $suggestions as suggestion}
        <li 
          class="suggestion-item p-2 cursor-pointer bg-white hover:bg-gray-100 m-1 rounded-md" 
          on:click={() => selectSuggestion(suggestion)}>
          {suggestion}
        </li>
        <hr class="mx-2">
      {/each}
    </ul>
  {/if}
</div>
