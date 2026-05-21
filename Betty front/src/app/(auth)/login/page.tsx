"use client";

import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { authApi } from "@/lib/api/auth";
import { useGoogleLogin } from "@react-oauth/google";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store/auth-store";
import { toast } from "sonner";
import { useState } from "react";
import axios from "axios";

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [isLoading, setIsLoading] = useState(false);
  const [pendingToken, setPendingToken] = useState<string | null>(null);
  const [username, setUsername] = useState("");

  const handleLoginSuccess = async (
    token: string,
    selectedUsername?: string,
  ) => {
    setIsLoading(true);
    try {
      const data = await authApi.login(token, selectedUsername);

      // Fetch user data after login using the new token
      const user = await authApi.getMe(data.access_token);
      setAuth(user, data.access_token);
      toast.success("Successfully logged in!");
      router.push("/");
    } catch (error: unknown) {
      if (
        axios.isAxiosError(error) &&
        error.response?.status === 404 &&
        error.config?.url?.includes("/login")
      ) {
        // Needs username
        setPendingToken(token);
        toast.info("Please choose a username to complete registration");
      } else if (
        axios.isAxiosError(error) &&
        error.response?.status === 400 &&
        error.config?.url?.includes("/login")
      ) {
        toast.error("Username already taken. Please choose another one.");
      } else {
        console.error("Login failed:", error);
        toast.error(
          axios.isAxiosError(error) && error.response?.status === 404
            ? "Backend endpoint /auth/me not found. Please implement it."
            : "Failed to login with Google"
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  const googleLogin = useGoogleLogin({
    onSuccess: (tokenResponse) =>
      handleLoginSuccess(tokenResponse.access_token),
    onError: () => toast.error("Google login was cancelled or failed"),
  });

  const onSubmitUsername = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !pendingToken) return;
    handleLoginSuccess(pendingToken, username.trim());
  };

  return (
    <div className="flex items-center justify-center px-4 py-12 min-h-screen">
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <Card className="glass border-border/50 shadow-2xl shadow-black/30">
          <CardHeader className="text-center pb-2">
            <div className="flex justify-center mb-4">
              <Link href="/" className="flex items-center gap-2">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/25">
                  <Zap className="h-6 w-6 text-white" />
                </div>
              </Link>
            </div>
            <CardTitle className="text-2xl font-bold">
              {pendingToken ? "Choose Username" : "Welcome Back"}
            </CardTitle>
            <CardDescription className="text-foreground-muted">
              {pendingToken
                ? "You're almost there! Pick a unique username."
                : "Sign in to track your progress and submit solutions"}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4 pb-8 px-8">
            <AnimatePresence mode="wait">
              {pendingToken ? (
                <motion.form
                  key="username-form"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  onSubmit={onSubmitUsername}
                  className="space-y-4"
                >
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-subtle" />
                    <Input
                      placeholder="Username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="pl-9 h-12"
                      required
                      minLength={3}
                      maxLength={20}
                      pattern="[a-zA-Z0-9_]+"
                      title="Letters, numbers and underscores only"
                      disabled={isLoading}
                    />
                  </div>
                  <Button
                    type="submit"
                    disabled={isLoading || !username.trim()}
                    size="lg"
                    className="w-full h-12 text-sm font-medium"
                    variant="gradient"
                  >
                    {isLoading
                      ? "Completing Registration..."
                      : "Complete Registration"}
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="w-full text-xs text-foreground-muted"
                    onClick={() => {
                      setPendingToken(null);
                      setUsername("");
                    }}
                    disabled={isLoading}
                  >
                    Cancel
                  </Button>
                </motion.form>
              ) : (
                <motion.div
                  key="login-btn"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                >
                  <Button
                    onClick={() => googleLogin()}
                    disabled={isLoading}
                    variant="outline"
                    size="lg"
                    className="w-full h-12 text-sm font-medium gap-3 border-border-hover hover:bg-card-elevated hover:border-primary/30 transition-all duration-200"
                  >
                    {isLoading ? (
                      <span className="h-5 w-5 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
                    ) : (
                      <svg className="h-5 w-5" viewBox="0 0 24 24">
                        <path
                          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
                          fill="#4285F4"
                        />
                        <path
                          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                          fill="#34A853"
                        />
                        <path
                          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                          fill="#FBBC05"
                        />
                        <path
                          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                          fill="#EA4335"
                        />
                      </svg>
                    )}
                    {isLoading ? "Signing in..." : "Continue with Google"}
                  </Button>

                  <p className="text-center text-xs text-foreground-subtle mt-6">
                    By signing in, you agree to our terms of service
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
