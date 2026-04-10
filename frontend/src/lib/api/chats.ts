import { ApiError } from "@/lib/api/auth";
import type { Chat, ChatReply, ChatThread } from "@/lib/types/chat";

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL;

async function parseApiError(
  response: Response,
  fallbackMessage: string,
): Promise<never> {
  const body = await response.json().catch(() => null);
  throw new ApiError(response.status, body?.detail ?? fallbackMessage);
}

export async function fetchChats(): Promise<Chat[]> {
  const response = await fetch(`${API_BASE}/chats`, {
    credentials: "include",
  });

  if (!response.ok) {
    return parseApiError(response, "Failed to fetch chats");
  }

  return response.json();
}

export async function fetchChat(chatId: string): Promise<ChatThread> {
  const response = await fetch(`${API_BASE}/chats/${chatId}`, {
    credentials: "include",
  });

  if (!response.ok) {
    return parseApiError(response, "Failed to fetch chat");
  }

  return response.json();
}

export async function createChat(message: string): Promise<ChatReply> {
  const response = await fetch(`${API_BASE}/chats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    return parseApiError(response, "Failed to create chat");
  }

  return response.json();
}

export async function addMessage(
  chatId: string,
  message: string,
): Promise<ChatReply> {
  const response = await fetch(`${API_BASE}/chats/${chatId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    return parseApiError(response, "Failed to send message");
  }

  return response.json();
}
