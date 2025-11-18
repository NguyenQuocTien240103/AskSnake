'use client'

import DashboardLayout from '@/components/dashboard/layout';
import { useState, useEffect } from 'react';
import { ContentLayout } from "@/components/dashboard/content-layout";
import { ChatPublicLayout } from '@/components/chat/chat-public-layout';
import { ChatContent } from '@/components/chat/chat-content';
import { getUserCurrent } from '@/services/userService';
import { useAuthStore } from "@/stores/use-auth";
import Loading from './loading';

export default function Home() {
  const [loading, setLoading] = useState(true);
  const {user, setLogin, setLogout} = useAuthStore();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await getUserCurrent();
        setLogin(res.data)
      } catch (error) {
        console.error(error);
        setLogout()
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  if (loading) {
    return <Loading />;
  }

  if (!user || !user.email) {
    return (
      <ChatPublicLayout>
        <ChatContent />
      </ChatPublicLayout>
    );
  }

  return (
    <DashboardLayout>
      <ContentLayout title="AskSnake">
        <ChatContent />
      </ContentLayout>
    </DashboardLayout>
  );
}