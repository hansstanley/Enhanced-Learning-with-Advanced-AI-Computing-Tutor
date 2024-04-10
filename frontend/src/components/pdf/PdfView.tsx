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
    <Card isFooterBlurred className="relative w-full h-full">
      <CardBody className="w-full h-full">
        <Document
          className="w-full h-full overflow-auto"
          file={file}
          onLoadSuccess={({ numPages }) => setPageCount(numPages)}
        >
          <Page pageIndex={page} />
        </Document>
      </CardBody>
      <CardFooter className="absolute bg-white/50 w-fit z-10 bottom-4 left-1/2 -translate-x-1/2 shadow-md rounded-xl">
        <Button isIconOnly onClick={prevPage} isDisabled={page === 0}>
          <FaAngleLeft />
        </Button>
        <p className="text-sm mx-4">{page + 1}</p>
        <Button
          isIconOnly
          onClick={nextPage}
          isDisabled={page === pageCount - 1}
        >
          <FaAngleRight />
        </Button>
      </CardFooter>
    </Card>
  );
}
