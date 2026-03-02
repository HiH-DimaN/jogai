import { useTranslation } from 'react-i18next';
import type { QuizResult } from '../types';

interface CasinoResultCardProps {
  casino: QuizResult;
  rank: number;
}

export default function CasinoResultCard({ casino, rank }: CasinoResultCardProps) {
  const { t } = useTranslation();

  const handleClick = () => {
    if (casino.affiliate_link) {
      window.open(casino.affiliate_link, '_blank');
    }
  };

  const matchColor =
    casino.match_percent >= 80
      ? 'text-jogai-green'
      : casino.match_percent >= 60
        ? 'text-yellow-400'
        : 'text-jogai-red';

  return (
    <div className="bg-jogai-card border border-jogai-border rounded-xl p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-jogai-accent font-bold text-lg">#{rank}</span>
            <h3 className="text-jogai-text font-semibold text-lg">{casino.name}</h3>
          </div>
          <p className="text-jogai-muted text-sm mt-1">{casino.description}</p>
        </div>
        <div className={`text-right ${matchColor}`}>
          <div className="text-2xl font-bold">{casino.match_percent}%</div>
          <div className="text-xs">{t('quiz_match', { percent: casino.match_percent })}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm">
        {casino.best_bonus && (
          <div className="bg-jogai-bg rounded-lg p-2">
            <div className="text-jogai-muted text-xs">{t('quiz_best_bonus')}</div>
            <div className="text-jogai-text font-medium truncate">{casino.best_bonus}</div>
          </div>
        )}
        <div className="bg-jogai-bg rounded-lg p-2">
          <div className="text-jogai-muted text-xs">{t('quiz_min_deposit')}</div>
          <div className="text-jogai-text font-medium">{casino.min_deposit_formatted}</div>
        </div>
        <div className="bg-jogai-bg rounded-lg p-2">
          <div className="text-jogai-muted text-xs">{t('quiz_withdrawal')}</div>
          <div className="text-jogai-text font-medium">{casino.withdrawal_time}</div>
        </div>
      </div>

      {casino.affiliate_link && (
        <button
          onClick={handleClick}
          className="w-full bg-jogai-accent hover:bg-jogai-accent/80 text-white font-semibold py-2.5 rounded-lg transition-colors"
        >
          {t('quiz_register')}
        </button>
      )}
    </div>
  );
}
