'use client';

import {useTranslations} from 'next-intl';

const steps = [
  {key: 'step1', icon: '1'},
  {key: 'step2', icon: '2'},
  {key: 'step3', icon: '3'},
] as const;

export default function HowItWorks() {
  const t = useTranslations('how_it_works');

  return (
    <section className="mx-auto max-w-6xl px-4 py-16">
      <h2 className="mb-12 text-center text-3xl font-bold">{t('title')}</h2>
      <div className="grid gap-8 md:grid-cols-3">
        {steps.map(({key, icon}) => (
          <div key={key} className="rounded-xl border border-jogai-border bg-jogai-card p-6 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-jogai-accent text-xl font-bold text-jogai-bg">
              {icon}
            </div>
            <h3 className="mb-2 text-lg font-bold text-jogai-accent">
              {t(`${key}_title`)}
            </h3>
            <p className="text-sm text-jogai-muted">
              {t(`${key}_desc`)}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
