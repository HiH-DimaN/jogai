import {NextIntlClientProvider, useMessages} from 'next-intl';
import {getTranslations} from 'next-intl/server';
import {ReactNode} from 'react';
import Script from 'next/script';
import '../globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

const SITE_URL = 'https://jogai.fun';

type Props = {
  children: ReactNode;
  params: {locale: string};
};

export async function generateMetadata({params: {locale}}: Props) {
  const t = await getTranslations({locale, namespace: 'meta'});
  return {
    metadataBase: new URL(SITE_URL),
    title: t('title'),
    description: t('description'),
    openGraph: {
      title: t('title'),
      description: t('description'),
      locale: locale,
      type: 'website',
      images: [
        {
          url: '/og-image.png',
          width: 1200,
          height: 630,
          alt: 'Jogai — AI Gambling Analytics',
        },
      ],
    },
    alternates: {
      languages: {
        'pt-BR': `${SITE_URL}/pt-BR`,
        'es-MX': `${SITE_URL}/es-MX`,
        'x-default': `${SITE_URL}/pt-BR`,
      },
    },
    verification: {
      google: 'WDtNKpJiYXoLUUb-GALCIbleh3kXWH_aLQtIWjokQ3A',
    },
  };
}

export default function LocaleLayout({children, params: {locale}}: Props) {
  const messages = useMessages();
  const gaId = process.env.NEXT_PUBLIC_GA_ID;
  return (
    <html lang={locale} className="dark">
      <body className="min-h-screen bg-jogai-bg text-jogai-text antialiased">
        {gaId && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
              strategy="afterInteractive"
            />
            <Script id="ga4-init" strategy="afterInteractive">
              {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${gaId}');`}
            </Script>
          </>
        )}
        <NextIntlClientProvider locale={locale} messages={messages}>
          <Header />
          <main>{children}</main>
          <Footer />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
