import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

export type UserRole = "primary" | "user";

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
  console.log("AuthProvider mounted");

const [user, setUser] = useState<User | null>(() => {
  const token = localStorage.getItem("access_token");
  return token
    ? { id: 0, email: "colby.wirth@maine.edu", role: "user" }
    : null;
});


  // ------------------------
  // Login
  // ------------------------
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (!res.ok) return false;

      const data = await res.json();
      const token = data.access_token;

      localStorage.setItem("access_token", token);

      // TEMP user (since no /me endpoint)
      setUser({
        id: 0,
        email,
        role: "user",
      });

      return true;
    } catch {
      return false;
    }
  };

  // ------------------------
  // Logout
  // ------------------------
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
