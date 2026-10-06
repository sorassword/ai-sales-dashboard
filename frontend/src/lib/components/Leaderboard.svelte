<script lang="ts">
  import type { LeaderboardRow } from '$lib/types';
  import { formatEurCompact, formatNum, slugify } from '$lib/utils/format';
  import { ChevronUp, ChevronDown, Minus, Flame, Crown } from 'lucide-svelte';
  import Avatar from '$lib/components/ui/Avatar.svelte';
  import { openModal } from '$lib/stores/modal.svelte';

  interface Props {
    rows: LeaderboardRow[];
    limit?: number;
  }
  let { rows, limit }: Props = $props();
  let visible = $derived(limit ? rows.slice(0, limit) : rows);

  const medal = (rank: number) =>
    rank === 1 ? 'text-brass' : rank === 2 ? 'text-ink-soft' : rank === 3 ? 'text-[#b08d57]' : 'text-ink-mute';

  // Podium row tints (rank 1 gold, 2 silver, 3 bronze).
  const rowTint = (rank: number) =>
    rank === 1 ? 'bg-[#FEF3C7]' : rank === 2 ? 'bg-[#F9FAFB]' : rank === 3 ? 'bg-[#FFF7ED]' : '';
</script>

<div class="overflow-hidden">
  <table class="w-full border-collapse text-sm">
    <thead>
      <tr class="text-left text-[11px] tracking-wide text-ink-mute uppercase">
        <th class="py-2 pr-2 font-medium">#</th>
        <th class="py-2 font-medium">Mitarbeiter</th>
        <th class="py-2 text-right font-medium">Punkte</th>
        <th class="hidden py-2 text-right font-medium sm:table-cell">Umsatz</th>
        <th class="hidden py-2 text-right font-medium md:table-cell">Streak</th>
        <th class="py-2 pl-2 text-right font-medium"></th>
      </tr>
    </thead>
    <tbody>
      {#each visible as row (row.employee.id)}
        <tr
          class="cursor-pointer border-t border-line/70 transition-colors duration-150 hover:bg-paper/70 {rowTint(row.rank)}"
          onclick={() => openModal('employee-detail', { employee_id: slugify(row.employee.name) })}
        >
          <td class="py-3 pr-2">
            <span class="tnum text-base font-semibold {medal(row.rank)}">{row.rank}</span>
          </td>
          <td class="py-3">
            <div class="flex items-center gap-3">
              <Avatar initials={row.employee.initials} hue={row.employee.avatar_hue} />
              <div class="leading-tight">
                <p class="flex items-center gap-1.5 text-ink {row.rank === 1 ? 'text-base font-semibold' : 'font-medium'}">
                  {#if row.rank === 1}<Crown size={15} class="text-brass" />{/if}{row.employee.name}
                </p>
                <p class="text-[12px] text-ink-soft">{row.employee.store_name}</p>
              </div>
            </div>
          </td>
          <td class="tnum py-3 text-right font-semibold text-ink">{formatNum(row.points)}</td>
          <td class="tnum hidden py-3 text-right text-ink-soft sm:table-cell">
            {formatEurCompact(row.revenue)}
          </td>
          <td class="hidden py-3 text-right md:table-cell">
            <span class="inline-flex items-center gap-1 text-ink-soft">
              {#if row.streak_days > 0}<Flame size={13} class="text-signal" />{/if}
              <span class="tnum text-[13px]">{row.streak_days}d</span>
            </span>
          </td>
          <td class="py-3 pl-2 text-right">
            {#if row.movement > 0}
              <span class="inline-flex items-center text-positive"><ChevronUp size={16} />{row.movement}</span>
            {:else if row.movement < 0}
              <span class="inline-flex items-center text-negative"><ChevronDown size={16} />{Math.abs(row.movement)}</span>
            {:else}
              <Minus size={14} class="inline text-ink-mute" />
            {/if}
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
