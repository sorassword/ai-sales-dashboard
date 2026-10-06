import { env } from '$env/dynamic/public';
import type {
  ArenaResponse,
  BadgeDefinitionsResponse,
  BotTrendDetail,
  CorrelationDetail,
  CorrelationInsight,
  DigestDetail,
  EarnedBadge,
  Employee,
  EmployeeDetail,
  EmployeeMetric,
  KpiSummary,
  LeaderboardRow,
  Period,
  QuizResult,
  ReadinessResponse,
  RevenueTrendDetail,
  Store,
  StoreDetail,
  StoreMetric,
  TrendPoint,
  WeeklyDigest
} from '$lib/types';

export const API_BASE = env.PUBLIC_API_URL || 'http://localhost:8000';

type Fetch = typeof globalThis.fetch;

async function get<T>(path: string, fetchFn: Fetch = fetch): Promise<T> {
  const res = await fetchFn(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`API ${res.status} on ${path}`);
  }
  return (await res.json()) as T;
}

/** Append the period query param (defaulting to "month"). */
function withPeriod(path: string, period?: Period): string {
  const sep = path.includes('?') ? '&' : '?';
  return `${path}${sep}period=${period ?? 'month'}`;
}

/**
 * Single typed surface for the whole backend.
 * In a +page.ts `load`, pass the SvelteKit `fetch` so SSR/caching work:
 *   api.kpis(fetch, period)
 * The *detail* endpoints are fetched client-side (inside modals), so they use
 * the global fetch and only take a period.
 */
export const api = {
  kpis: (f?: Fetch, period?: Period) =>
    get<KpiSummary>(withPeriod('/api/overview/kpis', period), f),
  trend: (metric: 'revenue' | 'bot_minutes' | 'learning_score', f?: Fetch, period?: Period) =>
    get<TrendPoint[]>(withPeriod(`/api/overview/trends/${metric}`, period), f),
  correlation: (f?: Fetch, period?: Period) =>
    get<CorrelationInsight>(withPeriod('/api/overview/correlation', period), f),
  digest: (f?: Fetch, period?: Period) =>
    get<WeeklyDigest>(withPeriod('/api/overview/digest', period), f),

  employees: (f?: Fetch, period?: Period) =>
    get<Employee[]>(withPeriod('/api/employees', period), f),
  employeeMetrics: (f?: Fetch, period?: Period) =>
    get<EmployeeMetric[]>(withPeriod('/api/employees/metrics', period), f),

  stores: (f?: Fetch, period?: Period) =>
    get<Store[]>(withPeriod('/api/stores', period), f),
  storeMetrics: (f?: Fetch, period?: Period) =>
    get<StoreMetric[]>(withPeriod('/api/stores/metrics', period), f),

  leaderboard: (f?: Fetch, period?: Period) =>
    get<LeaderboardRow[]>(withPeriod('/api/gamification/leaderboard', period), f),
  badges: (f?: Fetch, period?: Period) =>
    get<EarnedBadge[]>(withPeriod('/api/gamification/badges', period), f),
  quizzes: (f?: Fetch, period?: Period) =>
    get<QuizResult[]>(withPeriod('/api/gamification/quizzes', period), f),

  arena: (f?: Fetch, period?: Period) =>
    get<ArenaResponse>(withPeriod('/api/gamification/arena', period), f),
  // Badge definitions are static (period-independent); fetch carried for SSR.
  badgeDefinitions: (f?: Fetch) =>
    get<BadgeDefinitionsResponse>('/api/gamification/badge-definitions', f),

  readiness: (f?: Fetch, period?: Period) =>
    get<ReadinessResponse>(withPeriod('/api/readiness', period), f),

  // ----- Detail endpoints (client-side, for modals) --------------------- //
  storeDetail: (store_id: string, period?: Period) =>
    get<StoreDetail>(withPeriod(`/api/stores/${store_id}`, period)),
  employeeDetail: (employee_id: string, period?: Period) =>
    get<EmployeeDetail>(withPeriod(`/api/employees/${employee_id}`, period)),
  revenueTrendDetail: (period?: Period) =>
    get<RevenueTrendDetail>(withPeriod('/api/overview/trends/revenue/detail', period)),
  botTrendDetail: (period?: Period) =>
    get<BotTrendDetail>(withPeriod('/api/overview/trends/bot/detail', period)),
  correlationDetail: (period?: Period) =>
    get<CorrelationDetail>(withPeriod('/api/overview/correlation/detail', period)),
  digestDetail: (period?: Period) =>
    get<DigestDetail>(withPeriod('/api/overview/digest/detail', period))
};
