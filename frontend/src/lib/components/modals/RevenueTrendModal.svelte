<script lang="ts">
  import { get } from 'svelte/store';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ModalSkeleton from '$lib/components/ui/ModalSkeleton.svelte';
  import LineChart from '$lib/components/charts/LineChart.svelte';
  import { api } from '$lib/api/client';
  import { closeModal } from '$lib/stores/modal.svelte';
  import { activePeriod } from '$lib/stores/period.svelte';
  import { formatEur, formatEurCompact } from '$lib/utils/format';
  import type { Period, RevenueTrendDetail } from '$lib/types';

  interface Props {
    period?: Period;
    detail?: RevenueTrendDetail;
  }
  let { period, detail }: Props = $props();

  let fetched = $state<RevenueTrendDetail | null>(null);
  let data = $derived(detail ?? fetched);
  let loading = $derived(!data);

  $effect(() => {
    if (detail || fetched) return;
    let cancelled = false;
    api.revenueTrendDetail(period ?? get(activePeriod)).then((d) => {
      if (!cancelled) fetched = d;
    });
    return () => {
      cancelled = true;
    };
  });
</script>

<Modal open={true} title="Umsatzentwicklung — Detail" width="max-w-5xl" onClose={closeModal}>
  {#if loading || !data}
    <ModalSkeleton />
  {:else}
    <p class="mb-2 text-[13px] text-ink-soft">Letzte 24 Monate · Netto-Umsatz der Kette</p>
    <LineChart data={data.extended_points} valueFormat={formatEurCompact} color="var(--color-brass)" height={260} />

    <p class="mt-6 mb-3 text-[12px] font-medium tracking-wide text-ink-mute uppercase">
      Monats-Highlights (letzte 6 Monate)
    </p>
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {#each data.monthly_insights as mi (mi.label)}
        <div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
          <p class="text-[11px] font-medium tracking-wide text-ink-mute uppercase">{mi.label}</p>
          <p class="tnum mt-1 text-lg font-semibold text-ink">{formatEur(mi.value)}</p>
          <p class="mt-1 text-[13px] text-ink-soft">{mi.comment}</p>
        </div>
      {/each}
    </div>
  {/if}
</Modal>
