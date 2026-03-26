'use client';

import {useLocale, useTranslations} from 'next-intl';

const CHANNEL_MAP: Record<string, string> = {
  'pt-BR': 'https://t.me/jogai_br',
  'es-MX': 'https://t.me/jogai_mx',
};

export default function TelegramCTA() {
  const t = useTranslations('telegram');
  const locale = useLocale();
  const channelUrl = CHANNEL_MAP[locale] || CHANNEL_MAP['pt-BR'];

  return (
    <section className="mx-auto max-w-4xl px-4 py-20 text-center">
      <div className="rounded-2xl border border-jogai-border bg-jogai-card p-10">
        <h2 className="mb-4 text-3xl font-bold">{t('title')}</h2>
        <p className="mb-8 text-jogai-muted">{t('description')}</p>
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <a
            href="https://t.me/jogai_bot"
            className="rounded-lg bg-jogai-accent px-8 py-3 font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
          >
            {t('cta_bot')}
          </a>
          <a
            href={channelUrl}
            className="rounded-lg border border-jogai-border px-8 py-3 font-bold text-jogai-text transition hover:border-jogai-accent"
          >
            {t('cta_channel')}
          </a>
        </div>
      </div>
    </section>
  );
}
