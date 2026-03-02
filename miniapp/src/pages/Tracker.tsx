import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../api/client';
import { useUserStore } from '../stores/user';
import { formatCurrency } from '../utils/format';
import type { BetData, BetStats, BetCreateData } from '../types';

const GAME_TYPES = ['slots', 'crash', 'sports', 'table', 'other'] as const;

export default function Tracker() {
  const { t, i18n } = useTranslation();
  const { user } = useUserStore();
  const locale = i18n.language;

  const [bets, setBets] = useState<BetData[]>([]);
  const [stats, setStats] = useState<BetStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState('');

  // Form state
  const [gameType, setGameType] = useState('slots');
  const [gameName, setGameName] = useState('');
  const [betAmount, setBetAmount] = useState('');
  const [resultAmount, setResultAmount] = useState('');
  const [note, setNote] = useState('');

  const fetchData = async () => {
    try {
      const [betsRes, statsRes] = await Promise.all([
        api.get<BetData[]>('/tracker/bets'),
        api.get<BetStats>('/tracker/stats'),
      ]);
      setBets(betsRes.data);
      setStats(statsRes.data);
    } catch {
      // Not authenticated or error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchData();
    } else {
      setLoading(false);
    }
  }, [user]);

  const handleSubmit = async () => {
    if (!betAmount || !resultAmount) return;
    setSaving(true);
    try {
      const body: BetCreateData = {
        game_type: gameType,
        game_name: gameName,
        bet_amount: parseFloat(betAmount),
        result_amount: parseFloat(resultAmount),
        note: note || undefined,
      };
      await api.post('/tracker/bets', body);
      setSavedMsg(t('tracker_saved'));
      setTimeout(() => setSavedMsg(''), 2000);
      // Reset form
      setGameName('');
      setBetAmount('');
      setResultAmount('');
      setNote('');
      setShowForm(false);
      // Refresh data
      fetchData();
    } catch {
      setSavedMsg(t('error_generic'));
      setTimeout(() => setSavedMsg(''), 2000);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center pt-20">
        <p className="text-jogai-muted">{t('loading')}</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-center pt-20">
        <p className="text-jogai-muted">{t('referral_no_code')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-jogai-text">{t('tracker_title')}</h1>
          <p className="text-jogai-muted text-sm">{t('tracker_subtitle')}</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-jogai-accent hover:bg-jogai-accent/80 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
        >
          {showForm ? '✕' : '+ ' + t('tracker_add')}
        </button>
      </div>

      {savedMsg && (
        <div className="bg-jogai-green/20 text-jogai-green text-sm rounded-lg p-3 text-center">
          {savedMsg}
        </div>
      )}

      {/* Add bet form */}
      {showForm && (
        <div className="bg-jogai-card border border-jogai-border rounded-xl p-4 space-y-3">
          <div>
            <label className="text-jogai-muted text-xs block mb-1">{t('tracker_game_type')}</label>
            <div className="flex flex-wrap gap-2">
              {GAME_TYPES.map((gt) => (
                <button
                  key={gt}
                  onClick={() => setGameType(gt)}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    gameType === gt
                      ? 'bg-jogai-accent text-white'
                      : 'bg-jogai-bg text-jogai-muted border border-jogai-border'
                  }`}
                >
                  {t(`tracker_game_type_${gt}`)}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-jogai-muted text-xs block mb-1">{t('tracker_game_name')}</label>
            <input
              type="text"
              value={gameName}
              onChange={(e) => setGameName(e.target.value)}
              placeholder={t('tracker_game_name_placeholder')}
              className="w-full bg-jogai-bg border border-jogai-border rounded-lg px-3 py-2 text-jogai-text text-sm placeholder-jogai-muted/50 focus:border-jogai-accent focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-jogai-muted text-xs block mb-1">{t('tracker_bet_amount')}</label>
              <input
                type="number"
                value={betAmount}
                onChange={(e) => setBetAmount(e.target.value)}
                placeholder="0.00"
                step="0.01"
                min="0"
                className="w-full bg-jogai-bg border border-jogai-border rounded-lg px-3 py-2 text-jogai-text text-sm placeholder-jogai-muted/50 focus:border-jogai-accent focus:outline-none"
              />
            </div>
            <div>
              <label className="text-jogai-muted text-xs block mb-1">{t('tracker_result_amount')}</label>
              <input
                type="number"
                value={resultAmount}
                onChange={(e) => setResultAmount(e.target.value)}
                placeholder="0.00"
                step="0.01"
                min="0"
                className="w-full bg-jogai-bg border border-jogai-border rounded-lg px-3 py-2 text-jogai-text text-sm placeholder-jogai-muted/50 focus:border-jogai-accent focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="text-jogai-muted text-xs block mb-1">{t('tracker_note')}</label>
            <input
              type="text"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="w-full bg-jogai-bg border border-jogai-border rounded-lg px-3 py-2 text-jogai-text text-sm placeholder-jogai-muted/50 focus:border-jogai-accent focus:outline-none"
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={saving || !betAmount || !resultAmount}
            className="w-full bg-jogai-green hover:bg-jogai-green/80 text-white font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-50"
          >
            {saving ? t('tracker_saving') : t('tracker_save')}
          </button>
        </div>
      )}

      {/* Stats */}
      {stats && stats.total_bets > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-jogai-text">{t('tracker_stats_title')}</h2>
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-jogai-card border border-jogai-border rounded-xl p-3 text-center">
              <div className="text-xl font-bold text-jogai-accent">{stats.total_bets}</div>
              <div className="text-jogai-muted text-xs">{t('tracker_total_bets')}</div>
            </div>
            <div className="bg-jogai-card border border-jogai-border rounded-xl p-3 text-center">
              <div className={`text-xl font-bold ${stats.total_profit >= 0 ? 'text-jogai-green' : 'text-jogai-red'}`}>
                {stats.total_profit >= 0 ? '+' : ''}{formatCurrency(stats.total_profit, locale)}
              </div>
              <div className="text-jogai-muted text-xs">{t('tracker_profit')}</div>
            </div>
            <div className="bg-jogai-card border border-jogai-border rounded-xl p-3 text-center">
              <div className={`text-xl font-bold ${stats.roi >= 0 ? 'text-jogai-green' : 'text-jogai-red'}`}>
                {stats.roi >= 0 ? '+' : ''}{stats.roi}%
              </div>
              <div className="text-jogai-muted text-xs">{t('tracker_roi')}</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="bg-jogai-card border border-jogai-border rounded-xl p-3">
              <div className="text-jogai-muted text-xs">{t('tracker_win_rate')}</div>
              <div className="text-jogai-text font-bold">{stats.win_rate}%</div>
            </div>
            <div className="bg-jogai-card border border-jogai-border rounded-xl p-3">
              <div className="text-jogai-muted text-xs">{t('tracker_total_wagered')}</div>
              <div className="text-jogai-text font-bold">{formatCurrency(stats.total_wagered, locale)}</div>
            </div>
            {stats.best_game && (
              <div className="bg-jogai-card border border-jogai-border rounded-xl p-3">
                <div className="text-jogai-muted text-xs">{t('tracker_best_game')}</div>
                <div className="text-jogai-green font-bold truncate">{stats.best_game}</div>
              </div>
            )}
            {stats.worst_game && (
              <div className="bg-jogai-card border border-jogai-border rounded-xl p-3">
                <div className="text-jogai-muted text-xs">{t('tracker_worst_game')}</div>
                <div className="text-jogai-red font-bold truncate">{stats.worst_game}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recent bets */}
      <div>
        <h2 className="text-lg font-bold text-jogai-text mb-2">{t('tracker_recent')}</h2>
        {bets.length === 0 ? (
          <p className="text-jogai-muted text-center py-8">{t('tracker_no_bets')}</p>
        ) : (
          <div className="space-y-2">
            {bets.map((bet) => (
              <div
                key={bet.id}
                className="bg-jogai-card border border-jogai-border rounded-xl p-3 flex items-center justify-between"
              >
                <div className="flex-1 min-w-0">
                  <div className="text-jogai-text font-medium truncate">
                    {bet.game_name || bet.game_type}
                  </div>
                  <div className="text-jogai-muted text-xs">
                    {t(`tracker_game_type_${bet.game_type}` as 'tracker_game_type_slots')}
                    {' · '}
                    {formatCurrency(bet.bet_amount, locale)}
                  </div>
                </div>
                <div className={`text-right ${bet.profit >= 0 ? 'text-jogai-green' : 'text-jogai-red'}`}>
                  <div className="font-bold">
                    {bet.profit >= 0 ? '+' : ''}{formatCurrency(bet.profit, locale)}
                  </div>
                  <div className="text-xs">
                    {bet.profit >= 0 ? t('tracker_won') : t('tracker_lost')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
