'use client';

import {useLocale} from 'next-intl';
import {usePathname, useRouter} from '@/navigation';
import {locales, type Locale} from '@/i18n';

const LOCALE_LABELS: Record<string, string> = {
  'pt-BR': 'PT',
  'es-MX': 'ES',
};

export default function LocaleSwitcher() {
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();

  // Hide if only 1 locale
  if (locales.length <= 1) return null;

  return (
    <select
      value={locale}
      onChange={(e) => router.replace(pathname, {locale: e.target.value as Locale})}
      className="rounded border border-jogai-border bg-jogai-card px-2 py-1 text-sm text-jogai-text"
    >
      {locales.map((loc) => (
        <option key={loc} value={loc}>
          {LOCALE_LABELS[loc] ?? loc}
        </option>
      ))}
    </select>
  );
}
