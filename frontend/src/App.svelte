<script lang="ts">
  import Header from './components/Header.svelte';
  import Karts from './routes/Karts.svelte';
  import Teams from './routes/Teams.svelte';
  import KartDetails from './routes/KartDetails.svelte';
  import TeamDetails from './routes/TeamDetails.svelte';
  import Settings from './routes/Settings.svelte';
  
  // Simple routing
  let currentPath = window.location.pathname;
  let kartNumber = 5; // Default kart number for demo
  let teamId = 1; // Default team ID for demo
  
  // Update path when URL changes
  window.addEventListener('popstate', () => {
    currentPath = window.location.pathname;
    updateRouteParams();
  });
  
  // Function to navigate to a different route
  function navigate(path: string) {
    window.history.pushState({}, '', path);
    currentPath = path;
    updateRouteParams();
  }
  
  // Extract route parameters from the current path
  function updateRouteParams() {
    // Extract kart number from path like /kart-details/5
    if (currentPath.startsWith('/kart-details/')) {
      const match = currentPath.match(/\/kart-details\/(\d+)/);
      if (match && match[1]) {
        kartNumber = parseInt(match[1], 10);
      }
    }
    
    // Extract team ID from path like /team-detail/1
    if (currentPath.startsWith('/team-detail/')) {
      const match = currentPath.match(/\/team-detail\/(\d+)/);
      if (match && match[1]) {
        teamId = parseInt(match[1], 10);
      }
    }
  }
  
  // Initialize route parameters
  updateRouteParams();
  
  // Make navigate function available globally
  (window as any).appNavigate = navigate;
</script>

<main>
  <Header />
  <div class="content">
    {#if currentPath === '/' || currentPath === '/karts'}
      <Karts />
    {:else if currentPath === '/teams'}
      <Teams />
    {:else if currentPath.startsWith('/kart-details')}
      <KartDetails {kartNumber} />
    {:else if currentPath.startsWith('/team-detail')}
      <TeamDetails {teamId} />
    {:else if currentPath === '/settings'}
      <Settings />
    {:else}
      <h1>Page Not Found</h1>
      <p>The requested page does not exist.</p>
      <a href="/" on:click|preventDefault={() => navigate('/')}>Go to Home</a>
    {/if}
  </div>
</main>

<style>
  main {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }
  
  .content {
    padding: 1rem 0;
  }
</style>
