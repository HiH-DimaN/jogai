import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { getBackendLocale } from '../i18n';
import api from '../api/client';
import { useUserStore } from '../stores/user';
import CasinoResultCard from '../components/CasinoResultCard';
import type { QuizQuestion, QuizResult } from '../types';

const ANSWER_KEYS = ['game_type', 'deposit_range', 'payment', 'priority', 'experience'] as const;

export default function Quiz() {
  const { t, i18n } = useTranslation();
  const { user } = useUserStore();

  const [step, setStep] = useState(0); // 0 = intro, 1-5 = questions, 6 = results
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [results, setResults] = useState<QuizResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const startQuiz = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.post<{ questions: QuizQuestion[] }>('/quiz/start');
      setQuestions(res.data.questions);
      setStep(1);
    } catch {
      setError(t('error_generic'));
    } finally {
      setLoading(false);
    }
  };

  const selectOption = (value: string) => {
    const key = ANSWER_KEYS[step - 1];
    const newAnswers = { ...answers, [key]: value };
    setAnswers(newAnswers);

    if (step < 5) {
      setStep(step + 1);
    } else {
      submitQuiz(newAnswers);
    }
  };

  const submitQuiz = async (finalAnswers: Record<string, string>) => {
    setLoading(true);
    setError('');
    try {
      const locale = getBackendLocale(i18n.language);
      const geo = user?.geo || 'BR';
      const res = await api.post<QuizResult[]>('/quiz/result', {
        ...finalAnswers,
        geo,
        locale,
      });
      setResults(res.data);
      setStep(6);
    } catch {
      setError(t('error_generic'));
    } finally {
      setLoading(false);
    }
  };

  const resetQuiz = () => {
    setStep(0);
    setAnswers({});
    setResults([]);
    setError('');
  };

  // Intro screen
  if (step === 0) {
    return (
      <div className="space-y-6 text-center pt-8">
        <h1 className="text-2xl font-bold text-jogai-text">{t('quiz_title')}</h1>
        <p className="text-jogai-muted">{t('quiz_subtitle')}</p>
        <button
          onClick={startQuiz}
          disabled={loading}
          className="bg-jogai-accent hover:bg-jogai-accent/80 text-white font-semibold py-3 px-8 rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? t('loading') : t('quiz_submit')}
        </button>
        {error && <p className="text-jogai-red text-sm">{error}</p>}
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center pt-20">
        <p className="text-jogai-muted">{t('quiz_loading')}</p>
      </div>
    );
  }

  // Results
  if (step === 6) {
    return (
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-jogai-text">{t('quiz_result_title')}</h2>
        {results.length === 0 ? (
          <p className="text-jogai-muted">{t('error_generic')}</p>
        ) : (
          results.map((casino, idx) => (
            <CasinoResultCard key={casino.slug} casino={casino} rank={idx + 1} />
          ))
        )}
        <button
          onClick={resetQuiz}
          className="w-full border border-jogai-border text-jogai-muted hover:text-jogai-text py-2.5 rounded-lg transition-colors"
        >
          {t('quiz_retry')}
        </button>
      </div>
    );
  }

  // Question step (1-5)
  const question = questions[step - 1];
  if (!question) return null;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-jogai-muted text-sm">{t('quiz_step', { current: step, total: 5 })}</p>
        <div className="w-full bg-jogai-border rounded-full h-1.5 mt-2">
          <div
            className="bg-jogai-accent h-1.5 rounded-full transition-all"
            style={{ width: `${(step / 5) * 100}%` }}
          />
        </div>
      </div>

      <h2 className="text-lg font-bold text-jogai-text">{question.question}</h2>

      <div className="space-y-3">
        {question.options.map((opt) => (
          <button
            key={opt.value}
            onClick={() => selectOption(opt.value)}
            className="w-full text-left bg-jogai-card border border-jogai-border hover:border-jogai-accent rounded-xl p-4 text-jogai-text transition-colors"
          >
            {opt.label}
          </button>
        ))}
      </div>

      {error && <p className="text-jogai-red text-sm">{error}</p>}
    </div>
  );
}
