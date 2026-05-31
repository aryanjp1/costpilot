export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface Member {
  id: string;
  user_id: string;
  email: string;
  full_name: string | null;
  role: string;
  joined_at: string;
}

export interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
}

export interface CreatedApiKey extends ApiKey {
  key: string;
}

export interface OverviewStats {
  total_cost: number;
  total_requests: number;
  avg_cost_per_request: number;
  avg_latency: number;
  models_used: number;
  error_rate: number;
  prev_total_cost: number;
  cost_change_pct: number;
}

export interface TimelinePoint {
  timestamp: string;
  cost: number;
  requests: number;
}

export interface ModelStat {
  model: string;
  cost: number;
  requests: number;
  avg_latency: number;
  input_tokens: number;
  output_tokens: number;
}

export interface TagStat {
  tag_value: string;
  cost: number;
  requests: number;
}

export interface TokenPoint {
  timestamp: string;
  input_tokens: number;
  output_tokens: number;
}

export interface LatencyPoint {
  timestamp: string;
  p50: number;
  p95: number;
  p99: number;
}

export interface ErrorPoint {
  timestamp: string;
  error_count: number;
  error_rate: number;
}

export interface Forecast {
  current_daily_avg: number;
  projected_weekly: number;
  projected_monthly: number;
  trend: "increasing" | "stable" | "decreasing" | "insufficient_data";
}

export interface Budget {
  id: string;
  name: string;
  period: "daily" | "weekly" | "monthly";
  amount_usd: number;
  alert_threshold_pct: number;
  is_active: boolean;
  created_at: string;
}

export interface Alert {
  id: string;
  budget_id: string;
  alert_type: "warning" | "exceeded" | "anomaly";
  title: string;
  description: string;
  current_spend: number;
  budget_amount: number;
  is_read: boolean;
  created_at: string;
}

export interface Recommendation {
  type: string;
  title: string;
  description: string;
  estimated_savings_usd: number;
  model_from: string | null;
  model_to: string | null;
  affected_tags: string[];
}

export interface EventRow {
  id: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  latency_ms: number;
  status: string;
  error_message: string | null;
  tags: Record<string, string>;
  timestamp: string;
}

export interface EventPage {
  items: EventRow[];
  total: number;
  page: number;
  page_size: number;
}

export type Period = "24h" | "7d" | "30d" | "90d";
