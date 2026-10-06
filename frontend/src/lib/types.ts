// Mirrors backend/app/models/schemas.py — keep these in sync.
// (Later you can auto-generate these from the OpenAPI schema; see README.)

export type Period = 'week' | 'month' | 'quarter';

export interface Store {
  id: string;
  name: string;
  city: string;
  headcount: number;
}

export interface Employee {
  id: string;
  name: string;
  initials: string;
  store_id: string;
  store_name: string;
  role: 'Verkäufer' | 'Teamleitung' | 'Azubi';
  avatar_hue: number;
}

export interface TrendPoint {
  month: string;
  label: string;
  value: number;
  period: Period;
}

export interface KpiSummary {
  period: Period;
  total_revenue: number;
  revenue_delta_pct: number;
  bot_minutes: number;
  bot_minutes_delta_pct: number;
  avg_learning_score: number;
  learning_score_delta_pct: number;
  active_users: number;
  active_users_delta_pct: number;
  bot_hours: number;
  bot_hours_target: number;
  bot_hours_pct_of_target: number;
  bot_hours_per_employee: number;
  bot_hours_benchmark_label: 'Unter Ziel' | 'Auf Kurs' | 'Übertroffen';
}

export interface EmployeeMetric {
  period: Period;
  employee: Employee;
  revenue: number;
  bot_minutes: number;
  bot_interactions: number;
  learning_score: number;
  quiz_accuracy: number;
  streak_days: number;
  badges: number;
}

export interface StoreMetric {
  period: Period;
  store: Store;
  revenue: number;
  bot_minutes: number;
  chat_share_pct: number;
  revenue_share_pct: number;
  readiness_score: number;
}

export interface ScatterPoint {
  employee_id: string;
  name: string;
  bot_minutes: number;
  revenue: number;
  learning_score: number;
}

export interface CorrelationInsight {
  period: Period;
  points: ScatterPoint[];
  pearson_r: number;
  headline: string;
}

export interface BadgeDef {
  id: string;
  name: string;
  description: string;
  icon: string;
  tier: 'bronze' | 'silver' | 'gold';
  rarity: 'common' | 'rare' | 'legendary';
  icon_key: 'euro' | 'fire' | 'brain' | 'star' | 'lightning' | 'crown' | 'clock' | 'trophy';
}

export interface EarnedBadge {
  badge: BadgeDef;
  employee_id: string;
  employee_name: string;
  earned_on: string;
}

export interface PointsBreakdown {
  from_revenue: number;
  from_bot: number;
  from_quiz: number;
  from_streak: number;
  total: number;
}

export interface LeaderboardRow {
  period: Period;
  rank: number;
  employee: Employee;
  points: number;
  points_breakdown: PointsBreakdown;
  revenue: number;
  bot_minutes: number;
  streak_days: number;
  badges: number;
  movement: number;
}

export interface QuizResult {
  employee_id: string;
  employee_name: string;
  topic: string;
  accuracy: number;
  questions: number;
  taken_on: string;
}

export type AlertLevel = 'critical' | 'warning' | 'ok';

export interface ReadinessItem {
  collection: string;
  launch_date: string;
  prepared_employees: number;
  total_employees: number;
  readiness_score: number;
  status: 'on_track' | 'at_risk' | 'behind';
  alert_level: AlertLevel;
}

export interface NextLaunch {
  name: string;
  date: string;
  days_until: number;
  alert_level: AlertLevel;
}

export interface ReadinessResponse {
  items: ReadinessItem[];
  critical_count: number;
  warning_count: number;
  next_launch: NextLaunch;
  period: Period;
}

export interface TopQuestion {
  topic: string;
  count: number;
}

export interface WeeklyDigest {
  period: Period;
  week_label: string;
  readiness_score: number;
  top_questions: TopQuestion[];
  new_badges: number;
  most_active_employee: string;
}

// --------------------------------------------------------------------------- //
// Store detail
// --------------------------------------------------------------------------- //
export interface NextCollection {
  name: string;
  launch_date: string;
  readiness_score: number;
  alert_level: string;
}

export interface StoreEmployee {
  id: string;
  name: string;
  role: string;
  revenue: number;
  bot_hours: number;
  learn_score: number;
  quiz_pct: number;
  streak_days: number;
  badge_count: number;
  rank: number;
}

export interface StoreDetail {
  store_id: string;
  name: string;
  city: string;
  employee_count: number;
  period: Period;
  revenue: number;
  revenue_share_pct: number;
  revenue_per_employee: number;
  revenue_trend: number;
  bot_hours: number;
  bot_hours_per_employee: number;
  avg_learn_score: number;
  readiness_score: number;
  next_collection: NextCollection;
  employees: StoreEmployee[];
  insight: string;
}

// --------------------------------------------------------------------------- //
// Employee detail
// --------------------------------------------------------------------------- //
export interface EmployeeBadge {
  name: string;
  rarity: 'common' | 'rare' | 'legendary';
  icon_key: string;
  earned_date: string;
}

export interface EmployeeDetail {
  employee_id: string;
  name: string;
  initials: string;
  role: string;
  store_name: string;
  period: Period;
  revenue: number;
  bot_hours: number;
  learn_score: number;
  quiz_pct: number;
  streak_days: number;
  rank: number;
  points: number;
  points_breakdown: PointsBreakdown;
  revenue_vs_store_avg: number;
  bot_hours_vs_store_avg: number;
  badges: EmployeeBadge[];
  bot_trend: TrendPoint[];
  revenue_trend: TrendPoint[];
  insight: string;
}

// --------------------------------------------------------------------------- //
// Chart drilldowns
// --------------------------------------------------------------------------- //
export interface MonthlyInsight {
  label: string;
  value: number;
  comment: string;
}

export interface RevenueTrendDetail {
  period: Period;
  points: TrendPoint[];
  extended_points: TrendPoint[];
  monthly_insights: MonthlyInsight[];
}

export interface StoreBotBreakdown {
  store_name: string;
  bot_hours: number;
  pct_of_total: number;
  color_key: string;
}

export interface BotTrendDetail {
  period: Period;
  points: TrendPoint[];
  by_store: StoreBotBreakdown[];
}

export interface CorrelationEmployee {
  name: string;
  store: string;
  bot_minutes: number;
  revenue: number;
  is_outlier: boolean;
}

export interface CorrelationDetail {
  period: Period;
  correlation_r: number;
  employees: CorrelationEmployee[];
  insight: string;
}

export interface DigestTopQuestion {
  topic: string;
  count: number;
  top_stores: string[];
  example_query: string;
}

export interface ReadinessSummary {
  avg_score: number;
  critical_count: number;
  collections_launching_soon: number;
}

export interface DigestDetail {
  period: Period;
  top_questions: DigestTopQuestion[];
  readiness_summary: ReadinessSummary;
}

// --------------------------------------------------------------------------- //
// Arena (gamification) — GET /api/gamification/arena
// --------------------------------------------------------------------------- //
export interface ArenaEntry {
  rank: number;
  employee_id: string;
  name: string;
  initials: string;
  store_name: string;
  points: number;
  points_breakdown: PointsBreakdown;
  revenue: number;
  streak_days: number;
  badge_count: number;
  avatar_color: string;
}

export interface LeaderboardArenaRow {
  rank: number;
  rank_change: number;
  employee_id: string;
  name: string;
  initials: string;
  store_name: string;
  points: number;
  points_breakdown: PointsBreakdown;
  revenue: number;
  bot_hours: number;
  streak_days: number;
  badge_count: number;
  avatar_color: string;
}

export interface ArenaWeeklyHighlight {
  employee_id: string;
  name: string;
  store_name: string;
  highlight_reason: string;
}

export interface ArenaResponse {
  period: Period;
  podium: ArenaEntry[];
  leaderboard: LeaderboardArenaRow[];
  weekly_highlight: ArenaWeeklyHighlight;
}

// --------------------------------------------------------------------------- //
// Badge definitions — GET /api/gamification/badge-definitions
// --------------------------------------------------------------------------- //
export interface BadgeDefinition {
  name: string;
  rarity: 'common' | 'rare' | 'legendary';
  icon_key: string;
  condition_text: string;
  condition_detail: string;
  earned_count: number;
  total_employees: number;
  earn_rate_pct: number;
  last_earned_by: string;
  last_earned_date: string;
}

export interface BadgeDefinitionsResponse {
  badges: BadgeDefinition[];
}
