import { useTranslation } from 'react-i18next';
import type { AnalysisResult as AnalysisResultType } from '../types';
import JogaiScore from './JogaiScore';
import { formatCurrency } from '../utils/format';

interface AnalysisResultProps {
  result: AnalysisResultType;
}

export default function AnalysisResult({ result }: AnalysisResultProps) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;

  const rows: { label: string; value: string; negative?: boolean; highlight?: boolean }[] = [
    {
      label: t('result_deposit'),
      value: formatCurrency(result.deposit, lang),
    },
    {
      label: t('result_bonus'),
      value: `${formatCurrency(result.bonus_amount, lang)} (${result.bonus_percent}%)`,
    },
    {
      label: t('result_total'),
      value: formatCurrency(result.total_balance, lang),
    },
    {
      label: t('result_wagering'),
      value: `x${result.wagering_multiplier} = ${result.wagering_total_formatted}`,
    },
    {
      label: t('result_deadline'),
      value: `${result.deadline_days} ${t('days_suffix')}`,
    },
    {
      label: t('result_max_bet'),
      value: formatCurrency(result.max_bet, lang),
    },
    {
      label: t('result_bets_needed'),
      value: `${result.bets_needed} (${t('result_bets_detail', {
        perDay: result.bets_per_day,
        perHour: result.bets_per_hour,
      })})`,
    },
    {
      label: t('result_expected_loss'),
      value: result.expected_loss_formatted,
      negative: true,
    },
    {
      label: t('result_profit_chance'),
      value: `~${result.profit_probability}%`,
      highlight: result.profit_probability >= 50,
    },
  ];

  if (result.free_spins > 0) {
    rows.push({
      label: t('result_free_spins'),
      value: String(result.free_spins),
      negative: false,
      highlight: false,
    });
  }

  return (
    <div className="space-y-4">
      <div className="bg-jogai-card border border-jogai-border rounded-xl p-4">
        <div className="flex justify-center mb-4">
          <JogaiScore
            score={result.jogai_score}
            verdictKey={result.verdict_key}
            size="lg"
          />
        </div>

        <div className="space-y-2">
          {rows.map((row) => (
            <div
              key={row.label}
              className="flex justify-between items-center py-1.5 border-b border-jogai-border last:border-0"
            >
              <span className="text-jogai-muted text-sm">{row.label}</span>
              <span
                className={`text-sm font-medium ${
                  row.negative
                    ? 'text-jogai-red'
                    : row.highlight
                      ? 'text-jogai-green'
                      : 'text-jogai-text'
                }`}
              >
                {row.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {result.ai_summary && (
        <div className="bg-jogai-card border border-jogai-border rounded-xl p-4">
          <h3 className="text-jogai-accent font-semibold mb-2">
            {t('result_ai_summary')}
          </h3>
          <p className="text-jogai-text text-sm leading-relaxed whitespace-pre-line">
            {result.ai_summary}
          </p>
        </div>
      )}
    </div>
  );
}
