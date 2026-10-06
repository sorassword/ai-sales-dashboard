<script lang="ts">
  import Topbar from '$lib/components/Topbar.svelte';
  import { formatDate } from '$lib/utils/format';
  import { isReloading, periodLabelStore } from '$lib/stores/period.svelte';
  import { openModal } from '$lib/stores/modal.svelte';
  import type { AlertLevel } from '$lib/types';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  let items = $derived(data.items);
  let subtitle = $derived(
    `Wie gut ist das Team auf kommende Kollektions-Launches vorbereitet? · ${$periodLabelStore}`
  );

  // Per-alert-level presentation. Colors follow the spec exactly.
  const cardCls: Record<AlertLevel, string> = {
    critical: 'border-line border-l-4 border-l-[#DC2626] bg-[#FEF2F2]',
    warning: 'border-line border-l-4 border-l-[#D97706] bg-[#FFFBEB]',
    ok: 'border-line bg-card'
  };
  const badge: Record<AlertLevel, { label: string; cls: string }> = {
    critical: { label: 'Kritisch', cls: 'bg-[#DC2626]/10 text-[#DC2626]' },
    warning: { label: 'Rückstand', cls: 'bg-[#D97706]/10 text-[#D97706]' },
    ok: { label: 'Bereit', cls: 'bg-positive/10 text-positive' }
  };
  const barColor: Record<AlertLevel, string> = {
    critical: '#DC2626',
    warning: '#D97706',
    ok: 'var(--color-ink)'
  };
</script>

<Topbar title="Seasonal Readiness" {subtitle} />

<div class="flex flex-col gap-4 transition-opacity duration-200" class:opacity-50={$isReloading}>
  <!-- Critical alert banner (only when something is actually critical) -->
  {#if data.critical_count > 0}
    <div
      class="flex flex-col gap-2 rounded-lg bg-[#B91C1C] px-6 py-4 text-white sm:flex-row sm:items-center sm:justify-between"
    >
      <p class="font-bold">
        ⚠ {data.critical_count} Kollektion(en) im kritischen Rückstand — Launch in weniger als 7 Tagen
      </p>
      <p class="text-sm font-semibold whitespace-nowrap text-white/90">
        {data.next_launch.name} · noch {data.next_launch.days_until} Tage
      </p>
    </div>
  {/if}

  {#each items as r (r.collection)}
    {@const bdg = badge[r.alert_level]}
    <button
      type="button"
      class="block w-full cursor-pointer rounded-[var(--radius-card)] border p-5 text-left shadow-[0_1px_2px_rgba(27,31,59,0.04)] transition-shadow duration-150 hover:shadow-[0_4px_16px_rgba(0,0,0,0.08)] {cardCls[
        r.alert_level
      ]}"
      onclick={() => openModal('readiness-collection', { collection_name: r.collection, items })}
    >
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="min-w-0">
          <div class="flex items-center gap-3">
            <h2 class="font-display text-lg font-medium text-ink">{r.collection}</h2>
            <span class="rounded-full px-2.5 py-0.5 text-[12px] font-medium {bdg.cls}">{bdg.label}</span>
          </div>
          <p class="mt-1 text-[13px] text-ink-soft">
            Launch am {formatDate(r.launch_date)} · {r.prepared_employees} von {r.total_employees} eingearbeitet
          </p>
        </div>
        <div class="text-right">
          <p class="tnum text-3xl font-semibold text-ink">
            {r.readiness_score}<span class="text-base text-ink-mute">/100</span>
          </p>
        </div>
      </div>

      <div class="mt-4 h-2.5 overflow-hidden rounded-full bg-paper">
        <div
          class="h-full rounded-full transition-[width] duration-700"
          style="width:{r.readiness_score}%;background:{barColor[r.alert_level]}"
        ></div>
      </div>
    </button>
  {/each}
</div>
