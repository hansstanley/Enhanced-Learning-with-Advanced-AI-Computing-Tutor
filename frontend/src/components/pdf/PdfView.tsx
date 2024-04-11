import { Button, Card, CardBody, CardFooter } from '@nextui-org/react';
import { useState } from 'react';
import { FaAngleLeft, FaAngleRight } from 'react-icons/fa6';
import { Document, Page } from 'react-pdf';

export interface PdfViewProps {
  file: any;
  defaultPage?: number;
}

export default function PdfView({ file, defaultPage }: PdfViewProps) {
  const [page, setPage] = useState(defaultPage || 0);
  const [pageCount, setPageCount] = useState(1);

  const prevPage = () => setPage(Math.max(page - 1, 0));
  const nextPage = () => setPage(Math.min(page + 1, pageCount - 1));

  return (
    <Card isFooterBlurred className="relative">
      <CardBody>
        <Document
          className="overflow-auto"
          file={file}
          onLoadSuccess={({ numPages }) => setPageCount(numPages)}
        >
          <Page pageIndex={page} />
        </Document>
      </CardBody>
      <Card className="absolute w-fit z-10 top-4 right-4">
        <CardBody className="flex flex-row items-center gap-4">
          <Button isIconOnly onClick={prevPage} isDisabled={page === 0}>
            <FaAngleLeft />
          </Button>
          <p className="text-sm">{page + 1}</p>
          <Button
            isIconOnly
            onClick={nextPage}
            isDisabled={page === pageCount - 1}
          >
            <FaAngleRight />
          </Button>
        </CardBody>
      </Card>
    </Card>
  );
}
