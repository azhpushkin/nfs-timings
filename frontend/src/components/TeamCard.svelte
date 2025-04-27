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
  
  function navigateToTeamDetail() {
    if (typeof window !== 'undefined' && (window as any).appNavigate) {
      (window as any).appNavigate(`/team-detail/${team.number}`);
    }
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
      <a href="/team-detail/{team.number}" on:click|preventDefault={navigateToTeamDetail}>
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

<style>
  .team-card {
    border: 1px solid gray;
    border-radius: 10px;
    margin-bottom: 10px;
    padding: 10px 5px;
  }
  
  .team-card-line {
    padding-left: 10px;
    padding-right: 10px;
  }
  
  .team-card-line-team {
    display: flex;
    justify-content: space-between;
    align-content: center;
  }
  
  .team-card-line-team .title {
    font-weight: bold;
    font-size: 1.1em;
  }
  
  .team-card-line-team .pilot-names {
    font-size: 0.8em;
    text-align: right;
  }
  
  .team-card-line-karts {
    margin-top: 10px;
    display: flex;
    gap: 0.4em;
  }
  
  .collapsed {
    display: none;
  }
</style>
