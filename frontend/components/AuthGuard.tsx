"use client";

import { ReactNode, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { getToken } from "@/lib/auth";

const PUBLIC_ROUTES = [
  "/",
  "/login",
  "/register",
];

export default function AuthGuard({
  children,
}: {
  children: ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const isPublicRoute = PUBLIC_ROUTES.includes(pathname);
    const token = getToken();

    if (!token && !isPublicRoute) {
      router.replace("/login");
      return;
    }

    // Logged-in users should enter the application rather than
    // seeing auth screens or the marketing homepage.
    if (
      token &&
      (pathname === "/" ||
        pathname === "/login" ||
        pathname === "/register")
    ) {
      router.replace("/dashboard");
      return;
    }

    setChecking(false);
  }, [pathname, router]);

  if (checking) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#020817] text-white">
        <div className="text-center">
          <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-[#0F172A] text-lg font-black">
            V
          </div>

          <p className="mt-4 text-sm text-slate-400">
            Checking your session...
          </p>
        </div>
      </main>
    );
  }

  return <>{children}</>;
}
