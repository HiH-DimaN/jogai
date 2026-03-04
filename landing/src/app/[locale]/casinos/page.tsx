import {getTranslations} from 'next-intl/server';
import {Metadata} from 'next';
import {fetchCasinos} from '@/lib/api';
import JogaiScoreBadge from '@/components/JogaiScoreBadge';
import {Link} from '@/navigation';

type Props = {
  params: {locale: string};
};

export async function generateMetadata({params: {locale}}: Props): Promise<Metadata> {
  const t = await getTranslations({locale, namespace: 'casinos_page'});
  const altLocale = locale === 'pt-BR' ? 'es-MX' : 'pt-BR';
  return {
    title: t('meta_title'),
    description: t('meta_description'),
    alternates: {
      languages: {
        'pt-BR': 'https://jogai.fun/pt-BR/casinos',
        'es-MX': 'https://jogai.fun/es-MX/casinos',
        'x-default': 'https://jogai.fun/pt-BR/casinos',
      },
    },
    openGraph: {
      title: t('meta_title'),
      description: t('meta_description'),
      locale,
    },
  };
}

function PaymentBadge({available, label}: {available: boolean; label: string}) {
  if (!available) return null;
  return (
    <span className="rounded bg-jogai-green/20 px-1.5 py-0.5 text-xs font-medium text-jogai-green">
      {label}
    </span>
  );
}

export default async function CasinosPage({params: {locale}}: Props) {
  const t = await getTranslations({locale});
  const casinos = await fetchCasinos(locale);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: t('casinos_page.title'),
    itemListElement: casinos.map((casino, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: casino.name,
      url: `https://jogai.fun/${locale}/casinos/${casino.slug}`,
    })),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{__html: JSON.stringify(jsonLd)}}
      />

      {/* Breadcrumb */}
      <nav className="mx-auto max-w-6xl px-4 pt-6 text-sm text-jogai-muted">
        <Link href="/" className="hover:text-jogai-text">
          {t('breadcrumb.home')}
        </Link>
        <span className="mx-2">›</span>
        <span className="text-jogai-text">{t('breadcrumb.casinos')}</span>
      </nav>

      <section className="mx-auto max-w-6xl px-4 py-12">
        <h1 className="mb-2 text-4xl font-extrabold">{t('casinos_page.title')}</h1>
        <p className="mb-10 text-lg text-jogai-muted">{t('casinos_page.subtitle')}</p>

        <div className="grid gap-6 md:grid-cols-2">
          {casinos.map((casino) => (
            <div
              key={casino.id}
              className="rounded-xl border border-jogai-border bg-jogai-card p-6 transition hover:border-jogai-accent/50"
            >
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold text-jogai-text">{casino.name}</h2>
                  {casino.best_jogai_score !== null && (
                    <div className="mt-1">
                      <JogaiScoreBadge score={casino.best_jogai_score} />
                    </div>
                  )}
                </div>
                <span className="rounded-full bg-jogai-accent/10 px-3 py-1 text-xs font-medium text-jogai-accent">
                  {t('casinos_page.bonus_count', {count: casino.bonus_count})}
                </span>
              </div>

              {casino.description && (
                <p className="mb-4 line-clamp-2 text-sm text-jogai-muted">
                  {casino.description}
                </p>
              )}

              {casino.best_bonus && (
                <div className="mb-3 text-sm">
                  <span className="text-jogai-muted">{t('casinos_page.best_bonus')}: </span>
                  <span className="text-jogai-accent">{casino.best_bonus}</span>
                </div>
              )}

              <div className="mb-4 grid grid-cols-2 gap-2 text-sm">
                {casino.min_deposit_formatted && (
                  <div>
                    <span className="text-jogai-muted">{t('casinos_page.min_deposit')}: </span>
                    <span>{casino.min_deposit_formatted}</span>
                  </div>
                )}
                {casino.withdrawal_time && (
                  <div>
                    <span className="text-jogai-muted">{t('casinos_page.withdrawal')}: </span>
                    <span>{casino.withdrawal_time}</span>
                  </div>
                )}
              </div>

              <div className="mb-4 flex gap-1">
                <PaymentBadge available={casino.pix_supported} label="PIX" />
                <PaymentBadge available={casino.spei_supported} label="SPEI" />
                <PaymentBadge available={casino.crypto_supported} label={t('casinos.crypto')} />
              </div>

              <div className="flex gap-3">
                <Link
                  href={`/casinos/${casino.slug}`}
                  className="rounded-lg border border-jogai-border px-4 py-2 text-sm font-bold text-jogai-text transition hover:border-jogai-accent"
                >
                  {t('casinos_page.view_details')}
                </Link>
                {casino.affiliate_link && (
                  <a
                    href={casino.affiliate_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="rounded-lg bg-jogai-accent px-4 py-2 text-sm font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
                  >
                    {t('casinos_page.create_account')}
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        {casinos.length === 0 && (
          <p className="py-12 text-center text-jogai-muted">...</p>
        )}
      </section>
    </>
  );
}
