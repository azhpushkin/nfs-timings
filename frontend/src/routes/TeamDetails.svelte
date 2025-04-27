<script lang="ts">
  import { onMount } from 'svelte';
  import StintsTable from '../components/StintsTable.svelte';
  import { getTeamDetails, type Team, type Stint } from '../lib/api';
  
  export let teamId: number;
  
  let team: Team | null = null;
  let stints: Stint[] = [];
  let loading = true;
  let error = false;
  
  // Fetch team details from the API
  async function fetchTeamDetails() {
    try {
      loading = true;
      error = false;
      
      const data = await getTeamDetails(teamId);
      team = data.team;
      stints = data.stints;
      
      loading = false;
    } catch (err) {
      console.error('Error fetching team details:', err);
      error = true;
      loading = false;
    }
  }
  
  // Call the fetch function when the component is mounted
  onMount(() => {
    fetchTeamDetails();
  });
</script>

{#if loading}
  <div class="loading">Loading team details...</div>
{:else if error}
  <div class="error">
    <p>Error loading team details. Please try again later.</p>
    <button on:click={fetchTeamDetails}>Retry</button>
  </div>
{:else if team}
  <h3>{team.name} - # {team.number}</h3>
  <div style="font-size: 0.8em">Відрізки відсортовані від першого до останнього</div>
  <br>
  <StintsTable {stints} columns="PBSAL" />
{:else}
  <div class="error">Team not found</div>
{/if}

<style>
  .loading, .error {
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
  }
  
  .loading {
    background-color: #f0f0f0;
  }
  
  .error {
    background-color: #ffebee;
    color: #c62828;
  }
</style>
