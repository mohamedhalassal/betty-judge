import {
  Code2,
  Trophy,
  History,
  User,
  LayoutDashboard,
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

export const userNav: NavItem[] = [
  {
    title: "Profile",
    href: "/profile",
    icon: User,
    requiresAuth: true,
  },
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    requiresAuth: true,
  },
];
