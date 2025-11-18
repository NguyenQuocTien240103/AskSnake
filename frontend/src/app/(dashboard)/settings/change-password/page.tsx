'use client'

import Link from "next/link";
import { ChangePasswordForm } from '@/app/(dashboard)/settings/change-password/change-password-form'
import { ContentLayout } from "@/components/dashboard/content-layout";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { useAuthStore } from "@/stores/use-auth";
import { useEffect, useState } from "react";
import { getUserCurrent } from '@/services/userService';
import { Skeleton } from "@/components/ui/skeleton";
import { useRouter } from 'next/navigation'

export default function AccountPage() {
  const router = useRouter();
  const {setLogin, setLogout} = useAuthStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await getUserCurrent();
        setLogin(res.data)
        setLoading(false)
      } catch (error: any) {
        console.error(error);
        
        if(error.response?.status === 401){
          setLogout();
          router.push("/login")
          return;
        }

      } 
      // finally {
      //   setLoading(false)
      // }
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
    <ContentLayout title="Change Password">
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