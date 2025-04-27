<script lang="ts">
  export let columns: {
    pilot: boolean;
    best: boolean;
    sectors: boolean;
    average: boolean;
    link: boolean;
  };
  export let sorting: string = 'best';
  
  function getSortUrl(sortType: string): string {
    // In a real app, this would update the URL with the sort parameter
    return `?sort=${sortType}`;
  }
</script>

<thead>
  <tr>
    <th class="kart-number-cell {sorting === 'kart' ? 'selected-sorting' : ''}">
      <a href={getSortUrl('kart')}>#</a>
    </th>
    
    {#if columns.pilot}
      <th class="pilot-name {sorting === 'latest_first' || !sorting ? 'selected-sorting' : ''}">
        <a href={getSortUrl('latest_first')}>Stint</a>
      </th>
    {/if}
    
    {#if columns.best}
      <th class={sorting === 'best' ? 'selected-sorting' : ''}>
        <a href={getSortUrl('best')}>Best</a>
      </th>
    {/if}
    
    {#if columns.sectors}
      {#if sorting === 'sector_1'}
        <th class="selected-sorting">
          <a href={getSortUrl('sector_2')}>by S1</a>
        </th>
      {:else if sorting === 'sector_2'}
        <th class="selected-sorting">
          <a href={getSortUrl('sector_1')}>by S2</a>
        </th>
      {:else}
        <th>
          <a href={getSortUrl('sector_1')}>Sec</a>
        </th>
      {/if}
    {/if}
    
    {#if columns.average}
      <th class={sorting === 'average' ? 'selected-sorting' : ''}>
        <a href={getSortUrl('average')}>Avg</a>
      </th>
    {/if}
    
    {#if columns.link}
      <th class="stint-link"></th>
    {/if}
  </tr>
</thead>
