import { Card, CardBody, Tab, Tabs } from '@nextui-org/react';
import { pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import PdfView from './PdfView';
import { DocMeta } from '../../types';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.js',
  import.meta.url
).toString();

export interface PdfBoxProps {
  docs: DocMeta[];
}

export default function PdfBox({ docs }: PdfBoxProps) {
  return (
    <Card className="max-w-2xl w-full h-full">
      <CardBody>
        <Tabs>
          {docs.length === 0
            ? null
            : docs.map((d, i) => (
                <Tab key={i} title={`Source ${i + 1}`}>
                  <PdfView
                    file={require(`../../${d.source}`)}
                    defaultPage={d.page}
                  />
                </Tab>
              ))}
        </Tabs>
      </CardBody>
    </Card>
  );
}
