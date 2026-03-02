import { useTranslation } from 'react-i18next';
import type { Bonus } from '../types';
import JogaiScore from './JogaiScore';
import { formatCurrency } from '../utils/format';

interface BonusCardProps {
  bonus: Bonus;
}

export default function BonusCard({ bonus }: BonusCardProps) {
  const { t, i18n } = useTranslation();

  const handleClick = () => {
    if (bonus.affiliate_link) {
      window.open(bonus.affiliate_link, '_blank');
    }
  };

  return (
    <div className="bg-jogai-card border border-jogai-border rounded-xl p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="text-jogai-muted text-xs uppercase tracking-wide">
            {bonus.casino_name}
          </div>
          <h3 className="text-jogai-text font-semibold mt-1">{bonus.title}</h3>
        </div>
        <JogaiScore score={bonus.jogai_score} verdictKey={bonus.verdict_key} />
      </div>

      <div className="flex flex-wrap gap-2 text-xs">
        <span className="bg-jogai-bg px-2 py-1 rounded text-jogai-muted">
          {t('bonus_wagering', { multiplier: bonus.wagering_multiplier })}
        </span>
        {bonus.wagering_deadline_days > 0 && (
          <span className="bg-jogai-bg px-2 py-1 rounded text-jogai-muted">
            {t('bonus_deadline', { days: bonus.wagering_deadline_days })}
          </span>
        )}
        {bonus.max_bet > 0 && (
          <span className="bg-jogai-bg px-2 py-1 rounded text-jogai-muted">
            {t('bonus_max_bet', {
              amount: formatCurrency(bonus.max_bet, i18n.language),
            })}
          </span>
        )}
        {bonus.free_spins > 0 && (
          <span className="bg-jogai-accent/20 px-2 py-1 rounded text-jogai-accent">
            {t('bonus_free_spins', { count: bonus.free_spins })}
          </span>
        )}
        {bonus.no_deposit && (
          <span className="bg-jogai-green/20 px-2 py-1 rounded text-jogai-green">
            {t('bonus_no_deposit')}
          </span>
        )}
      </div>

      <button
        onClick={handleClick}
        className="w-full bg-jogai-accent hover:bg-jogai-accent/80 text-white font-semibold py-2.5 rounded-lg transition-colors"
      >
        {t('btn_get_bonus')}
      </button>
    </div>
  );
}
