<script lang="ts">
  import { get } from 'svelte/store';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ModalSkeleton from '$lib/components/ui/ModalSkeleton.svelte';
  import ScatterChart from '$lib/components/charts/ScatterChart.svelte';
  import { api } from '$lib/api/client';
  import { closeModal } from '$lib/stores/modal.svelte';
  import { activePeriod } from '$lib/stores/period.svelte';
  import { formatEur, formatNum } from '$lib/utils/format';
  import type { CorrelationDetail, CorrelationEmployee, Period, ScatterPoint } from '$lib/types';

  interface Props {
    period?: Period;
    detail?: CorrelationDetail;
  }
  let { period, detail }: Props = $props();

  let fetched = $state<CorrelationDetail | null>(null);
  let data = $derived(detail ?? fetched);
  let loading = $derived(!data);

  $effect(() => {
    if (detail || fetched) return;
    let cancelled = false;
    api.correlationDetail(period ?? get(activePeriod)).then((d) => {
      if (!cancelled) fetched = d;
    });
    return () => {
      cancelled = true;
    };
  });

  let scatterPoints = $derived<ScatterPoint[]>(
    (data?.employees ?? []).map((e, i) => ({
      employee_id: String(i),
      name: e.name,
      bot_minutes: e.bot_minutes,
      revenue: e.revenue,
      learning_score: 0
    }))
  );

  type SortKey = 'name' | 'store' | 'bot_minutes' | 'revenue';
  let sortKey = $state<SortKey>('revenue');

  let sortedEmployees = $derived(
    [...(data?.employees ?? [])].sort((a: CorrelationEmployee, b: CorrelationEmployee) => {
      if (sortKey === 'name' || sortKey === 'store') return a[sortKey].localeCompare(b[sortKey]);
      return b[sortKey] - a[sortKey];
    })
  );

  const cols: { key: SortKey; label: string; right?: boolean }[] = [
    { key: 'name', label: 'Name' },
    { key: 'store', label: 'Filiale' },
    { key: 'bot_minutes', label: 'Bot-Min.', right: true },
    { key: 'revenue', label: 'Umsatz', right: true }
  ];
</script>

<Modal open={true} title="Korrelation Bot-Nutzung → Umsatz" width="max-w-5xl" onClose={closeModal}>
  {#if loading || !data}
    <ModalSkeleton />
  {:else}
    <div class="rounded-xl border border-gray-100 p-4">
      <ScatterChart points={scatterPoints} height={340} />
    </div>

    <div class="mt-5 max-h-72 overflow-y-auto rounded-xl border border-gray-100">
      <table class="w-full border-collapse text-sm">
        <thead class="sticky top-0 bg-white">
          <tr class="text-left text-[11px] tracking-wide text-ink-mute uppercase">
            {#each cols as c (c.key)}
              <th class="px-4 py-2 font-medium {c.right ? 'text-right' : ''}">
                <button
                  class="cursor-pointer transition-colors duration-150 hover:text-ink {sortKey === c.key ? 'text-ink' : ''}"
                  onclick={() => (sortKey = c.key)}
                >
                  {c.label}{sortKey === c.key ? ' ↓' : ''}
                </button>
              </th>
            {/each}
            <th class="px-4 py-2 text-right font-medium">Ausreißer</th>
          </tr>
        </thead>
        <tbody>
          {#each sortedEmployees as e (e.name)}
            <tr class="border-t border-gray-100">
              <td class="px-4 py-2.5 font-medium text-ink">{e.name}</td>
              <td class="px-4 py-2.5 text-ink-soft">{e.store.replace('Modehaus ', '')}</td>
              <td class="tnum px-4 py-2.5 text-right text-ink-soft">{formatNum(e.bot_minutes)}</td>
              <td class="tnum px-4 py-2.5 text-right text-ink-soft">{formatEur(e.revenue)}</td>
              <td class="px-4 py-2.5 text-right">
                {#if e.is_outlier}
                  <span class="rounded-full bg-signal/10 px-2 py-0.5 text-[11px] font-medium text-signal">Ausreißer</span>
                {:else}
                  <span class="text-ink-mute">–</span>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="mt-4 rounded-lg bg-gray-50 px-4 py-3 text-[13px] text-ink-soft italic">
      {data.insight}
    </div>
  {/if}
</Modal>
