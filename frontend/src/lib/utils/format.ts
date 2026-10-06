// German-locale formatting helpers used across the dashboard.

const eur = new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0
});

const eurCompact = new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
  notation: 'compact',
  maximumFractionDigits: 1
});

const num = new Intl.NumberFormat('de-DE');

export const formatEur = (v: number) => eur.format(v);
export const formatEurCompact = (v: number) => eurCompact.format(v);
export const formatNum = (v: number) => num.format(Math.round(v));

/** 7054 (minutes) -> "117,6 h" */
export function formatHours(minutes: number): string {
  return `${(minutes / 60).toLocaleString('de-DE', { maximumFractionDigits: 1 })} h`;
}

/** 34.3 (already hours) -> "34,3 h" */
export function formatHoursValue(hours: number): string {
  return `${hours.toLocaleString('de-DE', { maximumFractionDigits: 1 })} h`;
}

export function formatPct(v: number): string {
  const sign = v > 0 ? '+' : '';
  return `${sign}${v.toLocaleString('de-DE', { maximumFractionDigits: 1 })}%`;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('de-DE', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  });
}

export function relativeDate(iso: string): string {
  return new Date(iso).toLocaleDateString('de-DE', { day: '2-digit', month: 'short' });
}

/** 'Leon Richter' -> 'leon-richter' (mirrors the backend slug logic). */
export function slugify(name: string): string {
  const umlauts: Record<string, string> = { ä: 'ae', ö: 'oe', ü: 'ue', ß: 'ss' };
  return name
    .toLowerCase()
    .replace(/[äöüß]/g, (c) => umlauts[c] ?? c)
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
