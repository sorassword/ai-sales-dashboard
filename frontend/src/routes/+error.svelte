<script lang="ts">
  import { page } from '$app/stores';
  import { API_BASE } from '$lib/api/client';

  $: message = $page.error?.message ?? 'Unbekannter Fehler';
  $: isApiError =
    message.includes('API ') ||
    message.includes('fetch failed') ||
    message.includes('ECONNREFUSED') ||
    message.includes('Failed to fetch');
</script>

<div class="flex min-h-screen items-center justify-center bg-paper p-8">
  <div class="max-w-md rounded-[var(--radius-card)] border border-line bg-card p-8 text-center">
    <p class="font-display text-2xl font-medium text-ink">
      {isApiError ? 'Keine Verbindung zur API' : 'Dashboard konnte nicht geladen werden'}
    </p>
    <p class="mt-3 text-sm leading-relaxed text-ink-soft">
      {#if isApiError}
        Das Frontend erreicht das Backend nicht ({$page.status}). Läuft das FastAPI-Backend?
      {:else}
        Status {$page.status}: {message}
      {/if}
    </p>
    {#if isApiError}
      <pre class="mt-4 rounded-lg bg-ink px-4 py-3 text-left text-[12px] text-card/90"><code>cd backend
uvicorn app.main:app --reload --port 8000</code></pre>
    {/if}
    <p class="mt-4 text-[12px] text-ink-mute">Erwartet unter: {API_BASE}</p>
  </div>
</div>
