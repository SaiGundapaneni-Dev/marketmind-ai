"use client";

import { usePathname, useRouter } from "next/navigation";
import {
  ReactNode,
  useEffect,
  useState,
} from "react";

import { getToken } from "@/lib/auth";

const PUBLIC_ROUTES = [
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

  const [checking, setChecking] =
    useState(true);

  useEffect(() => {
    const isPublicRoute =
      PUBLIC_ROUTES.includes(pathname);

    const token = getToken();

    if (!token && !isPublicRoute) {
      router.replace("/login");
      return;
    }

    if (token && isPublicRoute) {
      router.replace("/");
      return;
    }

    setChecking(false);
  }, [pathname, router]);

  if (checking) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="text-center">
          <p className="text-lg font-semibold">
            Vestora AI
          </p>

          <p className="mt-2 text-sm text-slate-400">
            Checking your session...
          </p>
        </div>
      </main>
    );
  }

  return <>{children}</>;
}