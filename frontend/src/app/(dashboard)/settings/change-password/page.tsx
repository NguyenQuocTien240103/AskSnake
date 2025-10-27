'use client'

import Link from "next/link";
import { ChangePasswordForm } from '@/app/(dashboard)/settings/change-password/change-password-form'
import { ContentLayout } from "@/components/dashboard/content-layout";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { useAuthStore } from "@/stores/use-auth";
import { useEffect, useState } from "react";
import { getUserCurrent } from '@/services/userService';
import { Skeleton } from "@/components/ui/skeleton";

export default function AccountPage() {
  const { user, setLogin } = useAuthStore();
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await getUserCurrent();
        setLogin(res.data)
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false)
      }
    };
    fetchUser();
  }, []);

  if(loading){
    return (
      <div className="space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-[400px] w-full" />
      </div>
    )
  }

  return (
    <ContentLayout title="Change Password" user={user}>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href="/">Home</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Change Password</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      
      <div className="mt-6">
        <ChangePasswordForm />
      </div>
    </ContentLayout>
  )
}