import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../api/client';
import { useUserStore } from '../stores/user';
import type { ReferralStats } from '../types';

export default function Referrals() {
  const { t } = useTranslation();
  const { user } = useUserStore();

  const [stats, setStats] = useState<ReferralStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get<ReferralStats>('/referrals/stats');
        setStats(res.data);
      } catch {
        // Not authenticated or error
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchStats();
    } else {
      setLoading(false);
    }
  }, [user]);

  const copyLink = async () => {
    if (!stats) return;
    try {
      await navigator.clipboard.writeText(stats.referral_link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for Telegram WebApp
      const input = document.createElement('input');
      input.value = stats.referral_link;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const shareToTelegram = () => {
    if (!stats) return;
    window.open(`https://t.me/share/url?url=${encodeURIComponent(stats.referral_link)}&text=${encodeURIComponent(t('referral_share_text'))}`, '_blank');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center pt-20">
        <p className="text-jogai-muted">{t('loading')}</p>
      </div>
    );
  }

  if (!user || !stats) {
    return (
      <div className="text-center pt-20">
        <p className="text-jogai-muted">{t('referral_no_code')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-jogai-text">{t('referral_title')}</h1>
        <p className="text-jogai-muted text-sm">{t('referral_subtitle')}</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-jogai-card border border-jogai-border rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-jogai-accent">{stats.jogai_coins}</div>
          <div className="text-jogai-muted text-xs mt-1">{t('referral_coins')}</div>
        </div>
        <div className="bg-jogai-card border border-jogai-border rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-jogai-green">{stats.referral_count}</div>
          <div className="text-jogai-muted text-xs mt-1">{t('referral_invited')}</div>
        </div>
      </div>

      {/* Referral link */}
      <div className="bg-jogai-card border border-jogai-border rounded-xl p-4 space-y-3">
        <div className="text-jogai-muted text-sm">{t('referral_your_link')}</div>
        <div className="bg-jogai-bg rounded-lg p-3 text-jogai-text text-sm break-all">
          {stats.referral_link}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={copyLink}
            className="bg-jogai-accent hover:bg-jogai-accent/80 text-white font-semibold py-2.5 rounded-lg transition-colors text-sm"
          >
            {copied ? t('referral_copied') : t('referral_copy')}
          </button>
          <button
            onClick={shareToTelegram}
            className="bg-jogai-card border border-jogai-accent text-jogai-accent hover:bg-jogai-accent/10 font-semibold py-2.5 rounded-lg transition-colors text-sm"
          >
            {t('referral_share')}
          </button>
        </div>
      </div>

      {/* Reward info */}
      <div className="text-center text-jogai-muted text-sm">
        {t('referral_reward')}
      </div>
    </div>
  );
}
