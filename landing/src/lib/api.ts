const API_BASE = process.env.INTERNAL_API_URL || 'http://backend:8001/api';

function toBackendLocale(locale: string): string {
  return locale.replace('-', '_');
}

function geoFromLocale(locale: string): string {
  if (locale.startsWith('es')) return 'MX';
  return 'BR';
}

export type CasinoAPI = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  min_deposit: number | null;
  min_deposit_formatted: string | null;
  pix_supported: boolean;
  spei_supported: boolean;
  crypto_supported: boolean;
  withdrawal_time: string | null;
  affiliate_link: string | null;
  best_bonus: string | null;
  best_jogai_score: number | null;
  bonus_count: number;
};

export type BonusAPI = {
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
};

export type CasinoDetailAPI = CasinoAPI & {
  bonuses: BonusAPI[];
};

export async function fetchCasinos(locale: string): Promise<CasinoAPI[]> {
  const backendLocale = toBackendLocale(locale);
  const geo = geoFromLocale(locale);
  try {
    const res = await fetch(
      `${API_BASE}/casinos?geo=${geo}&locale=${backendLocale}`,
      {next: {revalidate: 300}}
    );
    if (!res.ok) return [];
    const data = await res.json();
    return data.casinos || [];
  } catch {
    return [];
  }
}

export async function fetchCasino(
  slug: string,
  locale: string
): Promise<CasinoDetailAPI | null> {
  const backendLocale = toBackendLocale(locale);
  try {
    const res = await fetch(
      `${API_BASE}/casinos/${slug}?locale=${backendLocale}`,
      {next: {revalidate: 300}}
    );
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function fetchBonuses(locale: string): Promise<BonusAPI[]> {
  const backendLocale = toBackendLocale(locale);
  const geo = geoFromLocale(locale);
  try {
    const res = await fetch(
      `${API_BASE}/bonuses?geo=${geo}&locale=${backendLocale}`,
      {next: {revalidate: 300}}
    );
    if (!res.ok) return [];
    const data = await res.json();
    return data.bonuses || [];
  } catch {
    return [];
  }
}

export async function fetchCasinoSlugs(): Promise<string[]> {
  try {
    const res = await fetch(`${API_BASE}/casinos?geo=BR&locale=pt_BR`, {
      next: {revalidate: 300},
    });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.casinos || []).map((c: CasinoAPI) => c.slug);
  } catch {
    return [];
  }
}
