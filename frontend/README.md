# NFS Timings Frontend

This is a Svelte-based frontend for the NFS Timings application. It provides a modern, reactive UI for tracking kart racing timings and statistics.

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── routes/         # Page components
│   ├── styles/         # Global styles
│   ├── lib/            # Utility functions and shared code
│   ├── App.svelte      # Main application component
│   └── main.ts         # Application entry point
├── public/             # Static assets
├── index.html          # HTML entry point
├── package.json        # Project dependencies and scripts
├── tsconfig.json       # TypeScript configuration
└── vite.config.ts      # Vite configuration
```

## Components

### Core Components

- **Kart.svelte**: Displays a kart number with optional badge and styling
- **StintsTable.svelte**: Displays a table of stint information
- **StintsTableHeader.svelte**: Header for the stints table with sorting options
- **TeamCard.svelte**: Displays team information with expandable details
- **KartPit.svelte**: Displays a kart in the pit area
- **Header.svelte**: Main navigation header

### Pages

- **Karts.svelte**: Main page showing all karts and their stints
- **Teams.svelte**: Page showing all teams
- **KartDetails.svelte**: Detailed view for a specific kart
- **Settings.svelte**: Application settings

## Development

### Prerequisites

- Node.js (v14+)
- npm or yarn

### Setup

You can use the provided script to set up and run the development server:

```bash
./run-dev.sh
```

Or manually:

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm run dev
   ```

3. Build for production:
   ```
   npm run build
   ```

### Static Preview

If you're having issues with Node.js dependencies, you can view a static preview of the components without running the development server:

1. Open the `preview.html` file in your browser:
   ```
   open preview.html
   ```

This static preview shows the main components with sample data but doesn't include interactive functionality.

### TypeScript Support

This project uses TypeScript with Svelte. The TypeScript preprocessing is configured in the `vite.config.ts` file:

```typescript
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import sveltePreprocess from 'svelte-preprocess';

export default defineConfig({
  plugins: [
    svelte({
      preprocess: sveltePreprocess({
        typescript: true,
      }),
    }),
  ],
});
```

To use TypeScript in a Svelte component, add `lang="ts"` to the script tag:

```svelte
<script lang="ts">
  // TypeScript code here
  let count: number = 0;
  
  function increment(): void {
    count += 1;
  }
</script>
```

### Troubleshooting

#### macOS ICU Library Issues

If you encounter errors related to the ICU library (e.g., `dyld: Library not loaded: /opt/homebrew/opt/icu4c/lib/libicui18n.74.dylib`), try the following:

1. Reinstall Node.js using Homebrew:
   ```
   brew reinstall node
   brew link --overwrite node
   ```

2. Or use a Node version manager like nvm:
   ```
   nvm install 16  # Install Node.js v16
   nvm use 16      # Use Node.js v16
   ```

3. If using a different Node.js version, make sure the ICU libraries are properly linked:
   ```
   brew install icu4c
   brew link icu4c --force
   ```

## Features

- Display kart numbers with visual indicators for kart status
- Show team information with expandable stint details
- View detailed kart information with the ability to add notes and visual indicators
- Sort and filter stint data
- Simple client-side routing

## Notes

This frontend is designed to work with the NFS Timings backend API. It uses mock data for development purposes, but in a production environment, it would fetch data from the API.
