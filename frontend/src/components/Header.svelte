<script lang="ts">
  // Define the navigation items
  const navItems = [
    { path: '/', label: 'Карти', icon: '🚀' },
    { path: '/teams', label: 'Команди', icon: '👥' },
    { path: '/kart-details/5', label: 'Деталі', icon: '🏁' },
    { path: '/settings', label: 'Різне', icon: '🔧' }
  ];
  
  // Get current path
  let currentPath = window.location.pathname;
  
  // Handle navigation
  function handleNavClick(event: MouseEvent, path: string) {
    event.preventDefault();
    currentPath = path;
    
    // Use the global navigate function
    if (typeof window !== 'undefined' && (window as any).appNavigate) {
      (window as any).appNavigate(path);
    }
  }
</script>

<header>
  <h3 id="header-title">
    🚀
    🏁
    🏆
    NFS Telega
  </h3>
  <nav>
    {#each navItems as item}
      <a href={item.path} on:click={(e) => handleNavClick(e, item.path)}>
        <button class:active-tab={currentPath === item.path}>
          {item.icon} <br> {item.label}
        </button>
      </a>
    {/each}
  </nav>
</header>

<style>
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #ccc;
  }
  
  #header-title {
    margin: 0;
  }
  
  nav {
    display: flex;
    gap: 0.5rem;
  }
  
  button {
    padding: 0.5rem 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #f5f5f5;
    cursor: pointer;
    text-align: center;
  }
  
  button:hover {
    background-color: #e5e5e5;
  }
  
  .active-tab {
    background-color: #ddd;
    font-weight: bold;
  }
</style>
