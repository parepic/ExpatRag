import { renderHook } from "@testing-library/react";
import { useRouter } from "next/navigation";
import { useProfileGuard } from "@/hooks/useProfileGuard";
import * as profile from "@/lib/profile";

jest.mock("next/navigation", () => ({ useRouter: jest.fn() }));
jest.mock("@/lib/profile");

const mockPush = jest.fn();
beforeEach(() => {
  jest.mocked(useRouter).mockReturnValue({ push: mockPush } as any);
  mockPush.mockClear();
});

describe("useProfileGuard", () => {
  it("redirects to /chat when profile is complete on onboarding page", () => {
    jest.mocked(profile.isComplete).mockReturnValue(true);
    renderHook(() => useProfileGuard("onboarding"));
    expect(mockPush).toHaveBeenCalledWith("/chat");
  });

  it("redirects to /onboarding when profile is incomplete on chat page", () => {
    jest.mocked(profile.isComplete).mockReturnValue(false);
    renderHook(() => useProfileGuard("chat"));
    expect(mockPush).toHaveBeenCalledWith("/onboarding");
  });

  it("does not redirect on welcome page when profile is incomplete", () => {
    jest.mocked(profile.isComplete).mockReturnValue(false);
    renderHook(() => useProfileGuard("welcome"));
    expect(mockPush).not.toHaveBeenCalled();
  });
});
