<script lang="ts">
  import { activePeriod, PERIOD_OPTIONS } from '$lib/stores/period.svelte';

  interface Props {
    title: string;
    subtitle?: string;
  }
  let { title, subtitle }: Props = $props();
</script>

<header class="flex items-end justify-between gap-6 pb-6">
  <div>
    <h1 class="font-display text-3xl font-medium tracking-tight text-ink">{title}</h1>
    {#if subtitle}
      <p class="mt-1 text-sm text-ink-soft">{subtitle}</p>
    {/if}
  </div>

  <!-- Period switch — drives the global activePeriod store and reloads data. -->
  <div class="flex items-center gap-1 rounded-full bg-card p-1">
    {#each PERIOD_OPTIONS as opt (opt.value)}
      <button
        onclick={() => activePeriod.set(opt.value)}
        class="rounded-full px-3.5 py-1.5 text-[13px] font-medium transition-colors duration-150
          {$activePeriod === opt.value
          ? 'bg-[#1B1F3B] text-white'
          : 'bg-transparent text-[#6B7280] hover:bg-paper'}"
      >
        {opt.label}
      </button>
    {/each}
  </div>
</header>
