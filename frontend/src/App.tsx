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

function App() {
  return (
    <NextUIProvider>
      <div className="flex flex-row justify-center h-screen p-8 gap-8">
        <Card className="max-w-2xl w-full h-full">
          <CardHeader className="flex gap-2">
            <Image alt="logo" width={40} height={40} radius="sm" src={logo} />
            <p className="text-base">CS Tutor</p>
          </CardHeader>
          <Divider />
          <CardBody></CardBody>
          <Divider />
          <CardFooter className="flex flex-row gap-2">
            <Input isClearable type="text" placeholder="Ask anything" />
            <Button isIconOnly color="primary">
              <FaArrowUp />
            </Button>
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
