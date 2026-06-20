"use client";

import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import {
  Zap,
  Code2,
  Trophy,
  Users,
  ArrowRight,
  Terminal,
  Globe,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
};

const staggerContainer = {
  animate: {
    transition: { staggerChildren: 0.1 },
  },
};

export default function LandingPage() {
  return (
    <div className="relative">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center overflow-hidden">
        {/* Background Effects */}

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20">
          <div className="flex flex-col items-center gap-8">
            <Image src="/betty-icon.png" alt="Betty Judge" width={400} height={400} className="rounded-full shadow-2xl shadow-primary/20" />
            <div className="flex flex-col lg:flex-row items-center gap-16 w-full">
              {/* Left Content */}
              <motion.div
                className="flex-1 text-center lg:text-left"
                initial="initial"
                animate="animate"
                variants={staggerContainer}
              >
                <motion.div
                  variants={fadeInUp}
                  transition={{ duration: 0.5 }}
                  className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5 text-xs font-medium text-foreground-muted mb-6"
                >
                  <Image src="/betty-icon.png" alt="Betty Judge" width={16} height={16} className="rounded-full" />
                  <span className="inline-block h-2 w-2 rounded-full bg-primary animate-pulse" />
                  Adventure Judge Platform
                </motion.div>

                <motion.h1
                  variants={fadeInUp}
                  transition={{ duration: 0.5, delay: 0.1 }}
                  className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.1] mb-6"
                >
                  Master{" "}
                  <span className="gradient-text">Competitive</span>
                  <br />
                  Programming
                </motion.h1>

                <motion.p
                  variants={fadeInUp}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="text-lg text-foreground-muted max-w-xl mx-auto lg:mx-0 mb-8 leading-relaxed"
                >
                  Solve algorithmic challenges, submit solutions in multiple languages,
                  and compete with programmers worldwide. Built for speed and precision.
                </motion.p>

                <motion.div
                  variants={fadeInUp}
                  transition={{ duration: 0.5, delay: 0.3 }}
                  className="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start"
                >
                  <Button asChild size="lg" variant="gradient">
                    <Link href="/problems">
                      Start Solving
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button asChild size="lg" variant="outline">
                    <Link href="/leaderboard">
                      <Trophy className="h-4 w-4" />
                      View Leaderboard
                    </Link>
                  </Button>
                </motion.div>
              </motion.div>

              {/* Right — Code Preview */}
              <motion.div
                className="flex-1 w-full max-w-lg"
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <div className="rounded-2xl border border-border bg-card overflow-hidden shadow-2xl shadow-black/20">
                {/* Terminal Header */}
                <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-card-elevated">
                  <div className="flex gap-1.5">
                    <div className="h-3 w-3 rounded-full bg-primary/70" />
                    <div className="h-3 w-3 rounded-full bg-warning/70" />
                    <div className="h-3 w-3 rounded-full bg-accent/70" />
                  </div>
                  <span className="ml-2 text-xs text-foreground-subtle font-mono">adventure.cpp</span>
                </div>
                {/* Code Content */}
                <div className="p-5 font-mono text-sm leading-7 text-foreground-muted">
                  <div>
                    <span className="text-primary/70">#include</span>{" "}
                    <span className="text-accent">&lt;bits/stdc++.h&gt;</span>
                  </div>
                  <div>
                    <span className="text-primary/70">using namespace</span>{" "}
                    <span className="text-foreground">std;</span>
                  </div>
                  <div className="mt-3">
                    <span className="text-primary/70">int</span>{" "}
                    <span className="text-accent">main</span>
                    <span className="text-foreground">() {"{"}</span>
                  </div>
                  <div className="pl-6">
                    <span className="text-foreground-subtle">{"// Fast I/O"}</span>
                  </div>
                  <div className="pl-6">
                    <span className="text-foreground">ios_base::</span>
                    <span className="text-accent">sync_with_stdio</span>
                    <span className="text-foreground">(</span>
                    <span className="text-primary">false</span>
                    <span className="text-foreground">);</span>
                  </div>
                  <div className="pl-6">
                    <span className="text-foreground">cin.</span>
                    <span className="text-accent">tie</span>
                    <span className="text-foreground">(NULL);</span>
                  </div>
                  <div className="mt-3 pl-6">
                    <span className="text-primary/70">int</span>{" "}
                    <span className="text-foreground">n;</span>
                  </div>
                  <div className="pl-6">
                    <span className="text-foreground">cin &gt;&gt; n;</span>
                  </div>
                  <div className="pl-6 mt-1">
                    <span className="text-foreground-subtle">{"// Solve..."}</span>
                  </div>
                  <div className="mt-3">
                    <span className="text-foreground">{"}"}</span>
                  </div>
                </div>
                {/* Bottom bar */}
                <div className="flex items-center justify-between px-4 py-2.5 border-t border-border bg-card-elevated">
                  <div className="flex items-center gap-2 text-xs text-foreground-subtle">
                    <Terminal className="h-3.5 w-3.5" />
                    <span>C++ 17</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs">
                    <span className="inline-block h-2 w-2 rounded-full bg-success" />
                    <span className="text-success font-medium">Accepted</span>
                    <span className="text-foreground-subtle ml-2">42ms</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="text-3xl font-bold tracking-tight mb-4">
              Why <span className="gradient-text">Betty Judge</span>?
            </h2>
            <p className="text-foreground-muted max-w-2xl mx-auto">
              A competitive programming platform built by programmers, for programmers.
              Every feature is designed for speed and precision.
            </p>
          </motion.div>

          <motion.div
            className="grid md:grid-cols-3 gap-6"
            initial="initial"
            whileInView="animate"
            viewport={{ once: true, margin: "-50px" }}
            variants={staggerContainer}
          >
            {[
              {
                icon: Zap,
                title: "Lightning Fast Judge",
                description:
                  "Solutions are compiled, executed, and graded in milliseconds with accurate time and memory measurements.",
                color: "text-primary",
                bg: "bg-primary-muted",
              },
              {
                icon: Code2,
                title: "Multi-Language Support",
                description:
                  "Write your solutions in C++, Python, or Java with a professional Monaco code editor and syntax highlighting.",
                color: "text-accent",
                bg: "bg-accent-muted",
              },
              {
                icon: Trophy,
                title: "Compete & Climb",
                description:
                  "Track your progress, compare yourself on the leaderboard, and build your competitive programming profile.",
                color: "text-warning",
                bg: "bg-warning-muted",
              },
            ].map((feature) => (
              <motion.div key={feature.title} variants={fadeInUp} transition={{ duration: 0.4 }}>
                <Card className="h-full hover:border-border-hover hover:bg-card-hover transition-all duration-300 group">
                  <CardContent className="p-6">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${feature.bg} mb-4 group-hover:scale-110 transition-transform duration-300`}>
                      <feature.icon className={`h-6 w-6 ${feature.color}`} />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                    <p className="text-sm text-foreground-muted leading-relaxed">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent" />
        <motion.div
          className="relative mx-auto max-w-3xl px-4 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl font-bold tracking-tight mb-4">
            Ready to Start Solving?
          </h2>
          <p className="text-foreground-muted mb-8 max-w-lg mx-auto">
            Join thousands of competitive programmers. Sign in with Google to
            save your progress and compete on the leaderboard.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button asChild size="lg" variant="gradient">
              <Link href="/login">
                Get Started
                <ChevronRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/problems">
                Browse Problems
              </Link>
            </Button>
          </div>
        </motion.div>
      </section>
    </div>
  );
}