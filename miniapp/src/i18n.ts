import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData?: string;
        initDataUnsafe?: {
          user?: {
            id?: number;
            first_name?: string;
            last_name?: string;
            username?: string;
            language_code?: string;
          };
        };
        ready?: () => void;
        expand?: () => void;
        setHeaderColor?: (color: string) => void;
        setBackgroundColor?: (color: string) => void;
      };
    };
  }
}

export const getTelegramLocale = (): string => {
  const lang =
    window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code || 'pt';
  return lang.startsWith('es') ? 'es-MX' : 'pt-BR';
};

export const getBackendLocale = (frontLocale: string): string => {
  return frontLocale === 'es-MX' ? 'es_MX' : 'pt_BR';
};

i18n
  .use(Backend)
  .use(initReactI18next)
  .init({
    lng: getTelegramLocale(),
    fallbackLng: 'pt-BR',
    supportedLngs: ['pt-BR', 'es-MX'],
    backend: { loadPath: '/locales/{{lng}}/translation.json' },
    interpolation: { escapeValue: false },
  });

export default i18n;
