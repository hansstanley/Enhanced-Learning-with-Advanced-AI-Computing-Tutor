import { FormEvent, useState } from "react";
import logo from "./logo.svg";
import "./App.css";
import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Divider,
  Image,
  Input,
  NextUIProvider,
} from "@nextui-org/react";
import { FaArrowUp } from "react-icons/fa6";
import ChatBox from "./components/chat/ChatBox";

function App() {
  const [input, setInput] = useState<string>("");
  const [messages, setMessages] = useState<string[]>([
    "Hi, how may I help you?",
  ]);

  const addMessages = (...newMessages: string[]) =>
    setMessages([...messages, ...newMessages]);

  const handleSubmitInput = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (input.trim()) {
      addMessages(input.trim(), "Hello world!");
      setInput("");
    }
  };

  return (
    <NextUIProvider>
      <div className="flex flex-row justify-center h-screen p-8 gap-8">
        <Card className="max-w-2xl w-full h-full">
          <CardHeader className="flex gap-2">
            <Image alt="logo" width={32} height={32} radius="sm" src={logo} />
            <p className="text-base font-bold">CS Tutor</p>
          </CardHeader>
          <Divider />
          <CardBody>
            <ChatBox messages={messages} />
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
        <Card className="max-w-2xl w-full h-full">
          <CardHeader>
            <p className="text-base">PDF viewer</p>
          </CardHeader>
        </Card>
      </div>
    </NextUIProvider>
  );
}

export default App;
