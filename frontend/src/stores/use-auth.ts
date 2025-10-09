import { create } from 'zustand'

interface User {
  email: string;
}

interface AuthState {
  user: User | null;
  isLogout: boolean;
  setLogin: (user: User) => void;
  setLogout: () => void;
}

export const useAuthStore = create<AuthState>()(
  (set) => ({
      user: null,
      isLogout: false,
      setLogin: (user: User) => {
        set({user, isLogout: false})
      },
      setLogout: () => {
        set({user:null, isLogout: false})
      },
    }
  ),
)