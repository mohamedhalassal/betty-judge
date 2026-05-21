"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Code2,
  Menu,
  X,
  LogIn,
  LogOut,
  User,
  ChevronDown,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { mainNav } from "@/config/nav";
import { useAuthStore } from "@/lib/store/auth-store";
import { cn } from "@/lib/utils";

export function Navbar() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  React.useEffect(() => {
    // eslint-disable-next-line
    setMounted(true);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full glass-strong">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2.5 transition-opacity hover:opacity-80"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/20">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight">
            Betty<span className="text-primary">Judge</span>
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-1">
          {mainNav.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "relative px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200",
                  isActive
                    ? "text-foreground"
                    : "text-foreground-muted hover:text-foreground hover:bg-card-elevated"
                )}
              >
                {item.title}
                {isActive && (
                  <motion.div
                    layoutId="navbar-indicator"
                    className="absolute inset-0 rounded-lg bg-card-elevated border border-border-subtle"
                    style={{ zIndex: -1 }}
                    transition={{ type: "spring", duration: 0.4, bounce: 0.15 }}
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right Side */}
        <div className="hidden md:flex items-center gap-3">
          {mounted && isAuthenticated && user ? (
            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-foreground-muted hover:text-foreground hover:bg-card-elevated transition-colors"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/20 text-primary text-xs font-bold">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <span>{user.username}</span>
                <ChevronDown className="h-4 w-4" />
              </button>

              <AnimatePresence>
                {profileOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 8, scale: 0.96 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 8, scale: 0.96 }}
                    transition={{ duration: 0.15 }}
                    className="absolute right-0 mt-2 w-48 rounded-xl border border-border bg-card p-1.5 shadow-xl shadow-black/20"
                  >
                    <Link
                      href={`/profile/${user.username}`}
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-foreground-muted hover:text-foreground hover:bg-card-elevated transition-colors"
                    >
                      <User className="h-4 w-4" />
                      Profile
                    </Link>
                    <div className="my-1 h-px bg-border" />
                    <button
                      onClick={() => {
                        logout();
                        setProfileOpen(false);
                      }}
                      className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-destructive hover:bg-destructive-muted transition-colors"
                    >
                      <LogOut className="h-4 w-4" />
                      Logout
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ) : (
            <Button asChild size="sm" variant="gradient">
              <Link href="/login">
                <LogIn className="h-4 w-4" />
                Sign In
              </Link>
            </Button>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden flex items-center justify-center h-10 w-10 rounded-lg hover:bg-card-elevated transition-colors"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? (
            <X className="h-5 w-5" />
          ) : (
            <Menu className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Mobile Nav */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden border-t border-border overflow-hidden"
          >
            <div className="px-4 py-4 space-y-1">
              {mainNav.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-card-elevated text-foreground"
                        : "text-foreground-muted hover:text-foreground hover:bg-card-elevated"
                    )}
                  >
                    {item.icon && <item.icon className="h-4 w-4" />}
                    {item.title}
                  </Link>
                );
              })}
              <div className="pt-2 border-t border-border mt-2">
                {mounted && isAuthenticated && user ? (
                  <>
                    <Link
                      href={`/profile/${user.username}`}
                      onClick={() => setMobileOpen(false)}
                      className="flex items-center gap-3 rounded-lg px-4 py-3 text-sm text-foreground-muted hover:text-foreground hover:bg-card-elevated transition-colors"
                    >
                      <User className="h-4 w-4" />
                      Profile
                    </Link>
                    <button
                      onClick={() => {
                        logout();
                        setMobileOpen(false);
                      }}
                      className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm text-destructive hover:bg-destructive-muted transition-colors"
                    >
                      <LogOut className="h-4 w-4" />
                      Logout
                    </button>
                  </>
                ) : (
                  <Link
                    href="/login"
                    onClick={() => setMobileOpen(false)}
                    className="flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium text-primary hover:bg-primary-muted transition-colors"
                  >
                    <LogIn className="h-4 w-4" />
                    Sign In
                  </Link>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
