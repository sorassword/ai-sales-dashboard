import { writable, derived } from 'svelte/store';
import type { Period } from '$lib/types';

/** The globally selected reporting period. Drives every data load. */
export const activePeriod = writable<Period>('month');

/** True while a period-triggered reload is in flight (used for the dim state). */
export const isReloading = writable(false);

/** The period switch buttons, mapped to their Period value. */
export const PERIOD_OPTIONS: { value: Period; label: string }[] = [
  { value: 'week', label: 'Diese Woche' },
  { value: 'month', label: 'Dieser Monat' },
  { value: 'quarter', label: 'Quartal' }
];

/** Short label for page subtitles, e.g. "Mai 2026". */
export function periodLabel(period: Period): string {
  switch (period) {
    case 'week':
      return 'Diese Woche';
    case 'quarter':
      return 'Q2 2026';
    default:
      return 'Mai 2026';
  }
}

/** Reactive version of {@link periodLabel}. */
export const periodLabelStore = derived(activePeriod, ($p) => periodLabel($p));
