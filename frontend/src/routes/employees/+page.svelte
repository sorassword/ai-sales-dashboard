<script lang="ts">
  import Topbar from '$lib/components/Topbar.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Avatar from '$lib/components/ui/Avatar.svelte';
  import { formatEur, formatHours } from '$lib/utils/format';
  import { isReloading, periodLabelStore } from '$lib/stores/period.svelte';
  import { openModal } from '$lib/stores/modal.svelte';
  import { slugify } from '$lib/utils/format';
  import { Flame } from 'lucide-svelte';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  type SortKey = 'revenue' | 'bot_minutes' | 'learning_score' | 'quiz_accuracy';
  let sortKey = $state<SortKey>('revenue');

  let rows = $derived([...data.metrics].sort((a, b) => b[sortKey] - a[sortKey]));
  let subtitle = $derived(`${data.metrics.length} getrackte Mitarbeiter:innen · ${$periodLabelStore}`);

  const cols: { key: SortKey; label: string }[] = [
    { key: 'revenue', label: 'Umsatz' },
    { key: 'bot_minutes', label: 'Bot-Zeit' },
    { key: 'learning_score', label: 'Lernscore' },
    { key: 'quiz_accuracy', label: 'Quiz' }
  ];
</script>

<Topbar title="Mitarbeiter" {subtitle} />

<div class="transition-opacity duration-200" class:opacity-50={$isReloading}>
  <Card>
    <table class="w-full border-collapse text-sm">
      <thead>
        <tr class="text-left text-[11px] tracking-wide text-ink-mute uppercase">
          <th class="py-2 font-medium">Name</th>
          {#each cols as c (c.key)}
            <th class="py-2 text-right font-medium">
              <button
                class="transition-colors hover:text-ink {sortKey === c.key ? 'text-ink' : ''}"
                onclick={() => (sortKey = c.key)}
              >
                {c.label}{sortKey === c.key ? ' ↓' : ''}
              </button>
            </th>
          {/each}
          <th class="py-2 text-right font-medium">Streak</th>
          <th class="py-2 text-right font-medium">Badges</th>
        </tr>
      </thead>
      <tbody>
        {#each rows as m (m.employee.id)}
          <tr
            class="cursor-pointer border-t border-line/70 transition-colors duration-150 hover:bg-paper/70"
            onclick={() => openModal('employee-detail', { employee_id: slugify(m.employee.name) })}
          >
            <td class="py-3">
              <div class="flex items-center gap-3">
                <Avatar initials={m.employee.initials} hue={m.employee.avatar_hue} size={30} />
                <div class="leading-tight">
                  <p class="font-medium text-ink">{m.employee.name}</p>
                  <p class="text-[12px] text-ink-soft">{m.employee.role} · {m.employee.store_name}</p>
                </div>
              </div>
            </td>
            <td class="tnum py-3 text-right font-medium text-ink">{formatEur(m.revenue)}</td>
            <td class="tnum py-3 text-right text-ink-soft">{formatHours(m.bot_minutes)}</td>
            <td class="tnum py-3 text-right text-ink-soft">{m.learning_score}</td>
            <td class="tnum py-3 text-right text-ink-soft">{m.quiz_accuracy}%</td>
            <td class="py-3 text-right">
              <span class="tnum inline-flex items-center justify-end gap-1 text-ink-soft">
                {#if m.streak_days > 0}<Flame size={13} class="text-signal" />{/if}{m.streak_days}d
              </span>
            </td>
            <td class="tnum py-3 text-right text-ink-soft">{m.badges}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </Card>
</div>
