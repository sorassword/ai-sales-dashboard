<script lang="ts">
  import Topbar from '$lib/components/Topbar.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import { formatEur, formatHours } from '$lib/utils/format';
  import { isReloading, periodLabelStore } from '$lib/stores/period.svelte';
  import { openModal } from '$lib/stores/modal.svelte';
  import type { StoreDetail } from '$lib/types';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  let stores = $derived(data.stores);
  let subtitle = $derived(`Umsatz vs. Bot-Nutzung im Filialvergleich · ${$periodLabelStore}`);

  function open(storeId: string) {
    const details = data.storeDetails as Record<string, StoreDetail>;
    openModal('store-detail', { store_id: storeId, period: data.period, detail: details[storeId] });
  }
</script>

<Topbar title="Filialen" {subtitle} />

<div
  class="grid grid-cols-1 gap-4 transition-opacity duration-200 md:grid-cols-2"
  class:opacity-50={$isReloading}
>
  {#each stores as s (s.store.id)}
    <button class="block w-full cursor-pointer text-left" onclick={() => open(s.store.id)}>
      <Card>
        <div class="flex items-start justify-between">
          <div>
            <h2 class="font-display text-xl font-medium text-ink">{s.store.name}</h2>
            <p class="text-[13px] text-ink-soft">{s.store.headcount} Mitarbeiter:innen · {s.store.city}</p>
          </div>
          <span class="tnum rounded-full bg-paper px-2.5 py-1 text-[12px] font-medium text-ink-soft">
            Readiness {s.readiness_score}
          </span>
        </div>

        <div class="mt-5 grid grid-cols-2 gap-4">
          <div>
            <p class="text-[12px] tracking-wide text-ink-mute uppercase">Umsatz</p>
            <p class="tnum mt-1 text-2xl font-semibold text-ink">{formatEur(s.revenue)}</p>
            <p class="text-[12px] text-ink-soft">{s.revenue_share_pct}% der Kette</p>
          </div>
          <div>
            <p class="text-[12px] tracking-wide text-ink-mute uppercase">Bot-Zeit</p>
            <p class="tnum mt-1 text-2xl font-semibold text-ink">{formatHours(s.bot_minutes)}</p>
            <p class="text-[12px] text-ink-soft">{s.chat_share_pct}% der Chat-Zeit</p>
          </div>
        </div>

        <!-- revenue vs chat share comparison bars -->
        <div class="mt-5 space-y-2">
          <div class="flex items-center gap-3">
            <span class="w-20 text-[12px] text-ink-soft">Umsatz</span>
            <div class="h-2 flex-1 overflow-hidden rounded-full bg-paper">
              <div class="h-full rounded-full bg-ink" style="width:{s.revenue_share_pct}%"></div>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-20 text-[12px] text-ink-soft">Chat-Zeit</span>
            <div class="h-2 flex-1 overflow-hidden rounded-full bg-paper">
              <div class="h-full rounded-full bg-brass" style="width:{s.chat_share_pct}%"></div>
            </div>
          </div>
        </div>
      </Card>
    </button>
  {/each}
</div>
