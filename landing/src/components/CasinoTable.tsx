'use client';

import {useTranslations} from 'next-intl';
import JogaiScoreBadge from './JogaiScoreBadge';

export type CasinoRow = {
  name: string;
  slug: string;
  best_bonus: string | null;
  best_jogai_score: number | null;
  min_deposit_formatted: string | null;
  withdrawal_time: string | null;
  pix_supported: boolean;
  crypto_supported: boolean;
  spei_supported: boolean;
  affiliate_link: string | null;
};

function PaymentBadge({available, label}: {available: boolean; label: string}) {
  if (!available) return null;
  return (
    <span className="rounded bg-jogai-green/20 px-1.5 py-0.5 text-xs font-medium text-jogai-green">
      {label}
    </span>
  );
}

export default function CasinoTable({casinos}: {casinos: CasinoRow[]}) {
  const t = useTranslations('casinos');

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-jogai-border text-jogai-muted">
            <th className="px-4 py-3 font-medium">{t('name')}</th>
            <th className="px-4 py-3 font-medium">{t('bonus')}</th>
            <th className="px-4 py-3 font-medium">{t('score')}</th>
            <th className="px-4 py-3 font-medium">{t('deposit')}</th>
            <th className="px-4 py-3 font-medium">{t('withdraw')}</th>
            <th className="px-4 py-3 font-medium">{t('payment')}</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          {casinos.map((casino) => (
            <tr key={casino.slug} className="border-b border-jogai-border transition hover:bg-jogai-card">
              <td className="px-4 py-4 font-bold text-jogai-text">{casino.name}</td>
              <td className="px-4 py-4 text-jogai-accent">{casino.best_bonus || '—'}</td>
              <td className="px-4 py-4">
                {casino.best_jogai_score !== null ? (
                  <JogaiScoreBadge score={casino.best_jogai_score} />
                ) : (
                  '—'
                )}
              </td>
              <td className="px-4 py-4">{casino.min_deposit_formatted || '—'}</td>
              <td className="px-4 py-4">{casino.withdrawal_time || '—'}</td>
              <td className="px-4 py-4">
                <div className="flex gap-1">
                  <PaymentBadge available={casino.pix_supported} label={t('pix')} />
                  <PaymentBadge available={casino.crypto_supported} label={t('crypto')} />
                  <PaymentBadge available={casino.spei_supported} label="SPEI" />
                </div>
              </td>
              <td className="px-4 py-4">
                {casino.affiliate_link ? (
                  <a
                    href={casino.affiliate_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="rounded-lg bg-jogai-accent px-4 py-2 text-xs font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
                  >
                    {t('register')}
                  </a>
                ) : (
                  <span className="text-jogai-muted">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
