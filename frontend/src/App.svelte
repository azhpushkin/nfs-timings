<script lang="ts">
  import Header from './components/Header.svelte';
  import Karts from './routes/Karts.svelte';
  import Teams from './routes/Teams.svelte';
  import KartDetails from './routes/KartDetails.svelte';
  import Settings from './routes/Settings.svelte';
  
  // Simple routing
  let currentPath = window.location.pathname;
  let kartNumber = 5; // Default kart number for demo
  
  // Update path when URL changes
  window.addEventListener('popstate', () => {
    currentPath = window.location.pathname;
  });
  
  // Function to navigate to a different route
  function navigate(path: string) {
    window.history.pushState({}, '', path);
    currentPath = path;
  }
  
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
