<script lang="ts">
  import { get } from 'svelte/store';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ModalSkeleton from '$lib/components/ui/ModalSkeleton.svelte';
  import Avatar from '$lib/components/ui/Avatar.svelte';
  import LineChart from '$lib/components/charts/LineChart.svelte';
  import { api } from '$lib/api/client';
  import { closeModal } from '$lib/stores/modal.svelte';
  import { activePeriod } from '$lib/stores/period.svelte';
  import { formatEur, formatEurCompact, formatHoursValue, formatNum, formatPct, formatDate } from '$lib/utils/format';
  import { Euro, Flame, Brain, Star, Zap, Crown, Clock, Trophy, Award } from 'lucide-svelte';
  import type { EmployeeDetail, Period } from '$lib/types';

  interface Props {
    employee_id: string;
    period?: Period;
    detail?: EmployeeDetail;
  }
  let { employee_id, period, detail }: Props = $props();

  let fetched = $state<EmployeeDetail | null>(null);
  let data = $derived(detail ?? fetched);
  let loading = $derived(!data);

  $effect(() => {
    if (detail || fetched) return;
    let cancelled = false;
    api.employeeDetail(employee_id, period ?? get(activePeriod)).then((d) => {
      if (!cancelled) fetched = d;
    });
    return () => {
      cancelled = true;
    };
  });

  const iconMap = {
    euro: Euro,
    fire: Flame,
    brain: Brain,
    star: Star,
    lightning: Zap,
    crown: Crown,
    clock: Clock,
    trophy: Trophy
  } as const;
  const iconFor = (key: string) => iconMap[key as keyof typeof iconMap] ?? Award;

  // EmployeeDetail carries no avatar_hue, so derive a stable one from the name.
  const hueFor = (name: string) =>
    [...name].reduce((acc, ch) => (acc + ch.charCodeAt(0)) % 360, 0);

  const rarityRow: Record<string, string> = {
    common: 'border-l-4 border-l-transparent',
    rare: 'border-l-4 border-l-[#A78BFA] bg-[#FAF5FF]',
    legendary: 'border-l-4 border-l-[#F59E0B] bg-[#FFFBEB]'
  };
  const rarityIcon: Record<string, string> = {
    common: 'text-gray-500',
    rare: 'text-[#7C3AED]',
    legendary: 'text-[#B45309]'
  };
</script>

<Modal open={true} title={data?.name ?? 'Mitarbeiter:in'} width="max-w-4xl" onClose={closeModal}>
  {#if loading || !data}
    <ModalSkeleton />
  {:else}
    <!-- Header -->
    <div class="flex items-center gap-4">
      <Avatar initials={data.initials} hue={hueFor(data.name)} size={56} />
      <div class="min-w-0 flex-1">
        <h3 class="text-2xl font-semibold text-ink">{data.name}</h3>
        <p class="text-[13px] text-ink-soft">{data.role} · {data.store_name}</p>
      </div>
      <div class="flex shrink-0 items-center gap-2">
        <span
          class="tnum rounded-full px-2.5 py-1 text-[13px] font-semibold {data.rank <= 3
            ? 'bg-[#FEF3C7] text-[#B45309]'
            : 'bg-paper text-ink-soft'}"
        >
          #{data.rank}
        </span>
        <span class="tnum rounded-full bg-ink px-2.5 py-1 text-[13px] font-semibold text-card">
          {formatNum(data.points)} P
        </span>
      </div>
    </div>

    <!-- KPI row -->
    <div class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
        <p class="text-[11px] font-medium tracking-wide text-ink-mute uppercase">Umsatz</p>
        <p class="tnum mt-1 text-lg font-semibold text-ink">{formatEur(data.revenue)}</p>
      </div>
      <div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
        <p class="text-[11px] font-medium tracking-wide text-ink-mute uppercase">Bot-Zeit</p>
        <p class="tnum mt-1 text-lg font-semibold text-ink">{formatHoursValue(data.bot_hours)}</p>
      </div>
      <div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
        <p class="text-[11px] font-medium tracking-wide text-ink-mute uppercase">Lernscore</p>
        <p class="tnum mt-1 text-lg font-semibold text-ink">{data.learn_score}/100</p>
      </div>
      <div class="rounded-xl border border-gray-100 bg-gray-50 p-4">
        <p class="text-[11px] font-medium tracking-wide text-ink-mute uppercase">Streak</p>
        <p class="tnum mt-1 text-lg font-semibold text-ink">
          {#if data.streak_days > 14}🔥 {/if}{data.streak_days}d
        </p>
      </div>
    </div>

    <!-- vs store average -->
    <div class="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
      <div class="rounded-xl border border-gray-100 p-4">
        <p class="text-[13px] text-ink-soft">
          Umsatz vs. Ø Filiale:
          <span class="font-semibold {data.revenue_vs_store_avg >= 0 ? 'text-positive' : 'text-negative'}">
            {formatPct(data.revenue_vs_store_avg)}
          </span>
        </p>
      </div>
      <div class="rounded-xl border border-gray-100 p-4">
        <p class="text-[13px] text-ink-soft">
          Bot-Zeit vs. Ø Filiale:
          <span class="font-semibold {data.bot_hours_vs_store_avg >= 0 ? 'text-positive' : 'text-negative'}">
            {formatPct(data.bot_hours_vs_store_avg)}
          </span>
        </p>
      </div>
    </div>

    <!-- Insight -->
    <div class="mt-4 rounded-lg bg-gray-50 px-4 py-3 text-[13px] text-ink-soft italic">
      {data.insight}
    </div>

    <!-- Charts -->
    <div class="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div class="rounded-xl border border-gray-100 p-4">
        <p class="mb-2 text-[12px] font-medium tracking-wide text-ink-mute uppercase">Bot-Nutzung</p>
        <LineChart data={data.bot_trend} valueFormat={(v) => `${formatNum(v)} min`} color="var(--color-ink)" height={180} />
      </div>
      <div class="rounded-xl border border-gray-100 p-4">
        <p class="mb-2 text-[12px] font-medium tracking-wide text-ink-mute uppercase">Umsatzentwicklung</p>
        <LineChart data={data.revenue_trend} valueFormat={formatEurCompact} color="var(--color-brass)" height={180} />
      </div>
    </div>

    <!-- Badges -->
    <p class="mt-6 mb-2 text-[12px] font-medium tracking-wide text-ink-mute uppercase">Verdiente Badges</p>
    {#if data.badges.length}
      <div class="space-y-2">
        {#each data.badges as b (b.name + b.earned_date)}
          {@const Icon = iconFor(b.icon_key)}
          <div
            class="flex items-center gap-3 rounded-lg border border-gray-100 py-2.5 pr-4 pl-3 {rarityRow[b.rarity]}"
            style={b.rarity === 'legendary' ? 'box-shadow: 0 0 10px rgba(245,158,11,0.25)' : ''}
          >
            <Icon size={20} strokeWidth={1.8} class={rarityIcon[b.rarity]} />
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-ink">{b.name}</p>
              <p class="text-xs text-ink-mute capitalize">{b.rarity}</p>
            </div>
            <span class="shrink-0 text-xs text-ink-soft">{formatDate(b.earned_date)}</span>
          </div>
        {/each}
      </div>
    {:else}
      <p class="text-[13px] text-ink-soft">Noch keine Badges in diesem Zeitraum.</p>
    {/if}
  {/if}
</Modal>
