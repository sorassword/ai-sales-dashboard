<script lang="ts">
  import { TrendingUp, TrendingDown } from 'lucide-svelte';
  import { formatPct } from '$lib/utils/format';
  import { onMount, type Snippet } from 'svelte';

  interface Props {
    label: string;
    value: string;
    delta?: number;
    /** Show this metric as the highlighted "hero" KPI (the ROI number). */
    hero?: boolean;
    caption?: string;
    /** Optional extra content rendered below the delta row (e.g. a progress bar). */
    children?: Snippet;
    /** Entrance-animation delay in ms (for staggering a row of cards). */
    delay?: number;
  }
  let { label, value, delta, hero = false, caption, children, delay = 0 }: Props = $props();

  let positive = $derived(delta === undefined || delta >= 0);

  // Fade + rise in on mount, staggered by `delay`.
  let entered = $state(false);
  onMount(() => {
    const id = requestAnimationFrame(() => (entered = true));
    return () => cancelAnimationFrame(id);
  });
</script>

<div
  class="kpi-enter rounded-[var(--radius-card)] border p-5
    {entered ? 'is-visible' : ''}
    {hero
    ? 'border-ink bg-ink text-card'
    : 'border-line bg-card text-ink shadow-[0_1px_2px_rgba(27,31,59,0.04)]'}"
  style="--enter-delay:{delay}ms"
>
  <p
    class="text-[12px] font-medium tracking-wide uppercase
      {hero ? 'text-brass-soft' : 'text-ink-mute'}"
  >
    {label}
  </p>

  <p class="tnum mt-3 text-3xl font-semibold {hero ? 'text-card' : 'text-ink'}">
    {value}
  </p>

  <div class="mt-2 flex items-center gap-2">
    {#if delta !== undefined}
      <span
        class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[12px] font-semibold
          {positive
          ? hero
            ? 'bg-card/15 text-brass-soft'
            : 'bg-positive/10 text-positive'
          : 'bg-negative/10 text-negative'}"
      >
        {#if positive}<TrendingUp size={12} />{:else}<TrendingDown size={12} />{/if}
        {formatPct(delta)}
      </span>
    {/if}
    {#if caption}
      <span class="text-[12px] {hero ? 'text-brass-soft/80' : 'text-ink-soft'}">{caption}</span>
    {/if}
  </div>

  {#if children}{@render children()}{/if}
</div>

<style>
  .kpi-enter {
    opacity: 0;
    transform: translateY(8px);
    transition:
      opacity 400ms ease-out,
      transform 400ms ease-out;
    transition-delay: var(--enter-delay, 0ms);
  }
  .kpi-enter.is-visible {
    opacity: 1;
    transform: translateY(0);
  }
</style>
