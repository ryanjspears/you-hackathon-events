"use client";

import { ChatSidebar } from "@/components/ChatSidebar";
import { ThemeToggle } from "@/components/ThemeToggle";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { getUser, healthy, useUser } from "@/lib/api";
import { Sparkles } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export function Shell({ children }: { children: React.ReactNode }) {
  const user = useUser();
  const router = useRouter();
  const path = usePathname();
  const [ready, setReady] = useState<boolean | null>(null);

  useEffect(() => {
    // Read the cookie directly: during hydration `user` still holds the server snapshot (null),
    // which would bounce a logged-in user back to /login on every hard navigation.
    if (!getUser() && path !== "/login") router.replace("/login");
  }, [user, path, router]);

  // SPEC §4: poll /api/health on load; the API warms up One + memory for ~10–15 s.
  useEffect(() => {
    let alive = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const check = async () => {
      const ok = await healthy();
      if (!alive) return;
      setReady(ok);
      if (!ok) timer = setTimeout(check, 2000);
    };
    check();
    return () => {
      alive = false;
      if (timer) clearTimeout(timer);
    };
  }, []);

  const withSidebar = Boolean(user) && path !== "/login";

  return (
    <SidebarProvider>
      {withSidebar && <ChatSidebar />}
      <SidebarInset>
        <div className="mx-auto flex min-h-screen w-full max-w-4xl flex-col px-4 sm:px-6">
          <header className="flex items-center justify-between gap-4 py-5">
            <div className="flex items-center gap-2">
              {withSidebar ? (
                <SidebarTrigger className="-ml-2 text-foreground/65" />
              ) : (
                <Link href="/" className="flex items-center gap-2 text-base font-semibold">
                  <Sparkles className="size-4 text-foreground/70" />
                  Events Scanner
                </Link>
              )}
            </div>
            <nav className="flex items-center gap-4 text-sm">
              <ThemeToggle />
            </nav>
          </header>

          {ready === false && (
            <div role="status" className="lux-card mb-4 flex items-center gap-2 rounded-xl px-3 py-2 text-sm text-muted-foreground">
              <span className="relative flex size-2">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-brand opacity-75" />
                <span className="relative inline-flex size-2 rounded-full bg-brand" />
              </span>
              The agent is starting up. Searches will work in a few seconds.
            </div>
          )}

          <div className="flex-1 pb-16">{children}</div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
