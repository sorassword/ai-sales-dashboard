import { api } from '$lib/api/client';
import { get } from 'svelte/store';
import { activePeriod } from '$lib/stores/period.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, depends }) => {
  depends('app:period');
  const period = get(activePeriod);
  // /api/readiness now returns an object, not a bare array.
  const { items, critical_count, warning_count, next_launch } = await api.readiness(fetch, period);
  return { items, critical_count, warning_count, next_launch, period };
};
