import {getTranslations} from 'next-intl/server';
import {Metadata} from 'next';
import {guides} from '@/data/guides';
import {Link} from '@/navigation';

type Props = {
  params: {locale: string};
};

export async function generateMetadata({params: {locale}}: Props): Promise<Metadata> {
  const t = await getTranslations({locale, namespace: 'guides_page'});
  return {
    title: t('meta_title'),
    description: t('meta_description'),
    alternates: {
      languages: {
        'pt-BR': '/pt-BR/guides',
        'es-MX': '/es-MX/guides',
      },
    },
    openGraph: {
      title: t('meta_title'),
      description: t('meta_description'),
      locale,
    },
  };
}

export default async function GuidesPage({params: {locale}}: Props) {
  const t = await getTranslations({locale});

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: t('guides_page.title'),
    itemListElement: guides.map((guide, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: t(guide.titleKey),
      url: `https://jogai.fun/${locale}/guides/${guide.slug}`,
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
        <span className="text-jogai-text">{t('breadcrumb.guides')}</span>
      </nav>

      <section className="mx-auto max-w-6xl px-4 py-12">
        <h1 className="mb-2 text-4xl font-extrabold">{t('guides_page.title')}</h1>
        <p className="mb-10 text-lg text-jogai-muted">{t('guides_page.subtitle')}</p>

        <div className="grid gap-6 md:grid-cols-3">
          {guides.map((guide) => (
            <Link
              key={guide.slug}
              href={`/guides/${guide.slug}`}
              className="group rounded-xl border border-jogai-border bg-jogai-card p-6 transition hover:border-jogai-accent/50"
            >
              <h2 className="mb-2 text-lg font-bold text-jogai-text group-hover:text-jogai-accent">
                {t(guide.titleKey)}
              </h2>
              <p className="mb-4 text-sm text-jogai-muted">
                {t(guide.descriptionKey)}
              </p>
              <span className="text-xs text-jogai-muted">
                {t('guide.read_time', {minutes: String(guide.readTime)})}
              </span>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}
