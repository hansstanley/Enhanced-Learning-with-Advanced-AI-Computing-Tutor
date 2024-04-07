import ChatBubble from "./ChatBubble";

export interface ChatBoxProps {
  messages: string[];
}

export default function ChatBox({ messages }: ChatBoxProps) {
  return (
    <div className="flex flex-col gap-2 w-full">
      {messages.map((m, i) => (
        <ChatBubble message={m} isUser={i % 2 !== 0} />
      ))}
    </div>
  );
}
