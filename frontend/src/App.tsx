import './App.css';
import { NextUIProvider } from '@nextui-org/react';
import ChatBox from './components/chat/ChatBox';
import PdfBox from './components/pdf/PdfBox';

function App() {
  return (
    <NextUIProvider>
      <div className="flex flex-row justify-center h-screen p-8 gap-8">
        <ChatBox />
        <PdfBox />
      </div>
    </NextUIProvider>
  );
}

export default App;
