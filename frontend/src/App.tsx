import './App.css';
import { Card, CardHeader, NextUIProvider } from '@nextui-org/react';
import ChatBox from './components/chat/ChatBox';

function App() {
  return (
    <NextUIProvider>
      <div className="flex flex-row justify-center h-screen p-8 gap-8">
        <ChatBox />
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
