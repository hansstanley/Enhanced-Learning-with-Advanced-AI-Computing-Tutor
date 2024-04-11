import { Card, CardBody } from '@nextui-org/react';
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
  return (
    <Card
      className={isUser ? 'self-end ml-4 bg-primary-50' : 'self-start mr-4'}
    >
      <CardBody>
        <Markdown remarkPlugins={[remarkGfm]}>{message}</Markdown>
      </CardBody>
    </Card>
  );
}
