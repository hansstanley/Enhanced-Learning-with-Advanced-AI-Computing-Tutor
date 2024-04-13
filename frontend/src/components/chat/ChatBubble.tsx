import { Card, CardBody, Skeleton } from '@nextui-org/react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export interface ChatBubbleProps {
  message: string;
  isUser?: boolean;
}

export default function ChatBubble({
  message,
  isUser = false,
}: ChatBubbleProps) {
  const isLoaded = !!message;
  return (
    <Card
      className={`max-w-[calc(100%_-_1rem)] ${isUser ? 'self-end ml-4 bg-primary-50' : 'self-start mr-4'}`}
    >
      <CardBody>
        <Skeleton isLoaded={isLoaded} className="rounded-md">
          {isLoaded || <p className="text-base">Loading...</p>}
          <Markdown remarkPlugins={[remarkGfm]} className="prose">
            {message}
          </Markdown>
        </Skeleton>
      </CardBody>
    </Card>
  );
}
