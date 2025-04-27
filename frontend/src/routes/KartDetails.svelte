<script lang="ts">
  import Kart from '../components/Kart.svelte';
  import StintsTable from '../components/StintsTable.svelte';
  import { badgeColors } from '../lib/badges';
  
  export let kartNumber: number;
  
  // Mock data - in a real app, this would be fetched from an API
  let stints: any[] = [];
  let kartNote: string | null = null;
  let currentBadge: string | null = null;
  let currentAccent: string | null = null;
  
  // Badge options
  const BADGE_NAMES = {
    'good': 'Відкручена',
    'slowed': 'Закручена',
    'damaged': 'Поломка',
    'unknown': 'Нестабільна',
    'none': 'Очистити'
  };
  
  // Accent options
  const accentOptions = [null, '#69ff6e', '#e87474', '#faec6e'];
  
  function updateBadge(badge: string | null) {
    // In a real app, this would send a request to the server
    currentBadge = badge;
  }
  
  function updateAccent(accent: string | null) {
    // In a real app, this would send a request to the server
    currentAccent = accent;
  }
  
  function saveNote(event: Event) {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const formData = new FormData(form);
    const note = formData.get('note') as string;
    
    // In a real app, this would send a request to the server
    kartNote = note;
  }
</script>

<h3>
  Всі відрізки на <Kart number={kartNumber} nolink={true} inline={true} badge={currentBadge} accent={currentAccent} />
</h3>

{#if kartNote}
  <div class="kart-note"><b>Примітка: </b>{kartNote}</div>
{/if}

<StintsTable stints={stints} columns="PBSAL" sortable={true} />

<hr>

<div class="kart-config">
  <h4>Змінити фон</h4>
  <div class="picker">
    {#each accentOptions as accent}
      <button 
        class="accent-option"
        on:click={() => updateAccent(accent)}
        disabled={accent === currentAccent}
      >
        <Kart number={kartNumber} inline={true} accent={accent || 'white'} nolink={true} />
      </button>
    {/each}
  </div>

  <h4>Відмітити карт значком</h4>
  <div class="picker">
    {#each Object.entries(BADGE_NAMES) as [badge, name]}
      <button 
        class="badge-option"
        on:click={() => updateBadge(badge === 'none' ? null : badge)}
        disabled={badge === currentBadge}
      >
        {#if badge !== 'none'}
          <div class="badge-preview {badge}" style="background-color: {badgeColors[badge] || 'white'};"></div>
        {/if}
        <br>
        <span>{name}</span>
      </button>
    {/each}
  </div>

  <h4>Додати нотатку</h4>
  <form class="picker" on:submit={saveNote}>
    <textarea name="note" placeholder="Цей карт гавно тому що...">{kartNote || ''}</textarea>
    <input type="submit" value="Зберегти">
  </form>
</div>

<style>
  .badge-preview {
    display: inline-block;
    width: 1.5em;
    height: 1.5em;
    border-radius: 50%;
    border: 1px solid black;
  }
  
  .kart-note {
    border: 1px solid #ccc;
    padding: 10px;
    margin: 10px 0;
    border-radius: 5px;
    background-color: #f9f9f9;
  }
  
  .kart-config {
    margin-top: 20px;
  }
  
  .picker {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 20px;
  }
  
  .accent-option, .badge-option {
    padding: 5px;
    border: 1px solid #ccc;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .accent-option:disabled, .badge-option:disabled {
    border: 2px solid black;
  }
  
  textarea {
    width: 100%;
    min-height: 100px;
  }
</style>
