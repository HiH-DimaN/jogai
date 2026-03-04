import {getTranslations} from 'next-intl/server';
import {Metadata} from 'next';
import {fetchBonuses} from '@/lib/api';
import JogaiScoreBadge from '@/components/JogaiScoreBadge';
import {Link} from '@/navigation';

type Props = {
  params: {locale: string};
};

export async function generateMetadata({params: {locale}}: Props): Promise<Metadata> {
  const t = await getTranslations({locale, namespace: 'bonuses_page'});
  return {
    title: t('meta_title'),
    description: t('meta_description'),
    alternates: {
      languages: {
        'pt-BR': 'https://jogai.fun/pt-BR/bonuses',
        'es-MX': 'https://jogai.fun/es-MX/bonuses',
        'x-default': 'https://jogai.fun/pt-BR/bonuses',
      },
    },
    openGraph: {
      title: t('meta_title'),
      description: t('meta_description'),
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

export default async function BonusesPage({params: {locale}}: Props) {
  const t = await getTranslations({locale});
  const bonuses = await fetchBonuses(locale);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: t('bonuses_page.title'),
    itemListElement: bonuses.map((bonus, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: `${bonus.casino_name} — ${bonus.title}`,
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
        <span className="mx-2">&rsaquo;</span>
        <span className="text-jogai-text">{t('breadcrumb.bonuses')}</span>
      </nav>

      <section className="mx-auto max-w-6xl px-4 py-12">
        <h1 className="mb-2 text-4xl font-extrabold">{t('bonuses_page.title')}</h1>
        <p className="mb-10 text-lg text-jogai-muted">{t('bonuses_page.subtitle')}</p>

        {bonuses.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-jogai-border text-jogai-muted">
                  <th className="px-4 py-3 font-medium">{t('bonuses.casino')}</th>
                  <th className="px-4 py-3 font-medium">{t('bonuses.bonus')}</th>
                  <th className="px-4 py-3 font-medium">{t('bonuses.wagering')}</th>
                  <th className="px-4 py-3 font-medium">{t('bonuses.deadline')}</th>
                  <th className="px-4 py-3 font-medium">{t('bonuses.score')}</th>
                  <th className="px-4 py-3 font-medium">{t('bonuses.verdict')}</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody>
                {bonuses.map((bonus) => (
                  <tr
                    key={bonus.id}
                    className="border-b border-jogai-border transition hover:bg-jogai-card"
                  >
                    <td className="px-4 py-4">
                      <Link
                        href={`/casinos/${bonus.casino_slug}`}
                        className="font-bold text-jogai-text hover:text-jogai-accent"
                      >
                        {bonus.casino_name}
                      </Link>
                    </td>
                    <td className="px-4 py-4">
                      <div className="text-jogai-accent">{bonus.title}</div>
                      <div className="text-xs text-jogai-muted">
                        {bonus.formatted_max_bonus}
                        {bonus.free_spins > 0 && ` + ${bonus.free_spins} FS`}
                      </div>
                      <div className="mt-1 flex gap-1">
                        {bonus.no_deposit && (
                          <span className="rounded bg-jogai-green/20 px-1.5 py-0.5 text-xs text-jogai-green">
                            {t('bonuses_page.no_deposit_label')}
                          </span>
                        )}
                        {bonus.free_spins > 0 && (
                          <span className="rounded bg-jogai-accent/20 px-1.5 py-0.5 text-xs text-jogai-accent">
                            {t('bonuses_page.free_spins_label')}
                          </span>
                        )}
                      </div>
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
          <div className="rounded-xl border border-jogai-border bg-jogai-card px-6 py-16 text-center">
            <h2 className="mb-2 text-2xl font-bold text-jogai-text">
              {t('bonuses_empty.title')}
            </h2>
            <p className="mx-auto mb-6 max-w-md text-jogai-muted">
              {t('bonuses_empty.description')}
            </p>
            <a
              href="https://t.me/jogai_bot"
              className="inline-block rounded-lg bg-jogai-accent px-8 py-3 font-bold text-jogai-bg transition hover:bg-jogai-accent/90"
            >
              {t('bonuses_empty.cta')}
            </a>
          </div>
        )}
      </section>
    </>
  );
}
