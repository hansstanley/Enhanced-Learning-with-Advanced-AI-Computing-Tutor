import { Card, CardHeader } from '@nextui-org/react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import samplePdf from './sample.pdf';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.js',
  import.meta.url
).toString();

export default function PdfBox() {
  return (
    <Card className="max-w-2xl w-full h-full">
      <CardHeader className="w-full h-full">
        <Document className="w-full h-full overflow-auto" file={samplePdf}>
          <Page pageNumber={1} />
        </Document>
      </CardHeader>
    </Card>
  );
}
