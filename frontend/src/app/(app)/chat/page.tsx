"use client";

import { useEffect, useRef } from "react";
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
import { DefaultChatTransport } from "ai";
import { useProfileGuard } from "@/hooks/useProfileGuard";
import { useAppContext } from "@/context/AppContext";
import { createChat, getChat, getMessages, saveMessages } from "@/lib/chat-store";
import { Thread } from "@/components/assistant-ui/thread";

function ChatRuntime({ chatId }: { chatId: string }) {
  const runtime = useChatRuntime({
    id: chatId,
    messages: getMessages(chatId),
    transport: new DefaultChatTransport({
      api: "/api/chat",
      body: () => ({ chatId }),
    }),
    onFinish: ({ messages }) => {
      saveMessages(chatId, messages);
    },
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="flex h-full flex-col">
        <Thread />
      </div>
    </AssistantRuntimeProvider>
  );
}

export default function ChatPage() {
  useProfileGuard("chat");

  const { activeChatId, isChatStoreReady, setActiveChatId } = useAppContext();
  const hasCreatedInitialChat = useRef(false);
  const activeChatExists = activeChatId ? getChat(activeChatId) !== null : false;

  useEffect(() => {
    if (!isChatStoreReady) return;
    if (hasCreatedInitialChat.current) return;
    if (activeChatId && activeChatExists) return;

    const chat = createChat();
    hasCreatedInitialChat.current = true;
    setActiveChatId(chat.id);
  }, [activeChatExists, activeChatId, isChatStoreReady, setActiveChatId]);

  if (!isChatStoreReady || !activeChatId || !activeChatExists) return null;

  return <ChatRuntime key={activeChatId} chatId={activeChatId} />;
}
