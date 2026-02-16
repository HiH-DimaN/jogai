'use client';

type Props = {
  score: number;
};

export default function JogaiScoreBadge({score}: Props) {
  const color =
    score >= 8
      ? 'bg-jogai-green/20 text-jogai-green'
      : score >= 6
        ? 'bg-jogai-accent/20 text-jogai-accent'
        : 'bg-jogai-red/20 text-jogai-red';

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-sm font-bold ${color}`}>
      {score.toFixed(1)}
    </span>
  );
}
