import { useTranslation } from 'react-i18next';

interface JogaiScoreProps {
  score: number;
  verdictKey: string;
  size?: 'sm' | 'lg';
}

function getScoreColor(score: number): string {
  if (score >= 8) return 'bg-jogai-green text-white';
  if (score >= 6) return 'bg-yellow-500 text-black';
  if (score >= 4) return 'bg-orange-500 text-white';
  return 'bg-jogai-red text-white';
}

function getScoreBorderColor(score: number): string {
  if (score >= 8) return 'border-jogai-green';
  if (score >= 6) return 'border-yellow-500';
  if (score >= 4) return 'border-orange-500';
  return 'border-jogai-red';
}

export default function JogaiScore({
  score,
  verdictKey,
  size = 'sm',
}: JogaiScoreProps) {
  const { t } = useTranslation();

  const isLarge = size === 'lg';

  return (
    <div className="flex items-center gap-2">
      <div
        className={`${getScoreColor(score)} font-bold rounded-lg flex items-center justify-center ${
          isLarge ? 'w-14 h-14 text-xl' : 'w-10 h-10 text-sm'
        }`}
      >
        {score.toFixed(1)}
      </div>
      <div>
        <div
          className={`font-semibold ${isLarge ? 'text-base' : 'text-xs'} text-jogai-muted`}
        >
          {t('score_label')}
        </div>
        <div
          className={`font-bold ${isLarge ? 'text-lg' : 'text-sm'} ${getScoreBorderColor(score).replace('border-', 'text-')}`}
        >
          {t(verdictKey)}
        </div>
      </div>
    </div>
  );
}
