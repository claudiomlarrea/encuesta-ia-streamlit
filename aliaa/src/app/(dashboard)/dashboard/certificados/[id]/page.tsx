import { notFound } from "next/navigation";
import { CertificateView } from "@/components/certificates/certificate-view";
import { DownloadCertificateButton } from "@/components/certificates/download-certificate-button";
import { getCertificateById } from "@/lib/certificates";
import { getCertificateStudentName } from "@/lib/profile-name";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function CertificadoDetallePage({ params }: PageProps) {
  const { id } = await params;
  const cert = await getCertificateById(id);
  if (!cert) notFound();

  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
  const profile = cert.profile as { nombre_completo?: string; email?: string } | null;
  const studentName = getCertificateStudentName({
    nombreEstudiante: cert.nombre_estudiante,
    profile,
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between print:hidden">
        <h1 className="text-2xl font-bold">Certificado</h1>
        <DownloadCertificateButton />
      </div>
      <CertificateView
        studentName={studentName}
        courseTitle={cert.course?.titulo || "Curso ALIAA"}
        verificationCode={cert.codigo_verificacion}
        issuedAt={cert.emitido_en}
        verifyUrl={`${baseUrl}/certificados/verificar?codigo=${cert.codigo_verificacion}`}
      />
    </div>
  );
}
