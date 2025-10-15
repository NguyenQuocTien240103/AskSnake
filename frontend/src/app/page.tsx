'use client'

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/dashboard/layout';
import { ContentLayout } from "@/components/dashboard/content-layout";
import { ChatPublicLayout } from '@/components/chat/chat-public-layout';
import { ChatContent } from '@/components/chat/chat-content';
import { getUserCurrent } from '@/services/userService';

type User = {
  email: string;
}

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await getUserCurrent();
        setUser(res.data);
      } catch (error) {
        console.error(error);
        setUser(null); 
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  if (loading) {
    return; 
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
      <ContentLayout user={user} title="AskSnake">
        <ChatContent />
      </ContentLayout>
    </DashboardLayout>
  );
}
