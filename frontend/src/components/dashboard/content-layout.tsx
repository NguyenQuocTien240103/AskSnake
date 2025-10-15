'use client'

import { useEffect } from "react";
import { Navbar } from "@/components/dashboard/navbar";
import { useAuthStore } from "@/stores/use-auth";
import { Footer } from "@/components/dashboard/footer";
import { cn } from "@/lib/utils";

interface ContentLayoutProps {
  user: any;
  title: string;
  children: React.ReactNode;
}

export function ContentLayout({ user, title, children }: ContentLayoutProps) {
  const {setLogin} = useAuthStore();

  useEffect(() => {
    setLogin(user);
  }, [user, setLogin]);

  return (
    <div className="h-full flex flex-col">
      <Navbar title={title} />
      <div className="flex-1 flex flex-col pt-4 pb-4 px-4 sm:px-8">{children}</div>
    </div>
  );
}
