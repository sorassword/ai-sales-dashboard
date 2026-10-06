<script lang="ts">
  import Topbar from '$lib/components/Topbar.svelte';
  import ArenaTab from '$lib/components/gamification/ArenaTab.svelte';
  import BadgesTab from '$lib/components/gamification/BadgesTab.svelte';
  import { isReloading, periodLabelStore } from '$lib/stores/period.svelte';
  import { Trophy, Award } from 'lucide-svelte';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  let arena = $derived(data.arena);
  let definitions = $derived(data.badgeDefinitions.badges);
  let recentBadges = $derived(data.badges);
  let subtitle = $derived(`Leaderboard, Badges & Quiz-Training · ${$periodLabelStore}`);

  // Tab state — switching tabs never reloads data (both sets already loaded).
  let activeTab = $state<'arena' | 'badges'>('arena');
</script>

<Topbar title="Gamification" {subtitle} />

<!-- Tab switcher (left-aligned, below the title) -->
<div class="mb-4 flex gap-2">
  <button
    class="inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-medium transition-colors duration-150
      {activeTab === 'arena' ? 'bg-[#1B1F3B] text-white' : 'bg-transparent text-ink-mute hover:bg-card'}"
    onclick={() => (activeTab = 'arena')}
  >
    <Trophy size={15} strokeWidth={1.8} /> Arena
  </button>
  <button
    class="inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-medium transition-colors duration-150
      {activeTab === 'badges' ? 'bg-[#1B1F3B] text-white' : 'bg-transparent text-ink-mute hover:bg-card'}"
    onclick={() => (activeTab = 'badges')}
  >
    <Award size={15} strokeWidth={1.8} /> Badges
  </button>
</div>

<!-- Weekly highlight banner (shown on both tabs) -->
<div
  class="banner-pulse mb-4 w-full rounded-xl px-5 py-3.5 text-sm text-[#78350F]"
  style="background:linear-gradient(90deg,#FEF3C7,#FDE68A);"
>
  👑 <span class="font-semibold">Diese Woche: {arena.weekly_highlight.name}</span>
  — {arena.weekly_highlight.highlight_reason}
</div>

<div class="transition-opacity duration-200" class:opacity-50={$isReloading}>
  {#if activeTab === 'arena'}
    <ArenaTab podium={arena.podium} leaderboard={arena.leaderboard} />
  {:else}
    <BadgesTab {definitions} {recentBadges} />
  {/if}
</div>

<style>
  /* Subtle pulsing 4px left border on the weekly highlight banner. */
  .banner-pulse {
    border-left: 4px solid #f59e0b;
    animation: borderPulse 2.4s ease-in-out infinite;
  }
  @keyframes borderPulse {
    0%,
    100% {
      border-left-color: #f59e0b;
    }
    50% {
      border-left-color: #fcd34d;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .banner-pulse {
      animation: none;
    }
  }
</style>
