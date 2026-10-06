<script lang="ts">
  import { get } from 'svelte/store';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ModalSkeleton from '$lib/components/ui/ModalSkeleton.svelte';
  import LineChart from '$lib/components/charts/LineChart.svelte';
  import { api } from '$lib/api/client';
  import { closeModal } from '$lib/stores/modal.svelte';
  import { activePeriod } from '$lib/stores/period.svelte';
  import { formatNum, formatHoursValue } from '$lib/utils/format';
  import type { BotTrendDetail, Period } from '$lib/types';

  interface Props {
    period?: Period;
    detail?: BotTrendDetail;
  }
  let { period, detail }: Props = $props();

  let fetched = $state<BotTrendDetail | null>(null);
  let data = $derived(detail ?? fetched);
  let loading = $derived(!data);

  $effect(() => {
    if (detail || fetched) return;
    let cancelled = false;
    api.botTrendDetail(period ?? get(activePeriod)).then((d) => {
      if (!cancelled) fetched = d;
    });
    return () => {
      cancelled = true;
    };
  });

  const colorFor = (key: string) =>
    ({
      brass: 'var(--color-brass)',
      ink: 'var(--color-ink)',
      positive: 'var(--color-positive)',
      signal: 'var(--color-signal)'
    })[key] ?? 'var(--color-ink)';
</script>

<Modal open={true} title="Bot-Nutzung nach Filiale" width="max-w-4xl" onClose={closeModal}>
  {#if loading || !data}
    <ModalSkeleton />
  {:else}
    <p class="mb-2 text-[13px] text-ink-soft">Trainings- & Beratungszeit · Team gesamt</p>
    <LineChart data={data.points} valueFormat={(v) => `${formatNum(v)} min`} color="var(--color-ink)" height={240} />

    <p class="mt-6 mb-3 text-[12px] font-medium tracking-wide text-ink-mute uppercase">
      Bot-Stunden pro Filiale
    </p>
    <div class="space-y-3">
      {#each data.by_store as s (s.store_name)}
        <div>
          <div class="mb-1 flex items-baseline justify-between gap-3">
            <span class="text-[13px] font-medium text-ink">{s.store_name}</span>
            <span class="tnum text-[13px] text-ink-soft">{formatHoursValue(s.bot_hours)} · {s.pct_of_total}%</span>
          </div>
          <div class="h-2.5 overflow-hidden rounded-full bg-paper">
            <div
              class="h-full rounded-full transition-[width] duration-500"
              style="width:{s.pct_of_total}%;background:{colorFor(s.color_key)}"
            ></div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</Modal>
