import { FormEvent, useEffect, useRef, useState } from 'react';
import ChatBubble from './ChatBubble';
import { ChatMessage, ChatMeta, DocMeta } from '../../types';
import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Divider,
  Image,
  Input,
  Spacer,
} from '@nextui-org/react';
import { FaArrowUp } from 'react-icons/fa6';
import logo from '../../logo.svg';

const API_URL = process.env.REACT_APP_API;

function instanceOfChatMeta(obj: any): obj is ChatMeta {
  return 'docs' in obj;
}

function instanceOfChatMessage(obj: any): obj is ChatMessage {
  return 'content' in obj;
}

async function readNext(reader: ReadableStreamDefaultReader<Uint8Array>) {
  const { done, value } = await reader.read();
  const text = new TextDecoder().decode(value);
  return { done, text };
}

async function clearHistory() {
  await fetch(new URL('/chat/clear', API_URL), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
}

async function query(query: string): Promise<{
  docs?: DocMeta[];
  answer?: AsyncGenerator<string, void, unknown>;
}> {
  const res = await fetch(new URL('/chat', API_URL), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.body) {
    return {};
  }
  const reader = res.body.getReader();

  let done = false;
  let text = '';
  let docs: DocMeta[] | undefined;
  let firstChunk = '';
  while (!done) {
    ({ done, text } = await readNext(reader));
    if (!text) {
      break;
    }
    let obj;
    try {
      obj = JSON.parse(text);
    } catch (err) {
      console.log('bad json', text);
      console.error(err);
      break;
    }
    if (instanceOfChatMeta(obj)) {
      docs = obj.docs;
    } else if (instanceOfChatMessage(obj)) {
      firstChunk = obj.content;
      break;
    }
  }

  async function* stream() {
    if (firstChunk) {
      yield firstChunk;
    }
    let done = false;
    while (!done) {
      ({ done, text } = await readNext(reader));
      if (!text) {
        break;
      }
      let obj;
      try {
        obj = JSON.parse(text);
      } catch (err) {
        console.log('bad json', text);
        console.error(err);
        break;
      }
      if (instanceOfChatMessage(obj)) {
        yield obj.content;
      }
    }
  }

  return { docs, answer: stream() };
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

export interface ChatBoxProps {
  onDocsChange?: (docs: DocMeta[]) => void;
}

export default function ChatBox({ onDocsChange = () => {} }: ChatBoxProps) {
  const bottom = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(defaultMessages);

  const addMessages = (...newMessages: ChatMessage[]) =>
    setMessages((messages) => [...messages, ...newMessages]);

  const clearMessages = async () => {
    setMessages(defaultMessages);
    onDocsChange([]);

    await clearHistory();
  };

  const handleSubmitInput = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    addMessages(
      { role: 'user', content: input },
      { role: 'assistant', content: '' }
    );
    setInput('');

    const { docs, answer } = await query(input);
    onDocsChange(docs || []);
    if (answer) {
      for await (let chunk of answer) {
        setMessages((messages) => addToLastMessage(messages, chunk));
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, bottom]);

  return (
    <Card isFooterBlurred className="max-w-2xl w-full h-full">
      <CardHeader className="flex flex-row justify-between gap-2">
        <div className="flex flex-row gap-2">
          <Image alt="logo" width={32} height={32} radius="sm" src={logo} />
          <p className="text-base font-bold">CS Tutor</p>
        </div>
        <Button
          onClick={clearMessages}
          isDisabled={loading || messages.length < 2}
        >
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
        <Spacer y={16} />
        <div ref={bottom} />
      </CardBody>
      <CardFooter className="before:bg-white/20 border-white/30 border-1 overflow-hidden p-2 absolute rounded-2xl bottom-2 w-[calc(100%_-_16px)] shadow-medium mx-2 z-10">
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
