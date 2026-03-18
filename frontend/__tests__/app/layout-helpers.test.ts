jest.mock("next/link", () => ({
  __esModule: true,
  default: ({ children }: { children: unknown }) => children,
}));
jest.mock("next/navigation", () => ({ usePathname: jest.fn() }));
jest.mock("@/context/AppContext", () => ({ useAppContext: jest.fn() }));
jest.mock("lucide-react", () => ({
  Settings: () => null,
  ArrowLeft: () => null,
  ChevronRight: () => null,
}));
jest.mock("@/components/ui/checkbox", () => ({ Checkbox: () => null }));
jest.mock("@/components/ui/button", () => ({ Button: () => null }));

import { getBreadcrumb, isSettingsRoute } from "@/app/(app)/layout";

describe("getBreadcrumb", () => {
  it('"/chat" → single Chat with Patty crumb', () => {
    expect(getBreadcrumb("/chat")).toEqual([{ label: "Chat with Patty", muted: false }]);
  });

  it('"/settings/profile" → [Settings (muted), Profile]', () => {
    expect(getBreadcrumb("/settings/profile")).toEqual([
      { label: "Settings", muted: true },
      { label: "Profile", muted: false },
    ]);
  });

  it('"/settings/notifications" → [Settings (muted), Notifications]', () => {
    expect(getBreadcrumb("/settings/notifications")).toEqual([
      { label: "Settings", muted: true },
      { label: "Notifications", muted: false },
    ]);
  });

  it('"/settings" (no sub-page) → [Settings]', () => {
    expect(getBreadcrumb("/settings")).toEqual([{ label: "Settings", muted: false }]);
  });
});

describe("isSettingsRoute", () => {
  it('"/settings" → true', () => {
    expect(isSettingsRoute("/settings")).toBe(true);
  });

  it('"/settings/profile" → true', () => {
    expect(isSettingsRoute("/settings/profile")).toBe(true);
  });

  it('"/chat" → false', () => {
    expect(isSettingsRoute("/chat")).toBe(false);
  });
});
