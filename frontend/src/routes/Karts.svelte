<script lang="ts">
  import StintsTable from '../components/StintsTable.svelte';
  
  // State for showing first stint
  let showFirstStint = false;
  
  // Mock data - in a real app, this would be fetched from an API
  let stints = [
    {
      kart: 5,
      pilot: 'John Doe',
      stint_started_at: '14:30',
      best_lap: 82.345,
      best_sector_1: 41.123,
      best_sector_2: 41.222,
      avg_80: 83.456,
      stint_id: 'stint1'
    },
    {
      kart: 7,
      pilot: 'Jane Smith',
      stint_started_at: '15:30',
      best_lap: 81.987,
      best_sector_1: 40.876,
      best_sector_2: 41.111,
      avg_80: 82.789,
      stint_id: 'stint2'
    },
    {
      kart: 3,
      pilot: 'Bob Johnson',
      stint_started_at: '14:45',
      best_lap: 83.123,
      best_sector_1: 41.567,
      best_sector_2: 41.556,
      avg_80: 84.234,
      stint_id: 'stint3'
    },
    {
      kart: 9,
      pilot: 'Alice Brown',
      stint_started_at: '15:45',
      best_lap: 82.456,
      best_sector_1: 41.234,
      best_sector_2: 41.222,
      avg_80: 83.567,
      stint_id: 'stint4'
    }
  ];
  
  // Function to handle filter change
  function handleFilterChange(event: Event) {
    const target = event.target as HTMLInputElement;
    showFirstStint = target.value === '1';
    
    // In a real app, this would trigger a data refetch
  }
</script>

<h2>Karts</h2>

<details>
  <summary>Фільтрація відрізків</summary>
  
  <div class="show-first-stint">
    <form>
      <span>Показувати перший відрізок</span>
      &nbsp;&nbsp;&nbsp;
      <label>
        <input 
          type="radio" 
          name="show_first_stint" 
          value="1" 
          checked={showFirstStint} 
          on:change={handleFilterChange}
        >
        Так
      </label>
      
      <label>
        <input 
          type="radio" 
          name="show_first_stint" 
          value="0" 
          checked={!showFirstStint} 
          on:change={handleFilterChange}
        >
        Ні
      </label>
    </form>
  </div>
</details>
<br>

<StintsTable stints={stints} columns="PBSA" sortable={true} />

<style>
  .show-first-stint {
    margin: 10px 0;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #f9f9f9;
  }
  
  label {
    margin-right: 10px;
  }
</style>
