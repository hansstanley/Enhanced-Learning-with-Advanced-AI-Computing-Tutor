import { FormEvent, useEffect, useRef, useState } from 'react';
import ChatBubble from './ChatBubble';
import { ChatMessage } from '../../types';
import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Divider,
  Image,
  Input,
} from '@nextui-org/react';
import { FaArrowUp } from 'react-icons/fa6';
import logo from '../../logo.svg';

async function* streamCompletion() {
  const message =
    'Aliquip eiusmod laboris do et exercitation pariatur dolore nulla officia dolor magna.';
  const words = message.split(' ');
  for (const word of words) {
    yield ' ' + word;
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
}

function addToLastMessage(
  messages: ChatMessage[],
  chunk: string
): ChatMessage[] {
  if (messages.length === 0) {
    return [];
  }

  const { role, content } = messages[messages.length - 1];
  return [
    ...messages.slice(0, messages.length - 1),
    { role, content: content + chunk },
  ];
}

const defaultMessages: ChatMessage[] = [
  { role: 'assistant', content: 'Hi, how may I help you?' },
];

export default function ChatBox() {
  const bottom = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>(defaultMessages);

  const addMessages = (...newMessages: ChatMessage[]) =>
    setMessages((messages) => [...messages, ...newMessages]);

  const clearMessages = () => setMessages(defaultMessages);

  const handleSubmitInput = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (input.trim()) {
      addMessages(
        { role: 'user', content: input.trim() },
        { role: 'assistant', content: '' }
      );
      setInput('');
    }
    for await (let chunk of streamCompletion()) {
      setMessages((messages) => addToLastMessage(messages, chunk));
    }
  };

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, bottom]);

  return (
    <Card className="max-w-2xl w-full h-full">
      <CardHeader className="flex flex-row justify-between gap-2">
        <div className="flex flex-row gap-2">
          <Image alt="logo" width={32} height={32} radius="sm" src={logo} />
          <p className="text-base font-bold">CS Tutor</p>
        </div>
        <Button onClick={clearMessages} isDisabled={messages.length < 2}>
          Reset
        </Button>
      </CardHeader>
      <Divider />
      <CardBody>
        <div className="flex flex-col gap-4 w-full">
          {messages.map((m, i) => (
            <ChatBubble
              key={i}
              message={m.content}
              isUser={m.role === 'user'}
            />
          ))}
        </div>
        <div ref={bottom} />
      </CardBody>
      <Divider />
      <CardFooter>
        <form
          className="flex flex-row w-full gap-2"
          onSubmit={handleSubmitInput}
        >
          <Input
            isClearable
            id="input"
            name="input"
            type="text"
            placeholder="Ask anything"
            autoComplete="off"
            value={input}
            onClear={() => setInput('')}
            onChange={(e) => setInput(e.target.value)}
          />
          <Button
            isIconOnly
            isDisabled={input.length === 0}
            color="primary"
            type="submit"
          >
            <FaArrowUp />
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}
