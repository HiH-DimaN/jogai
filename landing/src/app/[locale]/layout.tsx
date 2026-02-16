import {NextIntlClientProvider, useMessages} from 'next-intl';
import {getTranslations} from 'next-intl/server';
import {ReactNode} from 'react';
import '../globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

type Props = {
  children: ReactNode;
  params: {locale: string};
};

export async function generateMetadata({params: {locale}}: Props) {
  const t = await getTranslations({locale, namespace: 'meta'});
  return {
    title: t('title'),
    description: t('description'),
    openGraph: {
      title: t('title'),
      description: t('description'),
      locale: locale,
      type: 'website',
    },
    alternates: {
      languages: {
        'pt-BR': '/pt-BR',
        'es-MX': '/es-MX',
      },
    },
  };
}

export default function LocaleLayout({children, params: {locale}}: Props) {
  const messages = useMessages();
  return (
    <html lang={locale} className="dark">
      <body className="min-h-screen bg-jogai-bg text-jogai-text antialiased">
        <NextIntlClientProvider locale={locale} messages={messages}>
          <Header />
          <main>{children}</main>
          <Footer />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
