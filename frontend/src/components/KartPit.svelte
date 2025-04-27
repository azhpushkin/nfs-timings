<script lang="ts">
  import Kart from './Kart.svelte';
  
  export let kartNumber: number;
  export let highlighted: boolean = false;
  export let errorMsg: string | null = null;
  
  function handleClick() {
    // In a real app, this would fetch kart details
    // and update the kart-details element
    const event = new CustomEvent('kart-selected', {
      detail: { kartNumber }
    });
    document.dispatchEvent(event);
  }
</script>

{#if !errorMsg}
  <span 
    class="kart-on-pit-v2 {highlighted ? 'highlighted-on-pit' : ''}"
    on:click={handleClick}
  >
    <Kart number={kartNumber} nolink={true} inline={true} />
  </span>
  ←
{/if}

{#if errorMsg}
  <div id="kart-add-error">
    {errorMsg}
  </div>
{/if}

<style>
  .kart-on-pit-v2 {
    cursor: pointer;
  }
  
  .highlighted-on-pit :global(.kart-number) {
    box-shadow: 0 0 5px 5px gold;
  }
  
  #kart-add-error {
    border: 1px solid red;
    border-radius: 5px;
    background-color: #ffaaaa;
    text-align: center;
    padding: 5px;
    margin: 10px;
  }
</style>
