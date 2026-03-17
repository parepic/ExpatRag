"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAppContext } from "@/context/AppContext";
import { Checkbox } from "@/components/ui/checkbox";

interface AppLayoutProps {
  children: React.ReactNode;
}

function isSettingsRoute(pathname: string) {
  return pathname.startsWith("/settings");
}

export default function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();
  const inSettings = isSettingsRoute(pathname);
  const { todos, toggleTodo, chats, activeChat, setActiveChat, addChat } = useAppContext();

  return (
    <div className="flex h-screen overflow-hidden bg-[--color-bg]">
      {/* Sidebar */}
      <aside
        className="flex flex-col border-r border-[--color-border] bg-[--color-bg-subtle]"
        style={{ width: "var(--sidebar-width)", minWidth: "var(--sidebar-width)" }}
      >
        {/* Logo */}
        <div className="px-4 py-4 border-b border-[--color-border]">
          <span className="font-bold text-lg tracking-tight text-[--color-text]">Patty</span>
        </div>

        {/* Nav */}
        <nav className="px-3 py-3 border-b border-[--color-border]">
          {inSettings ? (
            <Link
              href="/chat"
              className="flex items-center gap-2 px-2 py-1.5 text-sm text-[--color-text-muted] hover:text-[--color-text] rounded transition-colors"
            >
              ← Back to Patty
            </Link>
          ) : (
            <Link
              href="/settings/profile"
              className="flex items-center gap-2 px-2 py-1.5 text-sm text-[--color-text-muted] hover:text-[--color-text] rounded transition-colors"
            >
              ⚙ Settings
            </Link>
          )}
          {inSettings && (
            <div className="mt-2">
              <Link
                href="/settings/profile"
                className={`block px-2 py-1.5 text-sm rounded transition-colors ${
                  pathname === "/settings/profile"
                    ? "bg-[--color-accent] text-white"
                    : "text-[--color-text-muted] hover:text-[--color-text]"
                }`}
              >
                Profile
              </Link>
            </div>
          )}
        </nav>

        {/* Todos */}
        {!inSettings && (
          <div className="flex-1 overflow-y-auto px-3 py-3 border-b border-[--color-border]">
            <p className="text-xs font-semibold uppercase tracking-wider text-[--color-text-muted] mb-2 px-2">Tasks</p>
            {todos.length === 0 ? (
              <p className="text-xs text-[--color-text-muted] px-2">No tasks yet — Patty will suggest things as you chat.</p>
            ) : (
              <ul className="space-y-1">
                {todos.map((todo) => (
                  <li key={todo.id} className="flex items-start gap-2 px-2 py-1">
                    <Checkbox
                      checked={todo.completed}
                      onCheckedChange={() => toggleTodo(todo.id)}
                      className="mt-0.5"
                    />
                    <span className={`text-sm ${todo.completed ? "line-through text-[--color-text-muted]" : "text-[--color-text]"}`}>
                      {todo.text}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Previous chats */}
        {!inSettings && (
          <div className="px-3 py-3">
            <div className="flex items-center justify-between mb-2 px-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-[--color-text-muted]">Chats</p>
              <button
                onClick={() => addChat("New chat")}
                className="text-xs text-[--color-accent] hover:underline"
              >
                + New
              </button>
            </div>
            <p className="text-xs text-[--color-text-muted] px-2 mb-2 italic">Session only</p>
            {chats.length === 0 ? (
              <p className="text-xs text-[--color-text-muted] px-2">No previous chats this session.</p>
            ) : (
              <ul className="space-y-0.5">
                {chats.map((chat) => (
                  <li key={chat.id}>
                    <button
                      onClick={() => setActiveChat(chat.id)}
                      className={`w-full text-left px-2 py-1.5 text-sm rounded transition-colors truncate ${
                        activeChat === chat.id
                          ? "bg-[--color-accent] text-white"
                          : "text-[--color-text-muted] hover:text-[--color-text]"
                      }`}
                    >
                      {chat.title}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  );
}
