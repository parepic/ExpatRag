"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowLeft, ChevronRight, Settings } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ChatProvider, useChatContext } from "@/context/ChatContext";

type AppLayoutProps = {
  children: React.ReactNode;
};

type Breadcrumb = {
  label: string;
  muted: boolean;
};

function truncateTitle(title: string, maxLength: number) {
  if (title.length <= maxLength) {
    return title;
  }

  return `${title.slice(0, maxLength - 3)}...`;
}

function isSettingsRoute(pathname: string) {
  return pathname.startsWith("/settings");
}

function getBreadcrumbs(pathname: string): Breadcrumb[] {
  if (pathname === "/chat") {
    return [{ label: "Chat with Patty", muted: false }];
  }

  if (pathname.startsWith("/settings/")) {
    const pageName = pathname
      .split("/settings/")[1]
      .split("/")
      .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
      .join(" ");

    return [
      { label: "Settings", muted: true },
      { label: pageName, muted: false },
    ];
  }

  return [{ label: "Settings", muted: false }];
}

function AppShell({ children }: AppLayoutProps) {
  const pathname = usePathname();
  const inSettings = isSettingsRoute(pathname);
  const breadcrumbs = getBreadcrumbs(pathname);
  const { activeChatId, chats, setActiveChatId } = useChatContext();

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      <aside
        className="flex shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground"
        style={{ width: "var(--sidebar-width)", minWidth: "var(--sidebar-width)" }}
      >
        <div className="border-b border-sidebar-border px-4 py-4">
          <Link href="/chat" className="text-lg font-bold tracking-tight">
            Patty
          </Link>
        </div>

        <nav className="border-b border-sidebar-border px-3 py-3">
          {inSettings ? (
            <>
              <Link
                href="/chat"
                className="flex items-center gap-2 rounded px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              >
                <ArrowLeft className="size-4" />
                Back to Patty
              </Link>
              <div className="mt-2">
                <Link
                  href="/settings/profile"
                  className={`block rounded px-2 py-1.5 text-sm transition-colors ${
                    pathname === "/settings/profile"
                      ? "bg-sidebar-primary text-sidebar-primary-foreground"
                      : "text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  }`}
                >
                  Profile
                </Link>
              </div>
            </>
          ) : (
            <Link
              href="/settings/profile"
              className="flex items-center gap-2 rounded px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            >
              <Settings className="size-4" />
              Settings
            </Link>
          )}
        </nav>

        {!inSettings ? (
          <div className="flex flex-1 flex-col overflow-y-auto px-3 py-3">
            <div className="mb-2 flex items-center justify-between px-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Chats
              </p>
              <Button
                type="button"
                variant="ghost"
                className="h-auto px-0 py-0 text-xs text-primary shadow-none hover:bg-transparent hover:text-primary/80"
                onClick={() => setActiveChatId(null)}
              >
                + New
              </Button>
            </div>

            {chats.length === 0 ? (
              <p className="px-2 text-xs text-muted-foreground">
                No chats yet.
              </p>
            ) : (
              <ul className="space-y-0.5">
                {chats.map((chat) => (
                  <li key={chat.id}>
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => setActiveChatId(chat.id)}
                    className={`w-full justify-start truncate px-2 py-1.5 text-sm shadow-none transition-colors ${
                      activeChatId === chat.id
                        ? "bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary hover:text-sidebar-primary-foreground"
                        : "text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                    }`}
                  >
                      {truncateTitle(chat.title, 30)}
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ) : (
          <div className="flex-1" />
        )}
      </aside>

      <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <header className="flex shrink-0 items-center gap-2 border-b border-border px-6 py-3 text-sm">
          {breadcrumbs.map((crumb, index) => (
            <span key={crumb.label} className="flex items-center gap-2">
              {index > 0 ? (
                <ChevronRight className="size-3.5 text-muted-foreground" />
              ) : null}
              <span
                className={
                  crumb.muted ? "text-muted-foreground" : "font-medium text-foreground"
                }
              >
                {crumb.label}
              </span>
            </span>
          ))}
        </header>

        <div className="min-h-0 flex-1 overflow-y-auto">{children}</div>
      </main>
    </div>
  );
}

export default function AppLayout({ children }: AppLayoutProps) {
  return (
    <ChatProvider>
      <AppShell>{children}</AppShell>
    </ChatProvider>
  );
}
