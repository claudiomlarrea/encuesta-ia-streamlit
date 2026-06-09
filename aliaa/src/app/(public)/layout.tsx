import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { getProfile } from "@/lib/supabase/server";

export default async function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const profile = await getProfile();

  return (
    <>
      <Header profile={profile} />
      <main className="flex-1">{children}</main>
      <Footer />
    </>
  );
}
