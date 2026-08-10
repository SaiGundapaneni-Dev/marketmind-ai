"use client";

import { ReactNode, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { getToken } from "@/lib/auth";

const PUBLIC_ROUTES = [
  "/",
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
  "/privacy",
  "/terms",
];

export default function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const isPublic = PUBLIC_ROUTES.includes(pathname);
    const token = getToken();

    if (!token && !isPublic) {
      router.replace("/login");
      return;
    }

    if (token && ["/", "/login", "/register"].includes(pathname)) {
      router.replace("/dashboard");
      return;
    }

    setChecking(false);
  }, [pathname, router]);

  if (checking) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#020817] text-white">
        <div className="text-center">
          <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-[#0F172A] font-black">
            V
          </div>
          <p className="mt-4 text-sm text-slate-400">Checking your session...</p>
        </div>
      </main>
    );
  }

  return <>{children}</>;
}
