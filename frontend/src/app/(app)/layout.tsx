"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Settings, ArrowLeft, ChevronRight } from "lucide-react";
import { useAppContext } from "@/context/AppContext";
import { createChat } from "@/lib/chat-store";
import { useChatSessions } from "@/hooks/useChatSessions";
import { Button } from "@/components/ui/button";

interface AppLayoutProps {
  children: React.ReactNode;
}

export function isSettingsRoute(pathname: string) {
  return pathname.startsWith("/settings");
}

export function getBreadcrumb(pathname: string) {
  if (pathname === "/chat") {
    return [{ label: "Chat with Patty", muted: false }];
  }
  if (pathname.startsWith("/settings/")) {
    const segment = pathname.split("/settings/")[1];
    const pageName = segment.charAt(0).toUpperCase() + segment.slice(1);
    return [
      { label: "Settings", muted: true },
      { label: pageName, muted: false },
    ];
  }
  return [{ label: "Settings", muted: false }];
}

export default function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();
  const inSettings = isSettingsRoute(pathname);
  const { activeChatId, setActiveChatId } = useAppContext();
  const chats = useChatSessions();
  const breadcrumbs = getBreadcrumb(pathname);

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      {/* Sidebar */}
      <aside
        className="flex flex-col border-r border-border bg-sidebar text-sidebar-foreground"
        style={{ width: "var(--sidebar-width)", minWidth: "var(--sidebar-width)" }}
      >
        {/* Logo */}
        <div className="border-b border-sidebar-border px-4 py-4">
          <span className="text-lg font-bold tracking-tight">Patty</span>
        </div>

        {/* Nav */}
        <nav className="border-b border-sidebar-border px-3 py-3">
          {inSettings ? (
            <Link
              href="/chat"
              className="flex items-center gap-2 rounded px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            >
              <ArrowLeft className="size-4" /> Back to Patty
            </Link>
          ) : (
            <Link
              href="/settings/profile"
              className="flex items-center gap-2 rounded px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            >
              <Settings className="size-4" /> Settings
            </Link>
          )}
          {inSettings && (
            <div className="mt-2">
              <Link
                href="/settings/profile"
                className={`block px-2 py-1.5 text-sm rounded transition-colors ${
                  pathname === "/settings/profile"
                    ? "bg-sidebar-primary text-sidebar-primary-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                }`}
              >
                Profile
              </Link>
            </div>
          )}
        </nav>

        {/* Previous chats — flex-1 so it expands to fill remaining sidebar space */}
        {!inSettings && (
          <div className="flex-1 overflow-y-auto px-3 py-3">
            <div className="flex items-center justify-between mb-2 px-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Chats</p>
              <Button
                type="button"
                variant="ghost"
                onClick={() => {
                  const chat = createChat();
                  setActiveChatId(chat.id);
                }}
                className="h-auto px-0 py-0 text-xs text-primary shadow-none hover:bg-transparent hover:text-primary/80"
              >
                + New
              </Button>
            </div>
            <p className="mb-2 px-2 text-xs italic text-muted-foreground">Session only</p>
            {chats.length === 0 ? (
              <p className="px-2 text-xs text-muted-foreground">No previous chats this session.</p>
            ) : (
              <ul className="space-y-0.5">
                {chats.map((chat) => (
                  <li key={chat.id}>
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => setActiveChatId(chat.id)}
                      className={`w-full justify-start truncate px-2 py-1.5 text-sm transition-colors shadow-none ${
                        activeChatId === chat.id
                          ? "bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary hover:text-sidebar-primary-foreground"
                          : "text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                      }`}
                    >
                      {chat.title}
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header breadcrumb */}
        <header className="shrink-0 border-b border-border px-6 py-3 flex items-center gap-2 text-sm">
          {breadcrumbs.map((crumb, i) => (
            <span key={i} className="flex items-center gap-2">
              {i > 0 && <ChevronRight className="size-3.5 text-muted-foreground" />}
              <span className={crumb.muted ? "text-muted-foreground" : "text-foreground font-medium"}>
                {crumb.label}
              </span>
            </span>
          ))}
        </header>
        {/* Content — scrollable, fills remaining height so chat page h-full works */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
