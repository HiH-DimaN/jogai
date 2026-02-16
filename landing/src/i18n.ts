import {getRequestConfig} from 'next-intl/server';
import {notFound} from 'next/navigation';

export const locales = ['pt-BR', 'es-MX'] as const;
export const defaultLocale = 'pt-BR';

export type Locale = (typeof locales)[number];

export default getRequestConfig(async ({locale}) => {
  if (!locales.includes(locale as Locale)) notFound();

  return {
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});
