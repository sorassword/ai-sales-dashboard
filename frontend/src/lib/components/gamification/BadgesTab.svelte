<script lang="ts">
  import type { BadgeDefinition, EarnedBadge } from '$lib/types';
  import { relativeDate, slugify } from '$lib/utils/format';
  import { openModal } from '$lib/stores/modal.svelte';
  import { Euro, Flame, Brain, Star, Zap, Crown, Clock, Trophy, Award } from 'lucide-svelte';

  interface Props {
    definitions: BadgeDefinition[];
    recentBadges: EarnedBadge[];
  }
  let { definitions, recentBadges }: Props = $props();

  type Filter = 'all' | 'common' | 'rare' | 'legendary';
  let activeFilter = $state<Filter>('all');

  let filtered = $derived(
    activeFilter === 'all' ? definitions : definitions.filter((d) => d.rarity === activeFilter)
  );

  const FILTERS: { value: Filter; label: string; active: string }[] = [
    { value: 'all', label: 'Alle', active: 'bg-[#1B1F3B] text-white' },
    { value: 'common', label: 'Common', active: 'bg-[#6B7280] text-white' },
    { value: 'rare', label: 'Rare', active: 'bg-[#7C3AED] text-white' },
    { value: 'legendary', label: 'Legendary', active: 'bg-[#D97706] text-white' }
  ];

  // icon_key → lucide icon component.
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

  // --- rarity-driven styling --------------------------------------------- //
  const cardStyle = (rarity: string) => {
    if (rarity === 'legendary')
      return 'border:2px solid #F59E0B;background:linear-gradient(135deg,#FFFBEB,#FEF3C7);box-shadow:0 0 16px rgba(245,158,11,0.25);';
    if (rarity === 'rare')
      return 'border:1px solid #A78BFA;background:linear-gradient(135deg,#FAF5FF,#EDE9FE);';
    return 'border:1px solid #E5E7EB;background:#ffffff;';
  };
  const iconColor: Record<string, string> = {
    common: 'text-[#6B7280]',
    rare: 'text-[#7C3AED]',
    legendary: 'text-[#D97706]'
  };
  const barColor: Record<string, string> = {
    common: '#6B7280',
    rare: '#7C3AED',
    legendary: '#F59E0B'
  };
  const rarityPill: Record<string, string> = {
    common: 'bg-gray-100 text-gray-600',
    rare: 'bg-[#EDE9FE] text-[#7C3AED]',
    legendary: 'bg-[#FEF3C7] text-[#B45309]'
  };
  const cornerLabel: Record<string, string> = {
    rare: 'text-[#7C3AED]',
    legendary: 'text-[#D97706]'
  };

  // --- recent badges: deterministic colored avatar with white initials --- //
  const PALETTE = ['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#14B8A6', '#3B82F6', '#A78BFA', '#F97316'];
  const colorFor = (name: string) =>
    PALETTE[[...name].reduce((a, c) => a + c.charCodeAt(0), 0) % PALETTE.length];
  const initialsFor = (name: string) => {
    const p = name.split(' ');
    return ((p[0]?.[0] ?? '') + (p[p.length - 1]?.[0] ?? '')).toUpperCase();
  };
</script>

<!-- ============================== FILTER ROW ============================== -->
<div class="flex flex-wrap gap-2">
  {#each FILTERS as f (f.value)}
    <button
      class="rounded-full px-4 py-1.5 text-sm font-medium transition-colors duration-150
        {activeFilter === f.value ? f.active : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}"
      onclick={() => (activeFilter = f.value)}
    >
      {f.label}
    </button>
  {/each}
</div>

<!-- ========================= BADGE DEFINITION GRID ========================= -->
<div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
  {#each filtered as d (d.name)}
    {@const Icon = iconFor(d.icon_key)}
    <div class="relative flex min-h-[200px] flex-col rounded-xl p-5" style={cardStyle(d.rarity)}>
      {#if d.rarity !== 'common'}
        <span class="absolute top-3 right-3 text-[10px] font-bold tracking-wider uppercase {cornerLabel[d.rarity]}">
          {d.rarity}
        </span>
      {/if}

      <!-- top row: icon + name + rarity pill -->
      <div class="flex items-start gap-3 pr-16">
        <Icon size={32} strokeWidth={1.6} class={iconColor[d.rarity]} />
        <div class="min-w-0 flex-1">
          <h3 class="text-lg leading-tight font-bold text-ink">{d.name}</h3>
        </div>
        <span class="rounded-full px-2.5 py-0.5 text-[11px] font-semibold capitalize {rarityPill[d.rarity]}">
          {d.rarity}
        </span>
      </div>

      <!-- condition text -->
      <p class="mt-2 text-sm font-medium text-ink">{d.condition_text}</p>
      <p class="mt-1 text-xs text-gray-500">{d.condition_detail}</p>

      <!-- progress row -->
      <div class="mt-auto pt-4">
        <div class="flex items-center justify-between text-xs text-ink-soft">
          <span>{d.earned_count} von {d.total_employees} Mitarbeitern</span>
          <span class="tnum font-medium">{d.earn_rate_pct}%</span>
        </div>
        <div class="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-gray-200">
          <div
            class="h-full rounded-full"
            style="width:{d.earn_rate_pct}%;background:{barColor[d.rarity]};"
          ></div>
        </div>
      </div>

      <!-- footer -->
      <p class="mt-3 text-xs text-gray-400">
        Zuletzt verdient: {d.last_earned_by}{#if d.last_earned_date} · {relativeDate(d.last_earned_date)}{/if}
      </p>
    </div>
  {/each}
</div>

<!-- ========================= RECENT BADGES SECTION ========================= -->
<div class="mt-8">
  <h3 class="font-display mb-3 text-lg font-medium text-ink">Zuletzt verdiente Badges</h3>
  <div class="overflow-hidden rounded-xl border border-gray-100">
    {#each recentBadges as b, i (b.badge.id + b.employee_id)}
      {@const Icon = iconFor(b.badge.icon_key)}
      <button
        class="flex min-h-[56px] w-full cursor-pointer items-center gap-4 px-4 py-3 text-left transition-colors duration-150 hover:bg-gray-50 {i %
          2 ===
        1
          ? 'bg-[#FAFAFA]'
          : 'bg-white'}"
        onclick={() => openModal('employee-detail', { employee_id: slugify(b.employee_name) })}
      >
        <!-- avatar 40px, colored bg, white initials -->
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
          style="background:{colorFor(b.employee_name)};"
        >
          {initialsFor(b.employee_name)}
        </div>

        <!-- name (EarnedBadge carries no store, so just the name) -->
        <div class="min-w-0 flex-1">
          <p class="font-medium text-ink">{b.employee_name}</p>
        </div>

        <!-- badge icon + name + rarity (one line, no truncation) -->
        <div class="flex shrink-0 items-center gap-2 whitespace-nowrap">
          <Icon size={16} strokeWidth={1.8} class={iconColor[b.badge.rarity]} />
          <span class="text-sm font-medium text-ink">{b.badge.name}</span>
          <span class="rounded-full px-2.5 py-0.5 text-[11px] font-semibold capitalize {rarityPill[b.badge.rarity]}">
            {b.badge.rarity}
          </span>
        </div>

        <!-- date far right -->
        <span class="shrink-0 text-xs text-ink-soft">{relativeDate(b.earned_on)}</span>
      </button>
    {/each}
  </div>
</div>
