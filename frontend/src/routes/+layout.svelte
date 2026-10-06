<script lang="ts">
  import '../app.css';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import ModalHost from '$lib/components/ModalHost.svelte';
  import { invalidate } from '$app/navigation';
  import { activePeriod, isReloading } from '$lib/stores/period.svelte';
  import type { Snippet } from 'svelte';

  let { children }: { children: Snippet } = $props();

  // When the period changes, re-run every load() that registered the
  // 'app:period' dependency. Skip the very first run (the initial load already
  // ran with the default period) and dim the content while the reload is live.
  let initialized = false;
  $effect(() => {
    void $activePeriod; // track period changes
    if (!initialized) {
      initialized = true;
      return;
    }
    isReloading.set(true);
    invalidate('app:period').finally(() => isReloading.set(false));
  });
</script>

<div class="bg-grain flex min-h-screen bg-paper">
  <Sidebar />
  <main class="h-screen flex-1 overflow-y-auto">
    <div class="mx-auto max-w-[1180px] px-8 py-9">
      {@render children()}
    </div>
  </main>
</div>

<!-- Global modal host — renders the active modal from the shared store. -->
<ModalHost />
