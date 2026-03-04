import {getTranslations} from 'next-intl/server';
import {Metadata} from 'next';
import {notFound} from 'next/navigation';
import {fetchCasino} from '@/lib/api';
import JogaiScoreBadge from '@/components/JogaiScoreBadge';
import {Link} from '@/navigation';

type Props = {
  params: {locale: string; slug: string};
};

export async function generateMetadata({params: {locale, slug}}: Props): Promise<Metadata> {
  const casino = await fetchCasino(slug, locale);
  if (!casino) return {};

  const t = await getTranslations({locale, namespace: 'casino_detail'});
  const title = t('meta_title', {name: casino.name});
  const description = t('meta_description', {name: casino.name});

  return {
    title,
    description,
    alternates: {
      languages: {
        'pt-BR': `https://jogai.fun/pt-BR/casinos/${slug}`,
        'es-MX': `https://jogai.fun/es-MX/casinos/${slug}`,
        'x-default': `https://jogai.fun/pt-BR/casinos/${slug}`,
      },
    },
    openGraph: {
      title,
      description,
      locale,
    },
  };
}

type VerdictKey = 'verdict_excellent' | 'verdict_good' | 'verdict_caution' | 'verdict_bad';

function VerdictBadge({verdictKey, label}: {verdictKey: string; label: string}) {
  const colorMap: Record<string, string> = {
    verdict_excellent: 'bg-jogai-green/20 text-jogai-green',
    verdict_good: 'bg-jogai-accent/20 text-jogai-accent',
    verdict_caution: 'bg-yellow-500/20 text-yellow-400',
    verdict_bad: 'bg-jogai-red/20 text-jogai-red',
  };
  return (
    <span
      className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${colorMap[verdictKey] || colorMap.verdict_caution}`}
    >
      {label}
    </span>
  );
}

export default async function CasinoDetailPage({params: {locale, slug}}: Props) {
  const casino = await fetchCasino(slug, locale);
  if (!casino) notFound();

  const t = await getTranslations({locale});

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: casino.name,
    description: casino.description,
  };

  const breadcrumbLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: t('breadcrumb.home'),
        item: `https://jogai.fun/${locale}`,
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: t('breadcrumb.casinos'),
        item: `https://jogai.fun/${locale}/casinos`,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: casino.name,
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{__html: JSON.stringify(jsonLd)}}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{__html: JSON.stringify(breadcrumbLd)}}
      />

      {/* Breadcrumb */}
      <nav className="mx-auto max-w-6xl px-4 pt-6 text-sm text-jogai-muted">
        <Link href="/" className="hover:text-jogai-text">
          {t('breadcrumb.home')}
        </Link>
        <span className="mx-2">›</span>
        <Link href="/casinos" className="hover:text-jogai-text">
          {t('breadcrumb.casinos')}
        </Link>
        <span className="mx-2">›</span>
        <span className="text-jogai-text">{casino.name}</span>
      </nav>

      <section className="mx-auto max-w-6xl px-4 py-12">
        {/* Casino header */}
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 className="text-4xl font-extrabold">{casino.name}</h1>
          </div>
          {casino.affiliate_link && (
            <a
              href={casino.affiliate_link}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg bg-jogai-accent px-6 py-3 text-center font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
            >
              {t('casino_detail.create_account', {name: casino.name})}
            </a>
          )}
        </div>

        {/* Overview */}
        <div className="mb-8 rounded-xl border border-jogai-border bg-jogai-card p-6">
          <h2 className="mb-4 text-xl font-bold">{t('casino_detail.overview')}</h2>
          {casino.description && (
            <p className="mb-6 text-jogai-muted">{casino.description}</p>
          )}

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {casino.min_deposit_formatted && (
              <div>
                <span className="text-sm text-jogai-muted">{t('casino_detail.deposit')}</span>
                <p className="font-bold">{casino.min_deposit_formatted}</p>
              </div>
            )}
            {casino.withdrawal_time && (
              <div>
                <span className="text-sm text-jogai-muted">{t('casino_detail.withdrawal')}</span>
                <p className="font-bold">{casino.withdrawal_time}</p>
              </div>
            )}
            <div>
              <span className="text-sm text-jogai-muted">{t('casino_detail.payments')}</span>
              <div className="mt-1 flex gap-1">
                {casino.pix_supported && (
                  <span className="rounded bg-jogai-green/20 px-1.5 py-0.5 text-xs font-medium text-jogai-green">
                    PIX
                  </span>
                )}
                {casino.spei_supported && (
                  <span className="rounded bg-jogai-green/20 px-1.5 py-0.5 text-xs font-medium text-jogai-green">
                    SPEI
                  </span>
                )}
                {casino.crypto_supported && (
                  <span className="rounded bg-jogai-green/20 px-1.5 py-0.5 text-xs font-medium text-jogai-green">
                    {t('casinos.crypto')}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Bonuses */}
        <h2 className="mb-4 text-2xl font-bold">{t('casino_detail.bonuses_title')}</h2>
        {casino.bonuses.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-jogai-border text-jogai-muted">
                  <th className="px-4 py-3 font-medium">{t('bonuses.bonus')}</th>
                  <th className="px-4 py-3 font-medium">{t('bonuses.wagering')}</th>
                  <th className="px-4 py-3 font-medium">{t('bonuses.deadline')}</th>
                  <th className="px-4 py-3 font-medium">{t('bonuses.score')}</th>
                  <th className="px-4 py-3 font-medium">{t('bonuses.verdict')}</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody>
                {casino.bonuses.map((bonus) => (
                  <tr
                    key={bonus.id}
                    className="border-b border-jogai-border transition hover:bg-jogai-card"
                  >
                    <td className="px-4 py-4">
                      <div className="font-bold text-jogai-accent">{bonus.title}</div>
                      <div className="text-xs text-jogai-muted">
                        {bonus.formatted_max_bonus}
                        {bonus.free_spins > 0 && ` + ${bonus.free_spins} FS`}
                      </div>
                      {bonus.no_deposit && (
                        <span className="mt-1 inline-block rounded bg-jogai-green/20 px-1.5 py-0.5 text-xs text-jogai-green">
                          {t('bonuses_page.no_deposit_label')}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-4">{bonus.wagering_multiplier}x</td>
                    <td className="px-4 py-4">
                      {bonus.wagering_deadline_days} {t('bonuses.days')}
                    </td>
                    <td className="px-4 py-4">
                      <JogaiScoreBadge score={bonus.jogai_score} />
                    </td>
                    <td className="px-4 py-4">
                      <VerdictBadge
                        verdictKey={bonus.verdict_key}
                        label={t(`bonuses.${bonus.verdict_key}`)}
                      />
                    </td>
                    <td className="px-4 py-4">
                      {bonus.affiliate_link && (
                        <a
                          href={bonus.affiliate_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="rounded-lg bg-jogai-accent px-4 py-2 text-xs font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
                        >
                          {t('bonuses.get_bonus')}
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="rounded-xl border border-jogai-border bg-jogai-card px-6 py-12 text-center">
            <p className="mb-4 text-jogai-muted">
              {t('casino_detail.no_bonuses')}
            </p>
            <a
              href="https://t.me/jogai_bot"
              className="inline-block rounded-lg bg-jogai-accent px-6 py-2 font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
            >
              {t('casino_detail.no_bonuses_cta')}
            </a>
          </div>
        )}
      </section>
    </>
  );
}
