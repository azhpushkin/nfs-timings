<script lang="ts">
  // Mock settings
  let darkMode = false;
  let language = 'uk';
  let refreshInterval = 5;
  
  // Handle dark mode toggle
  function toggleDarkMode() {
    darkMode = !darkMode;
    // In a real app, this would update the theme
  }
  
  // Handle language change
  function changeLanguage(event: Event) {
    const select = event.target as HTMLSelectElement;
    language = select.value;
    // In a real app, this would update the language
  }
  
  // Handle refresh interval change
  function changeRefreshInterval(event: Event) {
    const input = event.target as HTMLInputElement;
    refreshInterval = parseInt(input.value);
    // In a real app, this would update the refresh interval
  }
</script>

<h2>Різне</h2>

<div class="settings-container">
  <div class="setting-item">
    <h3>Тема</h3>
    <label>
      <input type="checkbox" checked={darkMode} on:change={toggleDarkMode}>
      Темна тема
    </label>
  </div>
  
  <div class="setting-item">
    <h3>Мова</h3>
    <select value={language} on:change={changeLanguage}>
      <option value="uk">Українська</option>
      <option value="en">English</option>
      <option value="ru">Русский</option>
    </select>
  </div>
  
  <div class="setting-item">
    <h3>Інтервал оновлення (секунди)</h3>
    <input 
      type="number" 
      min="1" 
      max="60" 
      value={refreshInterval} 
      on:input={changeRefreshInterval}
    >
  </div>
  
  <div class="setting-item">
    <h3>Про додаток</h3>
    <p>NFS Timings - додаток для відстеження часу кругів у перегонах.</p>
    <p>Версія: 1.0.0</p>
  </div>
</div>

<style>
  .settings-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .setting-item {
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 15px;
    background-color: #f9f9f9;
  }
  
  .setting-item h3 {
    margin-top: 0;
    border-bottom: 1px solid #ddd;
    padding-bottom: 10px;
  }
  
  select, input[type="number"] {
    padding: 5px;
    border-radius: 3px;
    border: 1px solid #ccc;
  }
</style>
