export type Citation = {
  source_title: string;
  source_url: string;
  content: string;
};

export type MessageRole = "user" | "assistant";

export type Message = {
  role: MessageRole;
  content: string;
  citations: Citation[] | null;
  created_at: string;
};

export type Chat = {
  id: string;
  title: string;
  created_at: string;
};

export type ChatThread = {
  chat_id: string;
  messages: Message[];
};

export type ChatReply = {
  chat_id: string;
  user_message: Message;
  assistant_message: Message;
};
