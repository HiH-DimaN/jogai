import {getTranslations} from 'next-intl/server';
import {fetchCasinos} from '@/lib/api';
import CasinoTable from '@/components/CasinoTable';
import HowItWorks from '@/components/HowItWorks';
import TelegramCTA from '@/components/TelegramCTA';
import {Link} from '@/navigation';

type Props = {
  params: {locale: string};
};

export default async function HomePage({params: {locale}}: Props) {
  const t = await getTranslations({locale});

  const casinos = await fetchCasinos(locale);
  const topCasinos = casinos.slice(0, 4);

  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden px-4 py-20 text-center">
        <div className="absolute inset-0 bg-gradient-to-b from-jogai-accent/10 to-transparent" />
        <div className="relative mx-auto max-w-4xl">
          <h1 className="mb-4 text-5xl font-extrabold tracking-tight text-jogai-accent md:text-7xl">
            {t('hero.title')}
          </h1>
          <p className="mb-2 text-xl text-jogai-text md:text-2xl">
            {t('hero.subtitle')}
          </p>
          <p className="mx-auto mb-8 max-w-2xl text-jogai-muted">
            {t('hero.description')}
          </p>
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <a
              href="https://t.me/jogai_bot"
              className="rounded-lg bg-jogai-accent px-8 py-3 font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
            >
              {t('hero.cta')}
            </a>
            <Link
              href="/casinos"
              className="rounded-lg border border-jogai-border px-8 py-3 font-bold text-jogai-text transition hover:border-jogai-accent"
            >
              {t('hero.cta_secondary')}
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="mb-12 text-center text-3xl font-bold">{t('features.title')}</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {(['analysis', 'score', 'quiz', 'tracker'] as const).map((key) => (
            <div key={key} className="rounded-xl border border-jogai-border bg-jogai-card p-6">
              <h3 className="mb-2 text-lg font-bold text-jogai-accent">
                {t(`features.${key}_title`)}
              </h3>
              <p className="text-sm text-jogai-muted">
                {t(`features.${key}_desc`)}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Casino Table */}
      <section className="mx-auto max-w-6xl px-4 py-16" id="casinos">
        <h2 className="mb-2 text-center text-3xl font-bold">{t('casinos.title')}</h2>
        <p className="mb-8 text-center text-jogai-muted">{t('casinos.subtitle')}</p>
        <CasinoTable casinos={topCasinos} />
        <div className="mt-6 text-center">
          <Link
            href="/casinos"
            className="rounded-lg border border-jogai-border px-6 py-2 text-sm font-bold text-jogai-text transition hover:border-jogai-accent"
          >
            {t('casinos.view_all')}
          </Link>
        </div>
      </section>

      {/* How It Works */}
      <HowItWorks />

      {/* Telegram CTA */}
      <TelegramCTA />
    </>
  );
}
