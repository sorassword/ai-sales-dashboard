<script lang="ts">
  import { get } from 'svelte/store';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ModalSkeleton from '$lib/components/ui/ModalSkeleton.svelte';
  import { api } from '$lib/api/client';
  import { closeModal, openModal } from '$lib/stores/modal.svelte';
  import { activePeriod } from '$lib/stores/period.svelte';
  import { formatEur, formatHoursValue, formatDate } from '$lib/utils/format';
  import { Flame } from 'lucide-svelte';
  import type { Period, StoreDetail } from '$lib/types';

  interface Props {
    store_id: string;
    period?: Period;
    detail?: StoreDetail;
  }
  let { store_id, period, detail }: Props = $props();

  let fetched = $state<StoreDetail | null>(null);
  let data = $derived(detail ?? fetched);
  let loading = $derived(!data);

  $effect(() => {
    if (detail || fetched) return;
    let cancelled = false;
    api.storeDetail(store_id, period ?? get(activePeriod)).then((d) => {
      if (!cancelled) fetched = d;
    });
    return () => {
      cancelled = true;
    };
  });

  const alertMap: Record<string, { label: string; pill: string; bar: string }> = {
    critical: { label: 'Kritisch', pill: 'bg-[#DC2626]/10 text-[#DC2626]', bar: '#DC2626' },
    warning: { label: 'Rückstand', pill: 'bg-[#D97706]/10 text-[#D97706]', bar: '#D97706' },
    ok: { label: 'Bereit', pill: 'bg-positive/10 text-positive', bar: 'var(--color-ink)' }
  };

  const kpis = $derived(
    data
      ? [
          { label: 'Umsatz', value: formatEur(data.revenue) },
          { label: 'Umsatzanteil', value: `${data.revenue_share_pct}%` },
          { label: 'Umsatz / Mitarbeiter:in', value: formatEur(data.revenue_per_employee) },
          { label: 'Bot-Zeit gesamt', value: formatHoursValue(data.bot_hours) },
          { label: 'Bot-Zeit / Mitarbeiter:in', value: formatHoursValue(data.bot_hours_per_employee) },
          { label: 'Ø Lernscore', value: `${data.avg_learn_score}/100` }
        ]
      : []
  );
</script>

<Modal open={true} title={data?.name ?? 'Filiale'} width="max-w-5xl" onClose={closeModal}>
  {#if loading || !data}
    <ModalSkeleton />
  {:else}
    {@const nc = alertMap[data.next_collection.alert_level] ?? alertMap.ok}

    <!-- KPI grid 2×3 -->
    <div class="grid grid-cols-2 gap-3 md:grid-cols-3">
      {#each kpis as k (k.label)}
        <div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
          <p class="text-[11px] font-medium tracking-wide text-ink-mute uppercase">{k.label}</p>
          <p class="tnum mt-1 text-xl font-semibold text-ink">{k.value}</p>
        </div>
      {/each}
    </div>

    <!-- Next collection -->
    <p class="mt-6 mb-2 text-[12px] font-medium tracking-wide text-ink-mute uppercase">Nächste Kollektion</p>
    <div class="rounded-xl border border-gray-100 p-4">
      <div class="flex items-center justify-between gap-3">
        <div class="min-w-0">
          <p class="font-medium text-ink">{data.next_collection.name}</p>
          <p class="mt-0.5 text-[13px] text-ink-soft">Launch am {formatDate(data.next_collection.launch_date)}</p>
        </div>
        <div class="flex shrink-0 items-center gap-3">
          <span class="rounded-full px-2.5 py-0.5 text-[12px] font-medium {nc.pill}">{nc.label}</span>
          <span class="tnum text-lg font-semibold text-ink">{data.next_collection.readiness_score}</span>
        </div>
      </div>
      <div class="mt-3 h-2.5 overflow-hidden rounded-full bg-paper">
        <div
          class="h-full rounded-full"
          style="width:{data.next_collection.readiness_score}%;background:{nc.bar}"
        ></div>
      </div>
    </div>

    <!-- Insight -->
    <div class="mt-4 rounded-lg bg-gray-50 px-4 py-3 text-[13px] text-ink-soft italic">
      {data.insight}
    </div>

    <!-- Employee table -->
    <p class="mt-6 mb-2 text-[12px] font-medium tracking-wide text-ink-mute uppercase">Mitarbeiter:innen</p>
    <div class="overflow-x-auto rounded-xl border border-gray-100">
      <table class="w-full border-collapse text-sm">
        <thead>
          <tr class="text-left text-[11px] tracking-wide text-ink-mute uppercase">
            <th class="px-3 py-2 font-medium">Rang</th>
            <th class="px-3 py-2 font-medium">Name</th>
            <th class="px-3 py-2 font-medium">Rolle</th>
            <th class="px-3 py-2 text-right font-medium">Umsatz</th>
            <th class="px-3 py-2 text-right font-medium">Bot-Zeit</th>
            <th class="px-3 py-2 text-right font-medium">Lernscore</th>
            <th class="px-3 py-2 text-right font-medium">Streak</th>
            <th class="px-3 py-2 text-right font-medium">Badges</th>
          </tr>
        </thead>
        <tbody>
          {#each data.employees as e (e.id)}
            <tr
              class="cursor-pointer border-t border-gray-100 transition-colors duration-150 hover:bg-gray-50 {e.rank === 1 ? 'bg-[#FEF3C7]' : ''}"
              onclick={() => openModal('employee-detail', { employee_id: e.id, period })}
            >
              <td class="tnum px-3 py-2.5 font-semibold text-ink">{e.rank}</td>
              <td class="px-3 py-2.5 font-medium text-ink">{e.name}</td>
              <td class="px-3 py-2.5 text-ink-soft">{e.role}</td>
              <td class="tnum px-3 py-2.5 text-right text-ink">{formatEur(e.revenue)}</td>
              <td class="tnum px-3 py-2.5 text-right text-ink-soft">{formatHoursValue(e.bot_hours)}</td>
              <td class="tnum px-3 py-2.5 text-right text-ink-soft">{e.learn_score}</td>
              <td class="px-3 py-2.5 text-right">
                <span class="tnum inline-flex items-center justify-end gap-1 text-ink-soft">
                  {#if e.streak_days > 20}🔥{/if}{e.streak_days}d
                </span>
              </td>
              <td class="tnum px-3 py-2.5 text-right text-ink-soft">{e.badge_count}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</Modal>
