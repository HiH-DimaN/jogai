'use client';

import {useTranslations} from 'next-intl';
import JogaiScoreBadge from './JogaiScoreBadge';

const CASINOS = [
  {
    name: 'PIN-UP',
    bonus: '150% + 250 FS',
    wagering: '40x',
    score: 8.5,
    deposit: 'R$30 / MX$100',
    withdraw: '~2h',
    pix: true,
    crypto: true,
    card: true,
    url: '#',
  },
  {
    name: '1WIN',
    bonus: '500% até R$15.000',
    wagering: '50x',
    score: 7.8,
    deposit: 'R$20 / MX$50',
    withdraw: '~1h',
    pix: true,
    crypto: true,
    card: false,
    url: '#',
  },
  {
    name: 'STARDA',
    bonus: '100% + 500 FS',
    wagering: '35x',
    score: 8.2,
    deposit: 'R$50',
    withdraw: '~3h',
    pix: true,
    crypto: false,
    card: true,
    url: '#',
  },
];

function PaymentBadge({available, label}: {available: boolean; label: string}) {
  return (
    <span
      className={`rounded px-1.5 py-0.5 text-xs font-medium ${
        available ? 'bg-jogai-green/20 text-jogai-green' : 'bg-jogai-border text-jogai-muted'
      }`}
    >
      {label}
    </span>
  );
}

export default function CasinoTable() {
  const t = useTranslations('casinos');

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-jogai-border text-jogai-muted">
            <th className="px-4 py-3 font-medium">{t('name')}</th>
            <th className="px-4 py-3 font-medium">{t('bonus')}</th>
            <th className="px-4 py-3 font-medium">{t('wagering')}</th>
            <th className="px-4 py-3 font-medium">{t('score')}</th>
            <th className="px-4 py-3 font-medium">{t('deposit')}</th>
            <th className="px-4 py-3 font-medium">{t('withdraw')}</th>
            <th className="px-4 py-3 font-medium">{t('payment')}</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          {CASINOS.map((casino) => (
            <tr key={casino.name} className="border-b border-jogai-border transition hover:bg-jogai-card">
              <td className="px-4 py-4 font-bold text-jogai-text">{casino.name}</td>
              <td className="px-4 py-4 text-jogai-accent">{casino.bonus}</td>
              <td className="px-4 py-4">{casino.wagering}</td>
              <td className="px-4 py-4">
                <JogaiScoreBadge score={casino.score} />
              </td>
              <td className="px-4 py-4">{casino.deposit}</td>
              <td className="px-4 py-4">{casino.withdraw}</td>
              <td className="px-4 py-4">
                <div className="flex gap-1">
                  <PaymentBadge available={casino.pix} label={t('pix')} />
                  <PaymentBadge available={casino.crypto} label={t('crypto')} />
                  <PaymentBadge available={casino.card} label={t('card')} />
                </div>
              </td>
              <td className="px-4 py-4">
                <a
                  href={casino.url}
                  className="rounded-lg bg-jogai-accent px-4 py-2 text-xs font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
                >
                  {t('register')}
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
