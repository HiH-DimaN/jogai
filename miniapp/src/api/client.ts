import axios from 'axios';
import { getBackendLocale } from '../i18n';
import i18n from '../i18n';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const initData = window.Telegram?.WebApp?.initData;
  if (initData) {
    config.headers['X-Telegram-Init-Data'] = initData;
  }

  const token = localStorage.getItem('jogai_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  const locale = getBackendLocale(i18n.language);
  config.params = { ...config.params, locale };

  return config;
});

export default api;
