export interface Bonus {
  id: number;
  casino_id: number;
  casino_name: string;
  casino_slug: string;
  title: string;
  bonus_percent: number;
  max_bonus_amount: number;
  max_bonus_currency: string;
  wagering_multiplier: number;
  wagering_deadline_days: number;
  max_bet: number;
  free_spins: number;
  no_deposit: boolean;
  jogai_score: number;
  verdict_key: string;
  affiliate_link: string | null;
  formatted_max_bonus: string;
}

export interface Casino {
  id: number;
  name: string;
  slug: string;
  logo_url: string | null;
  description: string;
  min_deposit: number;
  pix_supported: boolean;
  spei_supported: boolean;
  crypto_supported: boolean;
  withdrawal_time: string;
  is_active: boolean;
}

export interface AnalysisResult {
  jogai_score: number;
  verdict_key: string;
  verdict_text: string;
  deposit: number;
  bonus_amount: number;
  bonus_percent: number;
  total_balance: number;
  wagering_multiplier: number;
  wagering_total: number;
  wagering_total_formatted: string;
  deadline_days: number;
  max_bet: number;
  bets_needed: number;
  bets_per_day: number;
  bets_per_hour: number;
  expected_loss: number;
  expected_loss_formatted: string;
  profit_probability: number;
  free_spins: number;
  ai_summary: string;
}

export interface UserData {
  id: number;
  username: string | null;
  first_name: string | null;
  locale: string;
  geo: string;
  jogai_coins: number;
  is_pro: boolean;
  referral_code: string | null;
}

export interface AuthResponse {
  access_token: string;
  user: UserData;
}

export interface QuizOption {
  value: string;
  label: string;
}

export interface QuizQuestion {
  question: string;
  options: QuizOption[];
}

export interface QuizResult {
  name: string;
  slug: string;
  match_percent: number;
  description: string;
  min_deposit_formatted: string;
  withdrawal_time: string;
  best_bonus: string | null;
  affiliate_link: string | null;
}

export interface ReferralStats {
  referral_code: string;
  referral_link: string;
  jogai_coins: number;
  referral_count: number;
}
