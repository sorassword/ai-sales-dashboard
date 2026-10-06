<script lang="ts">
  interface Row {
    label: string;
    value: number;
    display?: string;
  }
  interface Props {
    rows: Row[];
    color?: string;
  }
  let { rows, color = 'var(--color-ink)' }: Props = $props();

  let max = $derived(Math.max(...rows.map((r) => r.value), 1));
</script>

<ul class="flex flex-col gap-3">
  {#each rows as row (row.label)}
    <li>
      <div class="mb-1 flex items-baseline justify-between gap-3">
        <span class="text-[13px] font-medium text-ink">{row.label}</span>
        <span class="tnum text-[13px] text-ink-soft">{row.display ?? row.value}</span>
      </div>
      <div class="h-2 overflow-hidden rounded-full bg-paper">
        <div
          class="h-full rounded-full transition-[width] duration-700"
          style="width:{(row.value / max) * 100}%;background:{color}"
        ></div>
      </div>
    </li>
  {/each}
</ul>
