import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

export type UserRole = "admin" | "user";

export interface User {
  id: number;
  email: string;
  role: UserRole;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE = "http://127.0.0.1:8000";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  // --------------------------------------------------
  // Load user on app startup if token exists
  // --------------------------------------------------
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetchCurrentUser(token);
    }
  }, []);

  const fetchCurrentUser = async (token: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        logout();
        return;
      }

      const data = await res.json();
      setUser(data);
    } catch {
      logout();
    }
  };

  // --------------------------------------------------
  // Login
  // --------------------------------------------------
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const res = await fetch(`${API_BASE}/api/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) return false;

      const data = await res.json();

      const token = data.access_token;

      localStorage.setItem("access_token", token);

      await fetchCurrentUser(token);

      return true;
    } catch {
      return false;
    }
  };

  // --------------------------------------------------
  // Logout
  // --------------------------------------------------
  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}









// import React, { createContext, useContext, useState, ReactNode } from 'react';
//
// export type UserRole = 'admin' | 'viewer';
//
// export interface User {
//   id: string;
//   username: string;
//   role: UserRole;
// }
//
// interface AuthContextType {
//   user: User | null;
//   login: (username: string, password: string) => boolean;
//   logout: () => void;
//   isAuthenticated: boolean;
// }
//
// const AuthContext = createContext<AuthContextType | undefined>(undefined);
//
// // Mock users for demo
// const MOCK_USERS = [
//   { id: '1', username: 'admin', password: 'admin123', role: 'admin' as UserRole },
//   { id: '2', username: 'viewer', password: 'viewer123', role: 'viewer' as UserRole },
// ];
//
// export function AuthProvider({ children }: { children: ReactNode }) {
//   const [user, setUser] = useState<User | null>(null);
//
//   const login = (username: string, password: string): boolean => {
//     const foundUser = MOCK_USERS.find(
//       (u) => u.username === username && u.password === password
//     );
//
//     if (foundUser) {
//       setUser({ id: foundUser.id, username: foundUser.username, role: foundUser.role });
//       return true;
//     }
//     return false;
//   };
//
//   const logout = () => {
//     setUser(null);
//   };
//
//   return (
//     <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
//       {children}
//     </AuthContext.Provider>
//   );
// }
//
// export function useAuth() {
//   const context = useContext(AuthContext);
//   if (context === undefined) {
//     throw new Error('useAuth must be used within an AuthProvider');
//   }
//   return context;
// }
