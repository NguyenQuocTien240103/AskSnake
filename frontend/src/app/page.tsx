import DashboardLayout from '@/components/dashboard/layout'
import { ContentLayout } from "@/components/dashboard/content-layout";
import { ChatPublicLayout } from '@/components/chat/chat-public-layout';
import { ChatContent } from '@/components/chat/chat-content';
import { getUserCurrent } from '@/services/userService';
import { cookies } from 'next/headers';
export default async function Home() {
  let user = null;
  const cookieStore = await cookies()
  // const sessionToken = cookieStore.get('access_token');
  const accessToken = cookieStore.get('access_token')?.value;
  const refreshToken = cookieStore.get('refresh_token')?.value;
  // Tạo string cookie nguyên bản gửi cho backend
  let cookieHeader = '';
  if (accessToken) cookieHeader += `access_token=${accessToken}; `;
  if (refreshToken) cookieHeader += `refresh_token=${refreshToken}; `;


  try {

    if(cookieHeader){
      const res = await getUserCurrent(cookieHeader); 
      user = res.data;
    }

  } 
  catch (error: any) {
    if (error instanceof Response && error.status === 401) {
      console.log("Không xác thực, render public layout");
    } else {
      console.error("Lỗi gọi getUserCurrent:", error);
    }
  } 

  if (!user || !user.email) {
    return (
      <ChatPublicLayout>
        <ChatContent />
      </ChatPublicLayout>
    )
  }

  return (
    <DashboardLayout>
      <ContentLayout user={user} title="AskSnake">
        <ChatContent />
      </ContentLayout>
    </DashboardLayout>
  );

}
