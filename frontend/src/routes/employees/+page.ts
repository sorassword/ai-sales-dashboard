import { api } from '$lib/api/client';
import { get } from 'svelte/store';
import { activePeriod } from '$lib/stores/period.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, depends }) => {
  depends('app:period');
  const period = get(activePeriod);
  const metrics = await api.employeeMetrics(fetch, period);
  return { metrics, period };
};
