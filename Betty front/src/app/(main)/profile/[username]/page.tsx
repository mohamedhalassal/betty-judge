"use client";

import { use } from "react";
import { motion } from "framer-motion";
import { Calendar } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { useProfile } from "@/lib/hooks/use-user";
import { TableSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";

interface PageProps {
  params: Promise<{ username: string }>;
}

export default function ProfilePage({ params }: PageProps) {
  const { username } = use(params);

  const { data: profile, isLoading, isError, refetch } = useProfile(username);

  if (isLoading) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <TableSkeleton />
      </div>
    );
  }

  if (isError || !profile) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <ErrorState title="Failed to load profile" onRetry={() => refetch()} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-start gap-6">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent text-white text-2xl font-bold shadow-lg shadow-primary/20">
            {profile.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="text-2xl font-bold">{profile.username}</h1>
            <div className="flex items-center gap-2 mt-1 text-sm text-foreground-muted">
              <Calendar className="h-4 w-4" />
              Joined {formatDate(profile.created_at)}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
