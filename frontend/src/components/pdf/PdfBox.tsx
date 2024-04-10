import { Card, CardBody } from '@nextui-org/react';
import { pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import samplePdf from './sample.pdf';
import PdfView from './PdfView';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.js',
  import.meta.url
).toString();

export default function PdfBox() {
  return (
    <Card className="max-w-2xl w-full h-full">
      <CardBody className="flex flex-col w-full h-full">
        <PdfView file={samplePdf} />
      </CardBody>
    </Card>
  );
}
