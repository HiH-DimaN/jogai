import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';

export default function Layout({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation();
  const location = useLocation();

  const navItems = [
    { path: '/', label: t('nav_home'), icon: '🏠' },
    { path: '/analyze', label: t('nav_analyze'), icon: '🔍' },
  ];

  return (
    <div className="min-h-screen bg-jogai-bg flex flex-col">
      <header className="bg-jogai-card border-b border-jogai-border px-4 py-3">
        <h1 className="text-lg font-bold text-jogai-accent text-center">
          {t('app_name')}
        </h1>
      </header>

      <main className="flex-1 px-4 py-4 pb-20">{children}</main>

      <nav className="fixed bottom-0 left-0 right-0 bg-jogai-card border-t border-jogai-border">
        <div className="flex">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex-1 flex flex-col items-center py-3 text-xs transition-colors ${
                location.pathname === item.path
                  ? 'text-jogai-accent'
                  : 'text-jogai-muted'
              }`}
            >
              <span className="text-lg mb-0.5">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
}
