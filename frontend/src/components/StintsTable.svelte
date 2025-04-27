<script lang="ts">
  import Kart from './Kart.svelte';
  import StintsTableHeader from './StintsTableHeader.svelte';
  
  export let stints: any[] = [];
  export let columns: string = 'PBSAL';
  export let sortable: boolean = false;
  export let sorting: string = 'best';
  
  // Parse columns
  $: parsedColumns = {
    pilot: columns.includes('P'),
    best: columns.includes('B'),
    sectors: columns.includes('S'),
    average: columns.includes('A'),
    link: columns.includes('L')
  };
  
  // Format functions
  function formatRaceTime(time: string): string {
    // This is a placeholder - implement actual formatting logic
    return time;
  }
  
  function pilotSurname(pilot: string): string {
    // This is a placeholder - implement actual formatting logic
    return pilot;
  }
  
  function round(value: number, decimals: number = 2): string {
    return value.toFixed(decimals);
  }
</script>

<table class="stints">
  {#if sortable}
    <StintsTableHeader columns={parsedColumns} {sorting} />
  {:else}
    <thead>
      <tr>
        <th class="kart-number-cell">#</th>
        {#if parsedColumns.pilot}<th class="pilot-name">Stint</th>{/if}
        {#if parsedColumns.best}<th>Best</th>{/if}
        {#if parsedColumns.sectors}<th>Sec</th>{/if}
        {#if parsedColumns.average}<th>Avg</th>{/if}
        {#if parsedColumns.link}<th class="stint-link"></th>{/if}
      </tr>
    </thead>
  {/if}
  
  <tbody>
    {#each stints as stint}
      <tr>
        <td class="kart-number-cell">
          <Kart number={stint.kart} />
        </td>
        
        {#if parsedColumns.pilot}
          <td class="pilot-name">
            {pilotSurname(stint.pilot)}
            <br>
            <span class="stint-timeframe">⏰ {formatRaceTime(stint.stint_started_at)}</span>
          </td>
        {/if}
        
        {#if parsedColumns.best}
          <td class="best">{round(stint.best_lap)}</td>
        {/if}
        
        {#if parsedColumns.sectors}
          <td>
            <span class="sector_1">{round(stint.best_sector_1)}</span>
            <br>
            <span class="sector_2">{round(stint.best_sector_2)}</span>
          </td>
        {/if}
        
        {#if parsedColumns.average}
          <td class="average">{round(stint.avg_80)}</td>
        {/if}
        
        {#if parsedColumns.link}
          <td class="stint-link">
            <a href="/stint-detail/{stint.stint_id}">🔗</a>
          </td>
        {/if}
      </tr>
    {/each}
  </tbody>
</table>
