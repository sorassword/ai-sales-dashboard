import { api } from '$lib/api/client';
import { get } from 'svelte/store';
import { activePeriod } from '$lib/stores/period.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, depends }) => {
  depends('app:period');
  const period = get(activePeriod);

  // Preload the store list and all four store details in parallel so the
  // detail modal opens instantly.
  const [stores, koeln, essen, duesseldorf, krefeld] = await Promise.all([
    api.storeMetrics(fetch, period),
    api.storeDetail('koeln', period),
    api.storeDetail('essen', period),
    api.storeDetail('duesseldorf', period),
    api.storeDetail('krefeld', period)
  ]);

  return {
    stores,
    period,
    storeDetails: { koeln, essen, duesseldorf, krefeld }
  };
};
