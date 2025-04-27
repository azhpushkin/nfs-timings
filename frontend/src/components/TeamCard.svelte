<script lang="ts">
  import Kart from './Kart.svelte';
  import StintsTable from './StintsTable.svelte';
  
  export let team: {
    number: number;
    name: string;
    average_lap: string;
    pilots: string[];
    stints: any[];
  };
  
  let isExpanded = false;
  
  function toggleExpand() {
    isExpanded = !isExpanded;
  }
  
  function pilotSurname(pilot: string): string {
    // This is a placeholder - implement actual formatting logic
    return pilot;
  }
</script>

<div class="team-card">
  <div class="team-card-line" id="team-card-line-{team.number}">
    <div class="team-card-line-team">
      <div class="title" id="team-{team.number}-line">
        {team.name}
        <span style="color: gray; display: inline !important;"> #{team.number}</span>
        <br>
        <span style="font-size: 0.7em; color: gray;">Mid: {team.average_lap}</span>
      </div>
      <div class="pilot-names">
        {#each team.pilots as pilot, i}
          {pilotSurname(pilot)}
          {#if i < team.pilots.length - 1}<br>{/if}
        {/each}
      </div>
    </div>
    
    <div class="team-card-line-karts" id="team-card-line-karts-{team.number}">
      {#each team.stints as stint}
        <Kart number={stint.kart} nolink={true} />
      {/each}
    </div>
    
    <div class="team-card-line-link" class:collapsed={!isExpanded} id="team-card-line-link-{team.number}">
      <a href="/team-detail/{team.number}">
        <button>Перейти на сторінку команди</button>
      </a>
    </div>
  </div>
  
  <div class:collapsed={!isExpanded} id="stints-info-{team.number}">
    <StintsTable stints={team.stints} columns="PBAL" sortable={false} />
  </div>
  
  <button on:click={toggleExpand}>
    {isExpanded ? 'Hide details' : 'Show details'}
  </button>
</div>
