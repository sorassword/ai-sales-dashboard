import { api } from '$lib/api/client';
import { get } from 'svelte/store';
import { activePeriod } from '$lib/stores/period.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, depends }) => {
  // Re-run this load whenever the global period changes.
  depends('app:period');
  const period = get(activePeriod);

  // Fetch everything the overview needs in parallel — including the chart
  // drilldown details, so the modals open instantly without a second fetch.
  const [
    kpis,
    revenueTrend,
    botTrend,
    correlation,
    digest,
    leaderboard,
    badges,
    stores,
    revenueTrendDetail,
    botTrendDetail,
    correlationDetail,
    digestDetail
  ] = await Promise.all([
    api.kpis(fetch, period),
    api.trend('revenue', fetch, period),
    api.trend('bot_minutes', fetch, period),
    api.correlation(fetch, period),
    api.digest(fetch, period),
    api.leaderboard(fetch, period),
    api.badges(fetch, period),
    api.storeMetrics(fetch, period),
    api.revenueTrendDetail(period),
    api.botTrendDetail(period),
    api.correlationDetail(period),
    api.digestDetail(period)
  ]);

  return {
    kpis,
    revenueTrend,
    botTrend,
    correlation,
    digest,
    leaderboard,
    badges,
    stores,
    period,
    revenueTrendDetail,
    botTrendDetail,
    correlationDetail,
    digestDetail
  };
};
