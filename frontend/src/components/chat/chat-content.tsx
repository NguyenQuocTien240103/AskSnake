'use client'

import { Paperclip, Send } from "lucide-react"; // icon từ lucide.dev
import { useAuthStore } from "@/stores/use-auth";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Spinner } from '@/components/ui/shadcn-io/spinner'

export function ChatContent() {
    // const {isLogout} = useAuthStore();

    // if(isLogout){
    //     return (
    //         <div className="h-screen w-screen flex items-center justify-center">
    //             <Spinner />
    //         </div>
    //     )
    // }
    return (
        <main className="min-h-[calc(100vh-57px-120px)] flex flex-col gap-4">
            <div className="flex-1 flex justify-center items-end">                     
              <h1 className="text-center text-3xl font-bold leading-tight tracking-tighter md:text-5xl lg:leading-[1.1]">
                  Ask Snake
              </h1>
            </div>
            <div className="flex-1 flex justify-center items-end sm:items-start">
              <form className="mt-2 flex w-5/6 md:max-w-2xl gap-2 border rounded-lg px-3 py-2 shadow-sm bg-white dark:bg-zinc-900">
                  <Button variant="ghost" size="icon" type="button">
                      <Paperclip className="w-5 h-5 text-zinc-500" />
                  </Button>
                  <Input
                      type="text"
                      placeholder="Type your message..."
                      className="flex-1 border-none bg-transparent focus:outline-none text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 "
                  />
                  <Button type="submit" variant="ghost" size="icon">
                      <Send className="w-5 h-5 text-zinc-500" />
                  </Button>
              </form>
            </div>
        </main>
    )
}
