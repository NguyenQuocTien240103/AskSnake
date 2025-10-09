'use client'

import { useEffect } from "react";
import { Navbar } from "@/components/dashboard/navbar";
import { useAuthStore } from "@/stores/use-auth";

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
    <div>
      <Navbar title={title} />
      <div className="container pt-8 pb-8 px-4 sm:px-8">{children}</div>
    </div>
  );
}
