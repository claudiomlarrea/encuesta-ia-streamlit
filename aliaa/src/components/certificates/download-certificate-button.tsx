"use client";

import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";

export function DownloadCertificateButton() {
  function handleDownload() {
    window.print();
  }

  return (
    <Button variant="outline" onClick={handleDownload}>
      <Download className="mr-2 h-4 w-4" />
      Descargar PDF
    </Button>
  );
}
