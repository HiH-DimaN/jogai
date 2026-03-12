import {getTranslations} from 'next-intl/server';
import {Metadata} from 'next';
import {Link} from '@/navigation';

type Props = {
  params: {locale: string};
};

export async function generateMetadata({params: {locale}}: Props): Promise<Metadata> {
  const t = await getTranslations({locale, namespace: 'terms_page'});
  return {
    title: t('meta_title'),
    description: t('meta_description'),
    alternates: {
      languages: {
        'pt-BR': 'https://jogai.fun/pt-BR/terms',
        'es-MX': 'https://jogai.fun/es-MX/terms',
        'x-default': 'https://jogai.fun/pt-BR/terms',
      },
    },
  };
}

export default async function TermsPage({params: {locale}}: Props) {
  const t = await getTranslations({locale, namespace: 'terms_page'});

  return (
    <>
      <nav className="mx-auto max-w-4xl px-4 pt-6 text-sm text-jogai-muted">
        <Link href="/" className="hover:text-jogai-text">
          {t('breadcrumb_home')}
        </Link>
        <span className="mx-2">&rsaquo;</span>
        <span className="text-jogai-text">{t('title')}</span>
      </nav>

      <section className="mx-auto max-w-4xl px-4 py-12">
        <h1 className="mb-2 text-4xl font-extrabold">{t('title')}</h1>
        <p className="mb-10 text-sm text-jogai-muted">{t('last_updated')}</p>

        <div className="space-y-8 text-sm leading-relaxed text-jogai-muted">
          <div>
            <h2 className="mb-3 text-lg font-bold text-jogai-text">{t('section1_title')}</h2>
            <p>{t('section1_text')}</p>
          </div>
          <div>
            <h2 className="mb-3 text-lg font-bold text-jogai-text">{t('section2_title')}</h2>
            <p>{t('section2_text')}</p>
          </div>
          <div>
            <h2 className="mb-3 text-lg font-bold text-jogai-text">{t('section3_title')}</h2>
            <p>{t('section3_text')}</p>
          </div>
          <div>
            <h2 className="mb-3 text-lg font-bold text-jogai-text">{t('section4_title')}</h2>
            <p>{t('section4_text')}</p>
          </div>
          <div>
            <h2 className="mb-3 text-lg font-bold text-jogai-text">{t('section5_title')}</h2>
            <p>{t('section5_text')}</p>
          </div>
          <div>
            <h2 className="mb-3 text-lg font-bold text-jogai-text">{t('section6_title')}</h2>
            <p>{t('section6_text')}</p>
          </div>
        </div>
      </section>
    </>
  );
}
