import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../api/client';
import type { AnalysisResult as AnalysisResultType } from '../types';
import AnalysisResultComponent from '../components/AnalysisResult';
import { getBackendLocale } from '../i18n';

export default function Analyze() {
  const { t, i18n } = useTranslation();
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResultType | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || loading) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const locale = getBackendLocale(i18n.language);
      const res = await api.post('/analyze', { text: text.trim(), locale });
      setResult(res.data);
    } catch {
      setError(t('error_generic'));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setText('');
    setError('');
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-jogai-text">
          {t('analyze_title')}
        </h2>
        <p className="text-jogai-muted text-sm mt-1">
          {t('analyze_description')}
        </p>
      </div>

      {!result ? (
        <form onSubmit={handleSubmit} className="space-y-3">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={t('analyze_placeholder')}
            className="w-full h-32 bg-jogai-card border border-jogai-border rounded-xl p-3 text-jogai-text placeholder-jogai-muted text-sm resize-none focus:outline-none focus:border-jogai-accent transition-colors"
          />
          <button
            type="submit"
            disabled={!text.trim() || loading}
            className="w-full bg-jogai-accent hover:bg-jogai-accent/80 disabled:bg-jogai-border disabled:text-jogai-muted text-white font-semibold py-3 rounded-xl transition-colors"
          >
            {loading ? t('analyze_analyzing') : t('analyze_submit')}
          </button>
          {error && (
            <div className="text-center text-jogai-red text-sm">{error}</div>
          )}
        </form>
      ) : (
        <div className="space-y-4">
          <AnalysisResultComponent result={result} />
          <button
            onClick={handleReset}
            className="w-full bg-jogai-card border border-jogai-border text-jogai-text font-semibold py-3 rounded-xl transition-colors hover:bg-jogai-border"
          >
            {t('btn_analyze')}
          </button>
        </div>
      )}
    </div>
  );
}
