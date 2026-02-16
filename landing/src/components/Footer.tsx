'use client';

import {useTranslations} from 'next-intl';

export default function Footer() {
  const t = useTranslations('footer');

  return (
    <footer className="border-t border-jogai-border">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className="flex flex-col items-center gap-4 text-center text-sm text-jogai-muted md:flex-row md:justify-between md:text-left">
          <div>
            <p className="font-bold text-jogai-accent">Jogai</p>
            <p className="mt-1">{t('disclaimer')}</p>
          </div>
          <div className="flex gap-4">
            <a href="#" className="transition hover:text-jogai-text">
              {t('privacy')}
            </a>
            <a href="#" className="transition hover:text-jogai-text">
              {t('terms')}
            </a>
          </div>
        </div>
        <p className="mt-4 text-center text-xs text-jogai-muted">{t('copyright')}</p>
      </div>
    </footer>
  );
}
