<script lang="ts">
  import Topbar from '$lib/components/Topbar.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import KpiCard from '$lib/components/ui/KpiCard.svelte';
  import LineChart from '$lib/components/charts/LineChart.svelte';
  import ScatterChart from '$lib/components/charts/ScatterChart.svelte';
  import BarList from '$lib/components/charts/BarList.svelte';
  import Leaderboard from '$lib/components/Leaderboard.svelte';
  import BadgeWall from '$lib/components/BadgeWall.svelte';
  import { formatEurCompact, formatHours, formatNum } from '$lib/utils/format';
  import { isReloading, periodLabelStore } from '$lib/stores/period.svelte';
  import { openModal } from '$lib/stores/modal.svelte';
  import { ArrowRight } from 'lucide-svelte';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  // Reactive views onto the loaded data so they update when the period reloads.
  let kpis = $derived(data.kpis);
  let revenueTrend = $derived(data.revenueTrend);
  let botTrend = $derived(data.botTrend);
  let correlation = $derived(data.correlation);
  let digest = $derived(data.digest);
  let leaderboard = $derived(data.leaderboard);
  let badges = $derived(data.badges);
  let stores = $derived(data.stores);

  let subtitle = $derived(`${$periodLabelStore} · alle Filialen · Modehaus (Demo-Daten)`);

  // Bot-time benchmark presentation.
  const de1 = (v: number) => v.toLocaleString('de-DE', { maximumFractionDigits: 1 });
  let botPct = $derived(kpis.bot_hours_pct_of_target);
  let botBarColor = $derived(botPct < 85 ? '#DC2626' : botPct <= 100 ? 'var(--color-brass)' : '#16A34A');

  let questionRows = $derived(
    digest.top_questions.map((q) => ({ label: q.topic, value: q.count, display: String(q.count) }))
  );
  let storeRows = $derived(
    stores.map((s) => ({
      label: s.store.name.replace('Modehaus ', ''),
      value: s.revenue,
      display: formatEurCompact(s.revenue)
    }))
  );
</script>

<Topbar title="Übersicht" {subtitle} />

<div class="transition-opacity duration-200" class:opacity-50={$isReloading}>
  <!-- KPI row -->
  <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
    <KpiCard label="Umsatz gesamt" value={formatEurCompact(kpis.total_revenue)} delta={kpis.revenue_delta_pct} caption="vs. Vorperiode" delay={0} />
    <KpiCard label="Bot-Zeit" value={formatHours(kpis.bot_minutes)} delta={kpis.bot_minutes_delta_pct} caption={kpis.bot_hours_benchmark_label} delay={80}>
      {#snippet children()}
        <div class="mt-3">
          <div class="h-1.5 w-full overflow-hidden rounded-full bg-paper">
            <div
              class="h-full rounded-full transition-[width] duration-500"
              style="width:{Math.min(botPct, 100)}%;background:{botBarColor}"
            ></div>
          </div>
          <p class="mt-1.5 text-[11px] text-ink-soft">{de1(botPct)}% von Ziel ({de1(kpis.bot_hours_target)} h)</p>
          <p class="text-[11px] text-ink-mute">Ø {de1(kpis.bot_hours_per_employee)} h / Mitarbeiter:in</p>
        </div>
      {/snippet}
    </KpiCard>
    <KpiCard label="Ø Lernscore" value={`${kpis.avg_learning_score}/100`} delta={kpis.learning_score_delta_pct} caption="vs. Vorperiode" delay={160} />
    <KpiCard label="Aktive Nutzer" value={formatNum(kpis.active_users)} delta={kpis.active_users_delta_pct} caption="im Assistenten" delay={240} />
  </div>

  <!-- Trend + correlation -->
  <div class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
    <Card title="Umsatzentwicklung" hint="Netto · pro Zeitraum">
      {#snippet actions()}
        <button
          class="inline-flex cursor-pointer items-center gap-1 text-[13px] font-medium text-brass transition-colors duration-150 hover:underline"
          onclick={() => openModal('revenue-trend', { period: data.period, detail: data.revenueTrendDetail })}
        >
          Details <ArrowRight size={14} />
        </button>
      {/snippet}
      <button
        class="block w-full cursor-pointer rounded-lg text-left transition-colors duration-150 hover:bg-gray-50"
        onclick={() => openModal('revenue-trend', { period: data.period, detail: data.revenueTrendDetail })}
      >
        <LineChart data={revenueTrend} valueFormat={formatEurCompact} color="var(--color-brass)" />
      </button>
    </Card>

    <Card title="Bot-Nutzung → Umsatz" hint={correlation.headline}>
      {#snippet actions()}
        <button
          class="inline-flex cursor-pointer items-center gap-1 text-[13px] font-medium text-brass transition-colors duration-150 hover:underline"
          onclick={() => openModal('correlation', { period: data.period, detail: data.correlationDetail })}
        >
          Details <ArrowRight size={14} />
        </button>
      {/snippet}
      <button
        class="block w-full cursor-pointer rounded-lg text-left transition-colors duration-150 hover:bg-gray-50"
        onclick={() => openModal('correlation', { period: data.period, detail: data.correlationDetail })}
      >
        <ScatterChart points={correlation.points} />
      </button>
      <p class="mt-3 text-[13px] text-ink-soft">
        Jeder Punkt ist ein:e Mitarbeiter:in. Die gestrichelte Linie zeigt den Trend:
        <span class="font-medium text-ink">r = {correlation.pearson_r}</span>.
      </p>
    </Card>
  </div>

  <!-- Bot-minutes trend + store split -->
  <div class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
    <Card title="Trainings- & Beratungszeit" hint="Bot-Minuten · Team gesamt">
      {#snippet actions()}
        <button
          class="inline-flex cursor-pointer items-center gap-1 text-[13px] font-medium text-brass transition-colors duration-150 hover:underline"
          onclick={() => openModal('bot-trend', { period: data.period, detail: data.botTrendDetail })}
        >
          Details <ArrowRight size={14} />
        </button>
      {/snippet}
      <button
        class="block w-full cursor-pointer rounded-lg text-left transition-colors duration-150 hover:bg-gray-50"
        onclick={() => openModal('bot-trend', { period: data.period, detail: data.botTrendDetail })}
      >
        <LineChart data={botTrend} valueFormat={(v) => `${formatNum(v)} min`} color="var(--color-ink)" />
      </button>
    </Card>

    <Card title="Umsatz nach Filiale" hint="Anteil am Gesamtumsatz der Kette">
      <BarList rows={storeRows} color="var(--color-ink)" />
    </Card>
  </div>

  <!-- Digest + leaderboard -->
  <div class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-5">
    <Card class="lg:col-span-2" title="Weekly Digest" hint={digest.week_label}>
      {#snippet actions()}
        <button
          class="inline-flex cursor-pointer items-center gap-1 text-[13px] font-medium text-brass transition-colors duration-150 hover:underline"
          onclick={() => openModal('digest', { period: data.period, detail: data.digestDetail })}
        >
          Details <ArrowRight size={14} />
        </button>
      {/snippet}
      <div class="mb-5 flex items-end gap-4 rounded-xl border border-line bg-paper/60 p-4">
        <div>
          <p class="text-[12px] tracking-wide text-ink-mute uppercase">Readiness Score</p>
          <p class="tnum mt-1 text-3xl font-semibold text-ink">{digest.readiness_score}<span class="text-lg text-ink-mute">/100</span></p>
        </div>
        <p class="pb-1 text-[13px] text-ink-soft">
          {digest.new_badges} neue Badges · aktivste:r Mitarbeiter:in
          <span class="font-medium text-ink">{digest.most_active_employee}</span>
        </p>
      </div>
      <p class="mb-3 text-[12px] font-medium tracking-wide text-ink-mute uppercase">Top-Fragen der Woche</p>
      <button
        class="block w-full cursor-pointer rounded-lg text-left transition-colors duration-150 hover:bg-gray-50"
        onclick={() => openModal('digest', { period: data.period, detail: data.digestDetail })}
      >
        <BarList rows={questionRows} color="var(--color-brass)" />
      </button>
    </Card>

    <Card
      class="lg:col-span-3"
      title="Leaderboard"
      hint="Punkte aus Umsatz, Bot-Nutzung, Lernscore & Streaks"
    >
      {#snippet actions()}
        <a href="/gamification" class="inline-flex items-center gap-1 text-[13px] font-medium text-brass hover:underline">
          Alle ansehen <ArrowRight size={14} />
        </a>
      {/snippet}
      <Leaderboard rows={leaderboard} limit={6} />
    </Card>
  </div>

  <!-- Recently earned badges -->
  <div class="mt-4">
    <Card title="Zuletzt verdiente Badges" hint="{badges.length} insgesamt">
      <BadgeWall {badges} limit={10} layout="row" />
    </Card>
  </div>
</div>
