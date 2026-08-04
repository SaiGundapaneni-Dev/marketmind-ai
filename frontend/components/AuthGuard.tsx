"use client";

import { ReactNode, useEffect } from "react";
import {
  usePathname,
  useRouter,
} from "next/navigation";

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
    }
  }, [pathname, router]);

  /*
   * Always render the same child tree during server rendering,
   * initial hydration, and client-side navigation.
   *
   * Authentication redirects occur after mounting.
   */
  return <>{children}</>;
}