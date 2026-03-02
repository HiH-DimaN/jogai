import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../api/client';
import type { Bonus } from '../types';
import BonusCard from '../components/BonusCard';
import { useUserStore } from '../stores/user';

export default function Home() {
  const { t } = useTranslation();
  const user = useUserStore((s) => s.user);
  const [bonuses, setBonuses] = useState<Bonus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchBonuses = async () => {
      try {
        const geo = user?.geo || 'BR';
        const res = await api.get('/bonuses', { params: { geo } });
        setBonuses(res.data.bonuses);
      } catch {
        setError(t('error_generic'));
      } finally {
        setLoading(false);
      }
    };
    fetchBonuses();
  }, [user?.geo, t]);

  const name =
    user?.first_name ||
    window.Telegram?.WebApp?.initDataUnsafe?.user?.first_name ||
    'Jogador';

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-jogai-text">
          {t('greeting', { name })}
        </h2>
        <p className="text-jogai-muted text-sm mt-1">{t('home_subtitle')}</p>
      </div>

      <h3 className="text-lg font-semibold text-jogai-text">
        {t('home_title')}
      </h3>

      {loading && (
        <div className="text-center py-8 text-jogai-muted">
          {t('loading')}
        </div>
      )}

      {error && (
        <div className="text-center py-8 text-jogai-red">{error}</div>
      )}

      {!loading && !error && bonuses.length === 0 && (
        <div className="text-center py-8 text-jogai-muted">
          {t('no_bonuses')}
        </div>
      )}

      <div className="space-y-3">
        {bonuses.map((bonus) => (
          <BonusCard key={bonus.id} bonus={bonus} />
        ))}
      </div>
    </div>
  );
}
