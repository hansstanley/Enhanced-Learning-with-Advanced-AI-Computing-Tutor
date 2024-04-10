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

export default function ChatBox() {
  const bottom = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: 'Hi, how may I help you?' },
  ]);

  const addMessages = (...newMessages: ChatMessage[]) =>
    setMessages([...messages, ...newMessages]);

  const handleSubmitInput = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (input.trim()) {
      addMessages({ role: 'user', content: input.trim() });
      setInput('');
    }
  };

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, bottom]);

  return (
    <Card className="max-w-2xl w-full h-full">
      <CardHeader className="flex gap-2">
        <Image alt="logo" width={32} height={32} radius="sm" src={logo} />
        <p className="text-base font-bold">CS Tutor</p>
      </CardHeader>
      <Divider />
      <CardBody>
        <div className="flex flex-col gap-2 w-full">
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
            onChange={(e) => setInput(e.target.value)}
          />
          <Button isIconOnly color="primary" type="submit">
            <FaArrowUp />
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}
