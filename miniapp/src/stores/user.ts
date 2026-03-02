import { create } from 'zustand';
import type { UserData } from '../types';

interface UserState {
  user: UserData | null;
  token: string | null;
  isAuthenticated: boolean;
  setUser: (user: UserData) => void;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  token: localStorage.getItem('jogai_token'),
  isAuthenticated: !!localStorage.getItem('jogai_token'),

  setUser: (user) => set({ user, isAuthenticated: true }),

  setToken: (token) => {
    localStorage.setItem('jogai_token', token);
    set({ token, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('jogai_token');
    set({ user: null, token: null, isAuthenticated: false });
  },
}));
