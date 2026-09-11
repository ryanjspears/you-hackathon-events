"use client";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { clearUser, useUser } from "@/lib/api";
import { deleteConversation, groupByAge, selectConversation, startNewConversation, summarize, useActiveId, useConversations } from "@/lib/history";
import { CalendarCheck, LogOut, Plus, Sparkles, Trash2 } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

/** Left rail: past searches for the logged-in user, newest first, grouped by day. */
export function ChatSidebar() {
  const user = useUser();
  const router = useRouter();
  const path = usePathname();
  const list = useConversations(user);
  const activeId = useActiveId();
  const { isMobile, setOpenMobile } = useSidebar();
  const groups = groupByAge(list);

  function open(id: string | null) {
    if (id) selectConversation(id);
    else startNewConversation();
    if (path !== "/") router.push("/");
    if (isMobile) setOpenMobile(false);
  }

  return (
    <Sidebar>
      <SidebarHeader className="gap-3 px-3 pt-4">
        <Link href="/" className="flex items-center gap-2 px-1 text-base font-semibold" onClick={() => open(null)}>
          <Sparkles className="size-4 text-foreground/70" />
          Events Scanner
        </Link>
        <Button variant="secondary" size="sm" className="justify-start" onClick={() => open(null)}>
          <Plus className="size-3.5" /> New search
        </Button>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              render={<Link href="/going" />}
              isActive={path === "/going"}
              className="rounded-xl"
              onClick={() => {
                if (isMobile) setOpenMobile(false);
              }}
            >
              <CalendarCheck className="text-foreground/65" />
              <span>Going</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        {groups.length === 0 && (
          <div className="lux-card mx-3 mt-2 rounded-2xl p-3 text-xs leading-relaxed text-muted-foreground">
            <Sparkles className="mb-1.5 size-3.5 text-brand-text" />
            Your searches show up here. Each one is also remembered by the agent, so the next list is already yours.
          </div>
        )}
        {groups.map((g) => (
          <SidebarGroup key={g.label}>
            <SidebarGroupLabel>{g.label}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {g.items.map((c) => {
                  const sub = summarize(c);
                  const running = sub === "Searching…";
                  return (
                    <SidebarMenuItem key={c.id}>
                      <SidebarMenuButton
                        size="lg"
                        isActive={c.id === activeId}
                        onClick={() => open(c.id)}
                        title={c.title}
                        className="h-auto flex-col items-start gap-0.5 rounded-xl py-2 pr-8"
                      >
                        <span className="w-full truncate text-sm leading-tight">{c.title}</span>
                        {sub && (
                          <span className={`w-full truncate text-xs ${running ? "text-brand-text" : "text-muted-foreground"}`}>
                            {running && <span className="mr-1 inline-block size-1.5 animate-pulse rounded-full bg-brand align-middle" />}
                            {sub}
                          </span>
                        )}
                      </SidebarMenuButton>
                      <SidebarMenuAction
                        showOnHover
                        aria-label={`Delete "${c.title}"`}
                        className="top-2.5"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (user) deleteConversation(user, c.id);
                        }}
                      >
                        <Trash2 />
                      </SidebarMenuAction>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              onClick={() => {
                clearUser();
                selectConversation(null);
                router.push("/login");
              }}
            >
              <span className="flex size-6 items-center justify-center rounded-full bg-brand text-xs font-semibold uppercase text-brand-foreground">
                {user?.[0] ?? "?"}
              </span>
              <span className="truncate">{user}</span>
              <LogOut className="ml-auto size-3.5 text-muted-foreground" />
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
