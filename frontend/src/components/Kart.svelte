<script lang="ts">
  import { badgeColors } from '../lib/badges';
  
  export let number: number | null = null;
  export let nolink: boolean = false;
  export let inline: boolean = false;
  export let badge: string | null = null;
  export let accent: string | null = null;
  
  // Compute styles
  $: inlineStyle = inline ? 'display: inline-block;' : '';
  $: accentStyle = accent ? `background-color: ${accent};` : '';
  $: style = inlineStyle + accentStyle;
  
  // Determine if we should show a link
  $: showAsLink = number && !nolink;
  
  // Generate href for link
  $: href = showAsLink ? `/kart-details/${number}` : undefined;
  
  // Get badge background color
  $: badgeColor = badge && badgeColors[badge] ? badgeColors[badge] : 'white';
</script>

{#if showAsLink}
  <a class="kart-number" {style} {href}>
    {number ?? '?'}
    {#if badge}
      <div class="badge {badge}" style="background-color: {badgeColor};"></div>
    {/if}
  </a>
{:else}
  <span class="kart-number" {style}>
    {number ?? '?'}
    {#if badge}
      <div class="badge {badge}" style="background-color: {badgeColor};"></div>
    {/if}
  </span>
{/if}

<style>
  .badge {
    padding: 0.1em;
    border: 1px solid black;
    border-radius: 50%;
    width: 0.7em;
    height: 0.7em;
    position: absolute;
    top: -0.6em;
    right: -0.34em;
  }
</style>
