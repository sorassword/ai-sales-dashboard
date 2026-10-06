<script lang="ts">
  import type { Snippet } from 'svelte';
  interface Props {
    title?: string;
    hint?: string;
    class?: string;
    children: Snippet;
    actions?: Snippet;
  }
  let { title, hint, class: klass = '', children, actions }: Props = $props();
</script>

<section
  class="rounded-[var(--radius-card)] border border-line bg-card p-5 shadow-[0_1px_2px_rgba(27,31,59,0.04)] transition-[transform,box-shadow] duration-150 hover:-translate-y-0.5 hover:shadow-[0_4px_16px_rgba(0,0,0,0.08)] {klass}"
>
  {#if title || actions}
    <div class="mb-4 flex items-start justify-between gap-4">
      <div>
        {#if title}<h2 class="font-display text-lg font-medium text-ink">{title}</h2>{/if}
        {#if hint}<p class="mt-0.5 text-[13px] text-ink-soft">{hint}</p>{/if}
      </div>
      {#if actions}{@render actions()}{/if}
    </div>
  {/if}
  {@render children()}
</section>
