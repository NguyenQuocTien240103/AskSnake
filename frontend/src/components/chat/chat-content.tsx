'use client'

import { useState, useEffect } from "react";
import { Paperclip, Send, Folder, X } from "lucide-react"; 
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { prompt } from "@/services/chatService"
import { useRef } from "react";

interface Message {
    sender: "user" | "bot";
    text: string;
    image?: string; // URL hoặc base64 của hình ảnh
  }
export function ChatContent() {
    const [showContent, setShowContent] = useState<boolean>(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const messagesEndRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (messagesEndRef.current) {
          messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
      }, [messages]);
      
  
    const isSendDisabled = !message.trim() && !selectedFile;
  
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        setSelectedFile(e.target.files[0]);
      }
    };
  
    const handleFileRemove = () => {
      setSelectedFile(null);
    };      

    const handleSend = async () => {
        if (isSendDisabled) return;
        setShowContent(true);
      
        // Hiển thị tin nhắn người dùng ngay lập tức
        const imageUrl = selectedFile ? URL.createObjectURL(selectedFile) : undefined;
        const userMsg: Message = { 
          sender: "user", 
          text: message.trim() || "Uploaded an image",
          image: imageUrl
        };
        setMessages((prev) => [...prev, userMsg]);
      
        // Xóa input và file ngay lập tức (trước khi gọi API)
        setMessage("");
        setSelectedFile(null);

        // Bật trạng thái loading
        setIsLoading(true);
      
        // Chuẩn bị formData gửi lên server
        const formData = new FormData();
        formData.append("message", message.trim());
        if (selectedFile) {
          formData.append("file", selectedFile);
        }
      
        try {
          const response = await prompt(formData);
          console.log("Full response:", response);
      
          let responseText = "Unable to process";
          if (response?.data?.prediction) {
            responseText = `Identified as: ${response.data.prediction}`;
          } else if (response?.data?.response_rag) {
            responseText = response.data.response_rag;
          }
      
          const botMsg: Message = {
            sender: "bot",
            text: responseText
          };
      
          setMessages((prev) => [...prev, botMsg]);
        } catch (error) {
          console.error("Error sending data:", error);
          const errorMsg: Message = {
            sender: "bot",
            text: "Sorry, there was an error processing your request."
          };
          setMessages((prev) => [...prev, errorMsg]);
        } finally {
            // Tắt trạng thái loading
            setIsLoading(false);
        }
      };
      

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
                    <div className="w-5/6 md:max-w-2xl flex flex-col gap-4 pb-22">
                     {messages.map((msg, index) => (
                        <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} mb-3`}>
                            {msg.image ? (
                                // Nếu có hình ảnh, hiển thị riêng biệt không có background
                                <div className="flex flex-col items-end max-w-full">
                                    <div className="mb-3">
                                        <img 
                                            src={msg.image} 
                                            alt="Uploaded" 
                                            className="max-w-64 max-h-64 rounded-lg object-cover shadow-md"
                                        />
                                    </div>
                                    {msg.text && msg.text !== "Uploaded an image" && (
                                        <div className={`
                                            p-3 rounded-lg break-words whitespace-pre-wrap max-w-full overflow-hidden shadow-sm
                                            ${msg.sender === 'user'
                                            ? 'bg-blue-500 text-white rounded-br-sm'
                                            : 'bg-gray-200 text-gray-900 rounded-bl-sm'}
                                        `}>
                                            {msg.text}
                                        </div>
                                    )}
                                </div>
                            ) : (
                                // Nếu không có hình ảnh, hiển thị bình thường
                                <div className={`
                                    p-4 rounded-lg break-words whitespace-pre-wrap max-w-xs md:max-w-md overflow-hidden shadow-sm
                                    ${msg.sender === 'user'
                                    ? 'bg-blue-500 text-white rounded-br-sm'
                                    : 'bg-gray-200 text-gray-900 rounded-bl-sm'}
                                `}>
                                    <div>{msg.text}</div>
                                </div>
                            )}
                        </div>
                        ))}
                        {/* Scroll down */}
                        <div ref={messagesEndRef} />
                        {/* Hiển thị loading khi đang chờ phản hồi */}
                        {isLoading && (
                            <div className="flex justify-start mb-3">
                                <div className="bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 p-4 rounded-lg rounded-bl-sm shadow-sm">
                                    <div className="flex items-center gap-2">
                                        <div className="flex gap-1">
                                            <span className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                            <span className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                            <span className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                        </div>
                                        <span className="text-sm">Thinking...</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )
            }

            {
                !showContent ? (
                    <div className="fixed bottom-0 flex justify-center mb-10 w-full sm:flex-1 sm:static sm:w-full sm:mb-0 sm:items-start"> 
                        <div className="mt-2 flex w-5/6 md:max-w-2xl gap-2 border rounded-lg px-3 py-2 shadow-sm bg-white dark:bg-zinc-900">
                            <Button variant="ghost" size="icon" type="button">
                                <label className="cursor-pointer">
                                    <Paperclip className="w-5 h-5 text-zinc-500" />
                                    <input
                                        type="file"
                                        className="hidden"
                                        onChange={handleFileChange}
                                    />
                                </label>
                            </Button>
                            <Input
                                type="text"
                                placeholder="Type your message..."
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && !isSendDisabled && handleSend()}
                                className="flex-1 border-none bg-transparent focus:outline-none text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 "
                            />
                            {selectedFile && (
                                <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-md">
                                    <Folder className="w-5 h-5 text-blue-500" />
                                    <span className="text-sm text-zinc-900 dark:text-zinc-100 truncate max-w-[150px]">
                                        {selectedFile.name}
                                    </span>
                                    <button onClick={handleFileRemove} className="text-red-500">
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>
                            )}
                            <Button type="submit" variant="ghost" size="icon" onClick={handleSend} disabled={isSendDisabled}>
                                <Send className="w-5 h-5 text-zinc-500" />
                            </Button>
                        </div>
                    </div>
                ): (
                    <div className="fixed bottom-0 flex justify-center mb-8 w-full"> 
                        <div className="mt-2 flex w-5/6 md:max-w-2xl gap-2 border rounded-lg px-3 py-2 shadow-sm bg-white dark:bg-zinc-900">
                            <Button variant="ghost" size="icon" type="button">
                                <label className="cursor-pointer">
                                    <Paperclip className="w-5 h-5 text-zinc-500" />
                                    <input
                                        type="file"
                                        className="hidden"
                                        onChange={handleFileChange}
                                    />
                                </label>
                            </Button>
                            <Input
                                type="text"
                                placeholder="Type your message..."
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && !isSendDisabled && handleSend()}
                                className="flex-1 border-none bg-transparent focus:outline-none text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 "
                            />
                            {selectedFile && (
                                <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-md">
                                    <Folder className="w-5 h-5 text-blue-500" />
                                    <span className="text-sm text-zinc-900 dark:text-zinc-100 truncate max-w-[150px]">
                                        {selectedFile.name}
                                    </span>
                                    <button onClick={handleFileRemove} className="text-red-500">
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>
                            )}
                            <Button type="submit" variant="ghost" size="icon" onClick={handleSend} disabled={isSendDisabled}>
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