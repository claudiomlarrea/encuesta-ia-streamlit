"use client";

import { useEffect, useRef } from "react";
import QRCode from "qrcode";
import { Award } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { SITE_FULL_NAME } from "@/lib/constants";

interface CertificateViewProps {
  studentName: string;
  courseTitle: string;
  verificationCode: string;
  issuedAt: string;
  verifyUrl: string;
}

export function CertificateView({
  studentName,
  courseTitle,
  verificationCode,
  issuedAt,
  verifyUrl,
}: CertificateViewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (canvasRef.current) {
      QRCode.toCanvas(canvasRef.current, verifyUrl, { width: 120, margin: 1 });
    }
  }, [verifyUrl]);

  return (
    <div className="mx-auto max-w-3xl rounded-2xl border-4 border-[var(--aliaa-primary)] bg-white p-8 text-center shadow-xl dark:bg-zinc-900">
      <div className="mb-6 flex justify-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--aliaa-primary)]">
          <Award className="h-8 w-8 text-white" />
        </div>
      </div>

      <p className="text-sm uppercase tracking-widest text-[var(--aliaa-muted-foreground)]">
        {SITE_FULL_NAME}
      </p>
      <h2 className="mt-2 text-2xl font-bold text-[var(--aliaa-foreground)]">
        Certificado de Finalización
      </h2>
      <p className="mt-4 text-[var(--aliaa-muted-foreground)]">
        Se certifica que
      </p>
      <p className="mt-2 text-3xl font-bold text-[var(--aliaa-primary)]">
        {studentName}
      </p>
      <p className="mt-4 text-[var(--aliaa-muted-foreground)]">
        ha completado satisfactoriamente el curso
      </p>
      <p className="mt-2 text-xl font-semibold">{courseTitle}</p>
      <p className="mt-6 text-sm text-[var(--aliaa-muted-foreground)]">
        Emitido el {formatDate(issuedAt)}
      </p>

      <div className="mt-8 flex items-end justify-between border-t border-[var(--aliaa-border)] pt-6">
        <div className="text-left">
          <p className="text-xs text-[var(--aliaa-muted-foreground)]">Código de verificación</p>
          <p className="font-mono text-sm font-bold">{verificationCode}</p>
        </div>
        <canvas ref={canvasRef} />
      </div>
    </div>
  );
}
