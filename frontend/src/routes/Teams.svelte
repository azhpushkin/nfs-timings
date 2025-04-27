<script lang="ts">
  import TeamCard from '../components/TeamCard.svelte';
  
  // Mock data - in a real app, this would be fetched from an API
  let teams = [
    {
      number: 1,
      name: 'Team Alpha',
      average_lap: '1:23.456',
      pilots: ['John Doe', 'Jane Smith'],
      stints: [
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
        }
      ]
    },
    {
      number: 2,
      name: 'Team Beta',
      average_lap: '1:24.567',
      pilots: ['Bob Johnson', 'Alice Brown'],
      stints: [
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
      ]
    }
  ];
</script>

<h2>Teams</h2>

{#each teams as team}
  <TeamCard {team} />
{/each}
