import {
  Code2,
  Trophy,
  History,
  User,
  Plus,
} from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  requiresAuth?: boolean;
}

export const mainNav: NavItem[] = [
  {
    title: "Problems",
    href: "/problems",
    icon: Code2,
  },
  {
    title: "Submissions",
    href: "/submissions",
    icon: History,
    requiresAuth: true,
  },
  {
    title: "Leaderboard",
    href: "/leaderboard",
    icon: Trophy,
  },
];

export const mainNavAuth: NavItem[] = [
  {
    title: "New Problem",
    href: "/problems/create",
    icon: Plus,
    requiresAuth: true,
  },
];

export const userNav: NavItem[] = [
  {
    title: "Profile",
    href: "/profile",
    icon: User,
    requiresAuth: true,
  },
  {
    title: "New Problem",
    href: "/problems/create",
    icon: Plus,
    requiresAuth: true,
  },
];
