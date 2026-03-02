import { useEffect, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Layout from './components/Layout';
import Home from './pages/Home';
import Analyze from './pages/Analyze';
import api from './api/client';
import { useUserStore } from './stores/user';
import type { AuthResponse } from './types';

function AppContent() {
  useTranslation();
  const { setUser, setToken } = useUserStore();

  useEffect(() => {
    const webapp = window.Telegram?.WebApp;
    if (webapp) {
      webapp.ready?.();
      webapp.expand?.();
      webapp.setHeaderColor?.('#0f0f1a');
      webapp.setBackgroundColor?.('#0f0f1a');
    }

    const authenticate = async () => {
      const initData = webapp?.initData;
      if (!initData) return;

      try {
        const res = await api.post<AuthResponse>('/auth/telegram', {
          init_data: initData,
        });
        setToken(res.data.access_token);
        setUser(res.data.user);
      } catch {
        // Auth failed — continue as anonymous
      }
    };
    authenticate();
  }, [setUser, setToken]);

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analyze" element={<Analyze />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-jogai-bg flex items-center justify-center text-jogai-muted">
          ...
        </div>
      }
    >
      <AppContent />
    </Suspense>
  );
}
