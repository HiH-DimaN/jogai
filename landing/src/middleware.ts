import createMiddleware from 'next-intl/middleware';
import {NextRequest, NextResponse} from 'next/server';
import {locales, defaultLocale} from './i18n';

const intlMiddleware = createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'always',
});

export default function middleware(request: NextRequest) {
  const {pathname} = request.nextUrl;

  // Root path: permanent redirect to default locale for SEO
  if (pathname === '/') {
    const url = request.nextUrl.clone();
    url.pathname = `/${defaultLocale}`;
    return NextResponse.redirect(url, 308);
  }

  // Paths without locale prefix: redirect to default locale
  // e.g. /casinos → /pt-BR/casinos, /bonuses → /pt-BR/bonuses
  const hasLocale = locales.some((l) => pathname.startsWith(`/${l}`));
  if (!hasLocale) {
    const url = request.nextUrl.clone();
    url.pathname = `/${defaultLocale}${pathname}`;
    return NextResponse.redirect(url, 308);
  }

  return intlMiddleware(request);
}

export const config = {
  // Match all paths except _next, api, static files
  matcher: ['/((?!_next|api|img|.*\\..*).*)'],
};
