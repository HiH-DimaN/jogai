import {getTranslations} from 'next-intl/server';
import {Metadata} from 'next';
import {notFound} from 'next/navigation';
import {getGuideBySlug, guides} from '@/data/guides';
import {Link} from '@/navigation';

type Props = {
  params: {locale: string; slug: string};
};

export async function generateMetadata({params: {locale, slug}}: Props): Promise<Metadata> {
  const guide = getGuideBySlug(slug);
  if (!guide) return {};

  const t = await getTranslations({locale});
  const title = `${t(guide.titleKey)} — Jogai`;
  const description = t(guide.descriptionKey);

  return {
    title,
    description,
    alternates: {
      languages: {
        'pt-BR': `/pt-BR/guides/${slug}`,
        'es-MX': `/es-MX/guides/${slug}`,
      },
    },
    openGraph: {
      title,
      description,
      locale,
      type: 'article',
    },
  };
}

function MarkdownContent({content}: {content: string}) {
  // Simple markdown to HTML: headings, paragraphs, bold, lists
  const lines = content.split('\n');
  const elements: JSX.Element[] = [];
  let listItems: string[] = [];
  let key = 0;

  function flushList() {
    if (listItems.length > 0) {
      elements.push(
        <ul key={key++} className="mb-4 list-disc space-y-1 pl-6 text-jogai-muted">
          {listItems.map((item, i) => (
            <li key={i} dangerouslySetInnerHTML={{__html: processBold(item)}} />
          ))}
        </ul>
      );
      listItems = [];
    }
  }

  function processBold(text: string): string {
    return text.replace(
      /\*\*(.+?)\*\*/g,
      '<strong class="text-jogai-text font-semibold">$1</strong>'
    );
  }

  for (const line of lines) {
    if (line.startsWith('## ')) {
      flushList();
      elements.push(
        <h2 key={key++} className="mb-3 mt-8 text-2xl font-bold text-jogai-text">
          {line.slice(3)}
        </h2>
      );
    } else if (line.startsWith('### ')) {
      flushList();
      elements.push(
        <h3 key={key++} className="mb-2 mt-6 text-xl font-bold text-jogai-accent">
          {line.slice(4)}
        </h3>
      );
    } else if (line.startsWith('- ')) {
      listItems.push(line.slice(2));
    } else if (line.trim() === '') {
      flushList();
    } else {
      flushList();
      elements.push(
        <p
          key={key++}
          className="mb-4 text-jogai-muted"
          dangerouslySetInnerHTML={{__html: processBold(line)}}
        />
      );
    }
  }
  flushList();

  return <div>{elements}</div>;
}

export default async function GuideDetailPage({params: {locale, slug}}: Props) {
  const guide = getGuideBySlug(slug);
  if (!guide) notFound();

  const t = await getTranslations({locale});
  const title = t(guide.titleKey);
  const content = t(guide.contentKey);
  const readTime = String(guide.readTime);

  const otherGuides = guides.filter((g) => g.slug !== slug);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: title,
    description: t(guide.descriptionKey),
    publisher: {
      '@type': 'Organization',
      name: 'Jogai',
    },
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
        name: t('breadcrumb.guides'),
        item: `https://jogai.fun/${locale}/guides`,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: title,
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
      <nav className="mx-auto max-w-4xl px-4 pt-6 text-sm text-jogai-muted">
        <Link href="/" className="hover:text-jogai-text">
          {t('breadcrumb.home')}
        </Link>
        <span className="mx-2">›</span>
        <Link href="/guides" className="hover:text-jogai-text">
          {t('breadcrumb.guides')}
        </Link>
        <span className="mx-2">›</span>
        <span className="text-jogai-text">{title}</span>
      </nav>

      <article className="mx-auto max-w-4xl px-4 py-12">
        <header className="mb-8">
          <h1 className="mb-3 text-4xl font-extrabold">{title}</h1>
          <span className="text-sm text-jogai-muted">
            {t('guide.read_time', {minutes: readTime})}
          </span>
        </header>

        <div className="rounded-xl border border-jogai-border bg-jogai-card p-6 md:p-8">
          <MarkdownContent content={content} />
        </div>

        {/* Related guides */}
        {otherGuides.length > 0 && (
          <div className="mt-12">
            <h2 className="mb-4 text-xl font-bold">{t('guide.related')}</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {otherGuides.map((g) => (
                <Link
                  key={g.slug}
                  href={`/guides/${g.slug}`}
                  className="group rounded-xl border border-jogai-border bg-jogai-card p-4 transition hover:border-jogai-accent/50"
                >
                  <h3 className="font-bold text-jogai-text group-hover:text-jogai-accent">
                    {t(g.titleKey)}
                  </h3>
                  <p className="mt-1 text-sm text-jogai-muted">{t(g.descriptionKey)}</p>
                </Link>
              ))}
            </div>
          </div>
        )}

        <div className="mt-8">
          <Link
            href="/guides"
            className="text-jogai-accent hover:underline"
          >
            ← {t('guide.back')}
          </Link>
        </div>
      </article>
    </>
  );
}
