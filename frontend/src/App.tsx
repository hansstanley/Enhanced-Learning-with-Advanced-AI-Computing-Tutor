import './App.css';
import { useState } from 'react';
import { NextUIProvider } from '@nextui-org/react';
import ChatBox from './components/chat/ChatBox';
import PdfBox from './components/pdf/PdfBox';
import { DocMeta } from './types';

function App() {
  const [docs, setDocs] = useState<DocMeta[]>([]);

  const hidePdfBox = docs.length === 0;

  return (
    <NextUIProvider>
      <div className="flex flex-row justify-center h-screen p-8 gap-8">
        <ChatBox onDocsChange={(docs) => setDocs(docs)} />
        {hidePdfBox || <PdfBox docs={docs} />}
      </div>
    </NextUIProvider>
  );
}

export default App;
