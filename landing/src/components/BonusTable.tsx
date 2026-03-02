'use client';

import {useTranslations} from 'next-intl';
import JogaiScoreBadge from './JogaiScoreBadge';

type VerdictKey = 'verdict_excellent' | 'verdict_good' | 'verdict_caution' | 'verdict_bad';

const BONUSES = [
  {
    casino: 'PIN-UP',
    bonus: '150% + 250 FS',
    wagering: '40x',
    deadline: 7,
    score: 8.5,
    verdictKey: 'verdict_excellent' as VerdictKey,
    url: '#',
  },
  {
    casino: '1WIN',
    bonus: '500% até R$15.000',
    wagering: '50x',
    deadline: 30,
    score: 7.8,
    verdictKey: 'verdict_good' as VerdictKey,
    url: '#',
  },
  {
    casino: 'BET365',
    bonus: 'R$200 Free Bet',
    wagering: '1x',
    deadline: 30,
    score: 8.9,
    verdictKey: 'verdict_excellent' as VerdictKey,
    url: '#',
  },
  {
    casino: 'RIVALO',
    bonus: '100% até R$500 + 50 FS',
    wagering: '35x',
    deadline: 14,
    score: 8.2,
    verdictKey: 'verdict_excellent' as VerdictKey,
    url: '#',
  },
];

function VerdictBadge({verdictKey, label}: {verdictKey: VerdictKey; label: string}) {
  const colorMap: Record<VerdictKey, string> = {
    verdict_excellent: 'bg-jogai-green/20 text-jogai-green',
    verdict_good: 'bg-jogai-accent/20 text-jogai-accent',
    verdict_caution: 'bg-yellow-500/20 text-yellow-400',
    verdict_bad: 'bg-jogai-red/20 text-jogai-red',
  };
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${colorMap[verdictKey]}`}>
      {label}
    </span>
  );
}

export default function BonusTable() {
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
          {BONUSES.map((bonus) => (
            <tr key={bonus.casino} className="border-b border-jogai-border transition hover:bg-jogai-card">
              <td className="px-4 py-4 font-bold text-jogai-text">{bonus.casino}</td>
              <td className="px-4 py-4 text-jogai-accent">{bonus.bonus}</td>
              <td className="px-4 py-4">{bonus.wagering}</td>
              <td className="px-4 py-4">
                {bonus.deadline} {t('days')}
              </td>
              <td className="px-4 py-4">
                <JogaiScoreBadge score={bonus.score} />
              </td>
              <td className="px-4 py-4">
                <VerdictBadge verdictKey={bonus.verdictKey} label={t(bonus.verdictKey)} />
              </td>
              <td className="px-4 py-4">
                <a
                  href={bonus.url}
                  className="rounded-lg bg-jogai-accent px-4 py-2 text-xs font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
                >
                  {t('get_bonus')}
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
