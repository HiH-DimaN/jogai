'use client';

import {useTranslations} from 'next-intl';
import LocaleSwitcher from './LocaleSwitcher';

export default function Header() {
  const t = useTranslations('header');

  return (
    <header className="sticky top-0 z-50 border-b border-jogai-border bg-jogai-bg/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <a href="/" className="text-xl font-extrabold text-jogai-accent">
          Jogai
        </a>
        <nav className="hidden items-center gap-6 text-sm md:flex">
          <a href="#casinos" className="text-jogai-muted transition hover:text-jogai-text">
            {t('casinos')}
          </a>
          <a href="#bonuses" className="text-jogai-muted transition hover:text-jogai-text">
            {t('bonuses')}
          </a>
          <a href="#" className="text-jogai-muted transition hover:text-jogai-text">
            {t('guides')}
          </a>
        </nav>
        <div className="flex items-center gap-4">
          <LocaleSwitcher />
          <a
            href="https://t.me/jogai_bot"
            className="rounded-lg bg-jogai-accent px-4 py-2 text-sm font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
          >
            Telegram
          </a>
        </div>
      </div>
    </header>
  );
}
