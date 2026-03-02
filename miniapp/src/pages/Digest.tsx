import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../api/client';
import { useUserStore } from '../stores/user';
import BonusCard from '../components/BonusCard';
import type { Bonus } from '../types';

interface DigestData {
  bonuses: Bonus[];
  geo: string;
  locale: string;
}

export default function Digest() {
  const { t } = useTranslation();
  const { user } = useUserStore();

  const [bonuses, setBonuses] = useState<Bonus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDigest = async () => {
      try {
        const res = await api.get<DigestData>('/digest');
        setBonuses(res.data.bonuses);
      } catch {
        setError(t('error_generic'));
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchDigest();
    } else {
      setLoading(false);
    }
  }, [user, t]);

  if (loading) {
    return (
      <div className="flex items-center justify-center pt-20">
        <p className="text-jogai-muted">{t('loading')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-jogai-text">{t('digest_title')}</h1>
        <p className="text-jogai-muted text-sm">{t('digest_subtitle')}</p>
      </div>

      {error && <p className="text-jogai-red text-sm">{error}</p>}

      {bonuses.length === 0 && !error ? (
        <p className="text-jogai-muted text-center pt-8">{t('digest_empty')}</p>
      ) : (
        bonuses.map((bonus) => <BonusCard key={bonus.id} bonus={bonus} />)
      )}

      <p className="text-jogai-muted text-xs text-center">{t('digest_updated')}</p>
    </div>
  );
}
