"use client";

import { use, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Calendar } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { useProfile, useUpdateUsername } from "@/lib/hooks/use-user";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/shared/error-state";

interface PageProps {
  params: Promise<{ username: string }>;
}

function ProfileSkeleton() {
  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-start gap-6">
        <Skeleton className="h-20 w-20 rounded-2xl" />
        <div className="space-y-2">
          <Skeleton className="h-8 w-40" />
          <Skeleton className="h-4 w-32" />
        </div>
      </div>
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-3">
            <Skeleton className="h-10 flex-1 rounded-lg" />
            <Skeleton className="h-10 w-20 rounded-lg" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function ProfilePage({ params }: PageProps) {
  const { username: paramUsername } = use(params);

  const { data: profile, isLoading, isError, error, refetch } = useProfile();
  const { mutate: updateUsername, isPending } = useUpdateUsername();

  const [newUsername, setNewUsername] = useState("");

  useEffect(() => {
    if (profile) {
      setNewUsername(profile.username);
    }
  }, [profile]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = newUsername.trim();
    if (!trimmed || trimmed === profile?.username) return;
    updateUsername(trimmed);
  };

  if (isLoading) {
    return <ProfileSkeleton />;
  }

  if (isError || !profile) {
    return (
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <ErrorState
          title="Failed to load profile"
          message={error instanceof Error ? error.message : "Could not fetch your profile data."}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const hasChanges = newUsername.trim() && newUsername.trim() !== profile.username;

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
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

        <Card>
          <CardHeader>
            <CardTitle>Change Username</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex items-end gap-3">
              <div className="flex-1 space-y-1.5">
                <Input
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="Enter new username"
                  disabled={isPending}
                />
              </div>
              <Button type="submit" disabled={isPending || !hasChanges}>
                {isPending ? "Saving..." : "Save"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
