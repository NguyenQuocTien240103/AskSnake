'use client'

import { useState, useEffect } from "react";
import { Paperclip, Send } from "lucide-react"; 
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function ChatContent() {
    const [showContent, setShowContent] = useState<boolean>(false);
    const content = [
      'abc',
      'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu', 'vwx', 'yzs', 'yzs', 'yzs'
    ];

    return (
        <div className="flex-1 flex flex-col justify-center">
            <main className="flex-1 flex flex-col gap-4 items-center">
            {
                !showContent ? (
                    <div className="flex-1 flex flex-col justify-center sm:justify-end sm:items-center">                     
                        <h1 className="text-center text-3xl font-bold leading-tight tracking-tighter md:text-5xl lg:leading-[1.1]">
                        Ask Snake
                        </h1>
                    </div>
                ) : (
                    <div className="w-5/6 md:max-w-2xl flex flex-col gap-2 pb-22">
                    {content.map((item, index) => (
                        <div key={index} className={`flex ${index % 2 === 0 ? 'justify-start' : 'justify-end'}`}>
                        <div
                            className={`
                            p-4 
                            rounded-lg 
                            break-words 
                            whitespace-pre-wrap 
                            max-w-full 
                            overflow-hidden 
                            ${index % 2 === 0 ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-900'}
                            `}
                        >
                            {item}
                        </div>
                        </div>
                    ))}
                    </div>
                )
            }

            {
                !showContent ? (
                    <div className="fixed bottom-0 flex justify-center mb-10 w-full sm:flex-1 sm:static sm:w-full sm:mb-0 sm:items-start"> 
                        <div className="mt-2 flex w-5/6 md:max-w-2xl gap-2 border rounded-lg px-3 py-2 shadow-sm bg-white dark:bg-zinc-900">
                            <Button variant="ghost" size="icon" type="button">
                                <Paperclip className="w-5 h-5 text-zinc-500" />
                            </Button>
                            <Input
                                type="text"
                                placeholder="Type your message..."
                                className="flex-1 border-none bg-transparent focus:outline-none text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 "
                            />
                            <Button type="submit" variant="ghost" size="icon" onClick={(e) => setShowContent(true)}>
                                <Send className="w-5 h-5 text-zinc-500" />
                            </Button>
                        </div>
                    </div>
                ): (
                    <div className="fixed bottom-0 flex justify-center mb-10 w-full"> 
                        <div className="mt-2 flex w-5/6 md:max-w-2xl gap-2 border rounded-lg px-3 py-2 shadow-sm bg-white dark:bg-zinc-900">
                            <Button variant="ghost" size="icon" type="button">
                                <Paperclip className="w-5 h-5 text-zinc-500" />
                            </Button>
                            <Input
                                type="text"
                                placeholder="Type your message..."
                                className="flex-1 border-none bg-transparent focus:outline-none text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 "
                            />
                            <Button type="submit" variant="ghost" size="icon" onClick={(e) => setShowContent(true)}>
                                <Send className="w-5 h-5 text-zinc-500" />
                            </Button>
                        </div>
                    </div>  
                )
            }
            </main>
        </div>
    )
}