<script lang="ts">
  import { onMount } from 'svelte';
  import TeamCard from '../components/TeamCard.svelte';
  import { getTeams, type Team } from '../lib/api';
  
  let teams: Team[] = [];
  let loading = true;
  let error = false;
  
  // Fetch teams from the API
  async function fetchTeams() {
    try {
      loading = true;
      error = false;
      
      teams = await getTeams();
      
      loading = false;
    } catch (err) {
      console.error('Error fetching teams:', err);
      error = true;
      loading = false;
    }
  }
  
  // Call the fetch function when the component is mounted
  onMount(() => {
    fetchTeams();
  });
</script>

<h2>Teams</h2>

{#if loading}
  <div class="loading">Loading teams...</div>
{:else if error}
  <div class="error">
    <p>Error loading teams. Please try again later.</p>
    <button on:click={fetchTeams}>Retry</button>
  </div>
{:else if teams.length === 0}
  <div class="empty">No teams found</div>
{:else}
  {#each teams as team}
    <TeamCard {team} />
  {/each}
{/if}

<style>
  .loading, .error, .empty {
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
  
  .empty {
    background-color: #e8f5e9;
    color: #2e7d32;
  }
</style>
