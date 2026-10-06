<script lang="ts">
  import type { ArenaEntry, LeaderboardArenaRow, PointsBreakdown } from '$lib/types';
  import { formatEur, formatNum, formatHoursValue } from '$lib/utils/format';
  import { openModal } from '$lib/stores/modal.svelte';
  import { Info, Flame } from 'lucide-svelte';

  interface Props {
    podium: ArenaEntry[];
    leaderboard: LeaderboardArenaRow[];
  }
  let { podium, leaderboard }: Props = $props();

  // Collapsible "how are points calculated" box.
  let showFormula = $state(false);

  // --- Podium styling (per rank) ----------------------------------------- //
  const MEDAL: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' };
  const blockHeight = (rank: number) => (rank === 1 ? 180 : rank === 2 ? 140 : 110);
  const blockStyle = (rank: number) => {
    if (rank === 1)
      return 'background:linear-gradient(180deg,#FEF3C7,#FDE68A);border:2px solid #F59E0B;';
    if (rank === 2)
      return 'background:linear-gradient(180deg,#F3F4F6,#E5E7EB);border:2px solid #9CA3AF;';
    return 'background:linear-gradient(180deg,#FFF7ED,#FED7AA);border:2px solid #F97316;';
  };
  // Desktop visual order: rank2 | rank1 | rank3. Mobile: natural (rank1 first).
  const desktopOrder = (rank: number) => (rank === 1 ? 'md:order-2' : rank === 2 ? 'md:order-1' : 'md:order-3');

  // --- Breakdown chips (podium) ------------------------------------------ //
  const chips = (b: PointsBreakdown) => [
    { icon: '💰', value: b.from_revenue, label: 'Aus Umsatz' },
    { icon: '🤖', value: b.from_bot, label: 'Aus Bot-Zeit' },
    { icon: '📝', value: b.from_quiz, label: 'Aus Quizzes' },
    { icon: '🔥', value: b.from_streak, label: 'Aus Streak' }
  ];

  // --- Mini stacked bar (leaderboard AUFSCHLÜSSELUNG) -------------------- //
  const BAR_W = 120;
  const BAR_H = 8;
  const SEG_COLORS = {
    from_revenue: '#6366F1',
    from_bot: '#14B8A6',
    from_quiz: '#F59E0B',
    from_streak: '#EC4899'
  } as const;

  /** Returns [{x, w, color}] segments scaled to BAR_W. */
  function segments(b: PointsBreakdown) {
    const total = b.total || 1;
    const parts: { key: keyof typeof SEG_COLORS; value: number }[] = [
      { key: 'from_revenue', value: b.from_revenue },
      { key: 'from_bot', value: b.from_bot },
      { key: 'from_quiz', value: b.from_quiz },
      { key: 'from_streak', value: b.from_streak }
    ];
    let x = 0;
    return parts.map((p) => {
      const w = (p.value / total) * BAR_W;
      const seg = { x, w, color: SEG_COLORS[p.key] };
      x += w;
      return seg;
    });
  }

  // --- Leaderboard row styling ------------------------------------------- //
  const rowTint = (rank: number, i: number) => {
    if (rank === 1) return 'bg-[#FEF3C7]';
    if (rank === 2) return 'bg-[#F9FAFB]';
    if (rank === 3) return 'bg-[#FFF7ED]';
    return i % 2 === 1 ? 'bg-[#FAFAFA]' : 'bg-white';
  };
  const rankColor = (rank: number) =>
    rank === 1 ? 'text-[#D97706]' : rank <= 3 ? 'font-bold text-ink' : 'text-ink-soft';
</script>

<!-- ============================ SECTION A — PODIUM ============================ -->
<section
  class="rounded-[var(--radius-card)] border border-line bg-card p-6 shadow-[0_1px_2px_rgba(27,31,59,0.04)]"
>
  <div class="flex flex-col items-center gap-6 md:flex-row md:items-end md:justify-center md:gap-6">
    {#each podium as p (p.employee_id)}
      <div class="flex w-[200px] flex-col items-center {desktopOrder(p.rank)}">
        <!-- medal + avatar above the block -->
        <div class="mb-1 text-2xl">{MEDAL[p.rank] ?? ''}</div>
        <div
          class="mb-2 flex h-12 w-12 items-center justify-center rounded-full text-lg font-bold text-white shadow-sm"
          style="background:{p.avatar_color};"
        >
          {p.initials}
        </div>

        <!-- the podium block -->
        <div
          class="flex w-full flex-col items-center justify-center rounded-xl px-3 text-center"
          style="height:{blockHeight(p.rank)}px;{blockStyle(p.rank)}"
        >
          <p class="text-sm font-semibold text-ink">{p.name}</p>
          <p class="text-xs text-ink-soft">{p.store_name}</p>
          <p class="tnum mt-2 text-2xl font-bold text-ink">{formatNum(p.points)}</p>
          <p class="text-xs text-ink-soft">Punkte</p>
        </div>

        <!-- breakdown chips below the block -->
        <div class="mt-2 flex flex-wrap justify-center gap-1">
          {#each chips(p.points_breakdown) as c (c.label)}
            <span
              class="tnum cursor-default rounded-full bg-gray-100 px-2 py-0.5 text-[11px] text-gray-600"
              title={c.label}
            >
              {c.icon} {formatNum(c.value)}
            </span>
          {/each}
        </div>
      </div>
    {/each}
  </div>

  <!-- score formula explanation (collapsible) -->
  <div class="mt-6 flex justify-center">
    <div class="w-full max-w-2xl">
      <button
        class="inline-flex items-center gap-1.5 text-sm text-ink-soft transition-colors duration-150 hover:text-ink"
        onclick={() => (showFormula = !showFormula)}
      >
        <Info size={15} strokeWidth={1.8} />
        Wie werden Punkte berechnet?
      </button>
      {#if showFormula}
        <div class="mt-2 rounded-lg bg-gray-100 p-4">
          <code class="block font-mono text-[13px] leading-relaxed text-ink">
            Punkte = Umsatz (€ ÷ 100) + Bot-Minuten × 2 + Quiz-Score × 10 + Streak-Tage × 5
          </code>
        </div>
      {/if}
    </div>
  </div>
</section>

<!-- ========================= SECTION B — LEADERBOARD ========================= -->
<section
  class="mt-4 overflow-hidden rounded-[var(--radius-card)] border border-line bg-card shadow-[0_1px_2px_rgba(27,31,59,0.04)]"
>
  <div class="overflow-x-auto">
    <table class="w-full border-collapse text-sm">
      <thead>
        <tr class="text-left text-[11px] tracking-wide text-ink-mute uppercase">
          <th class="px-4 py-3 font-medium">#</th>
          <th class="px-4 py-3 font-medium">Mitarbeiter</th>
          <th class="px-4 py-3 text-right font-medium">Punkte</th>
          <th class="px-4 py-3 font-medium">Aufschlüsselung</th>
          <th class="px-4 py-3 text-right font-medium">Umsatz</th>
          <th class="px-4 py-3 text-right font-medium">Bot-Zeit</th>
          <th class="px-4 py-3 text-right font-medium">Streak</th>
          <th class="px-4 py-3 text-right font-medium">Badges</th>
        </tr>
      </thead>
      <tbody>
        {#each leaderboard as row, i (row.employee_id)}
          <tr
            class="cursor-pointer border-t border-line/70 transition-colors duration-150 hover:brightness-95 {rowTint(row.rank, i)}"
            onclick={() => openModal('employee-detail', { employee_id: row.employee_id })}
          >
            <!-- rank + change -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <span class="tnum text-base {rankColor(row.rank)}">{row.rank}</span>
                {#if row.rank_change > 0}
                  <span class="tnum text-[11px] font-medium text-positive">↑{row.rank_change}</span>
                {:else if row.rank_change < 0}
                  <span class="tnum text-[11px] font-medium text-negative">↓{Math.abs(row.rank_change)}</span>
                {:else}
                  <span class="text-[11px] text-ink-mute">—</span>
                {/if}
              </div>
            </td>

            <!-- avatar + name + store -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-3">
                <div
                  class="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold text-white"
                  style="background:{row.avatar_color};"
                >
                  {row.initials}
                </div>
                <div class="leading-tight">
                  <p class="font-medium text-ink">{row.name}</p>
                  <p class="text-[12px] text-ink-soft">{row.store_name}</p>
                </div>
              </div>
            </td>

            <!-- points -->
            <td class="tnum px-4 py-3 text-right font-semibold text-ink">{formatNum(row.points)}</td>

            <!-- breakdown stacked bar -->
            <td class="px-4 py-3">
              <svg width={BAR_W} height={BAR_H} viewBox="0 0 {BAR_W} {BAR_H}" class="rounded-full">
                {#each segments(row.points_breakdown) as s}
                  <rect x={s.x} y="0" width={Math.max(0, s.w)} height={BAR_H} fill={s.color} />
                {/each}
              </svg>
            </td>

            <!-- revenue -->
            <td class="tnum px-4 py-3 text-right text-ink-soft">{formatEur(row.revenue)}</td>

            <!-- bot hours -->
            <td class="tnum px-4 py-3 text-right text-ink-soft">{formatHoursValue(row.bot_hours)}</td>

            <!-- streak -->
            <td class="px-4 py-3 text-right">
              <span class="inline-flex items-center gap-1 text-ink-soft">
                {#if row.streak_days > 14}<Flame size={13} class="text-signal" />{/if}
                <span class="tnum text-[13px]">{row.streak_days}d</span>
              </span>
            </td>

            <!-- badge count -->
            <td class="tnum px-4 py-3 text-right text-ink-soft">{row.badge_count}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</section>
