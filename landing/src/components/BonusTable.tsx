'use client';

import {useTranslations} from 'next-intl';
import JogaiScoreBadge from './JogaiScoreBadge';

export type BonusRow = {
  id: number;
  casino_name: string;
  casino_slug: string;
  title: string;
  wagering_multiplier: number;
  wagering_deadline_days: number;
  jogai_score: number;
  verdict_key: string;
  affiliate_link: string | null;
};

function VerdictBadge({verdictKey, label}: {verdictKey: string; label: string}) {
  const colorMap: Record<string, string> = {
    verdict_excellent: 'bg-jogai-green/20 text-jogai-green',
    verdict_good: 'bg-jogai-accent/20 text-jogai-accent',
    verdict_caution: 'bg-yellow-500/20 text-yellow-400',
    verdict_bad: 'bg-jogai-red/20 text-jogai-red',
  };
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${colorMap[verdictKey] || colorMap.verdict_caution}`}>
      {label}
    </span>
  );
}

export default function BonusTable({bonuses}: {bonuses: BonusRow[]}) {
  const t = useTranslations('bonuses');

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-jogai-border text-jogai-muted">
            <th className="px-4 py-3 font-medium">{t('casino')}</th>
            <th className="px-4 py-3 font-medium">{t('bonus')}</th>
            <th className="px-4 py-3 font-medium">{t('wagering')}</th>
            <th className="px-4 py-3 font-medium">{t('deadline')}</th>
            <th className="px-4 py-3 font-medium">{t('score')}</th>
            <th className="px-4 py-3 font-medium">{t('verdict')}</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          {bonuses.map((bonus) => (
            <tr key={bonus.id} className="border-b border-jogai-border transition hover:bg-jogai-card">
              <td className="px-4 py-4 font-bold text-jogai-text">{bonus.casino_name}</td>
              <td className="px-4 py-4 text-jogai-accent">{bonus.title}</td>
              <td className="px-4 py-4">{bonus.wagering_multiplier}x</td>
              <td className="px-4 py-4">
                {bonus.wagering_deadline_days} {t('days')}
              </td>
              <td className="px-4 py-4">
                <JogaiScoreBadge score={bonus.jogai_score} />
              </td>
              <td className="px-4 py-4">
                <VerdictBadge verdictKey={bonus.verdict_key} label={t(bonus.verdict_key)} />
              </td>
              <td className="px-4 py-4">
                {bonus.affiliate_link ? (
                  <a
                    href={bonus.affiliate_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="rounded-lg bg-jogai-accent px-4 py-2 text-xs font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
                  >
                    {t('get_bonus')}
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
