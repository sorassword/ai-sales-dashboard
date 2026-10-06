import { api } from '$lib/api/client';
import { get } from 'svelte/store';
import { activePeriod } from '$lib/stores/period.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, depends }) => {
  depends('app:period');
  const period = get(activePeriod);

  // Arena + recent badges scale with the period; badge *definitions* are static
  // (period-independent) but loaded here in parallel for a single round-trip.
  const [arena, badgeDefinitions, badges] = await Promise.all([
    api.arena(fetch, period),
    api.badgeDefinitions(fetch),
    api.badges(fetch, period)
  ]);

  return { arena, badgeDefinitions, badges, period };
};
