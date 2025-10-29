// 'use client'

// import { useState, useEffect } from "react";
// import { Paperclip, Send, Folder, X } from "lucide-react"; 
// import { Input } from "@/components/ui/input";
// import { Button } from "@/components/ui/button";
// import { prompt } from "@/services/chatService"
// interface Message {
//     sender: "user" | "bot";
//     text: string;
//   }
// export function ChatContent() {
//     const [showContent, setShowContent] = useState<boolean>(false);
//     const [selectedFile, setSelectedFile] = useState<File | null>(null);
//     const [message, setMessage] = useState("");
//     const [messages, setMessages] = useState<Message[]>([]);
  
//     const isSendDisabled = !message.trim() && !selectedFile;
  
//     const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
//       if (e.target.files && e.target.files.length > 0) {
//         setSelectedFile(e.target.files[0]);
//       }
//     };
  
//     const handleFileRemove = () => {
//       setSelectedFile(null);
//     };
    
//     const handleSend = async () => {
//       if (isSendDisabled) return;
//       setShowContent(true);
        
//       const userMsg: Message = { sender: "user", text: message.trim() };
//       setMessages((prev) => [...prev, userMsg]); // hiển thị tin người dùng ngay
  
//       const formData = new FormData();
//       formData.append("message", message.trim());
//       if (selectedFile) {
//         formData.append("file", selectedFile);
//       }
  
//       try {
//         const response = await prompt(formData);
  
//         const botMsg: Message = {
//           sender: "bot",
//           text: response?.reply || JSON.stringify(response), // tuỳ backend trả về
//         };
  
//         setMessages((prev) => [...prev, botMsg]);
//         setMessage("");
//         setSelectedFile(null);
//       } catch (error) {
//         console.error("Error sending data:", error);
//       }
//     };
      

//     return (
//         <div className="flex-1 flex flex-col justify-center">
//             <main className="flex-1 flex flex-col gap-4 items-center">
//             {
//                 !showContent ? (
//                     <div className="flex-1 flex flex-col justify-center sm:justify-end sm:items-center">                     
//                         <h1 className="text-center text-3xl font-bold leading-tight tracking-tighter md:text-5xl lg:leading-[1.1]">
//                         Ask Snake
//                         </h1>
//                     </div>
//                 ) : (
//                     <div className="w-5/6 md:max-w-2xl flex flex-col gap-2 pb-22">
//                      {messages.map((msg, index) => (
//                         <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
//                             <div
//                             className={`
//                                 p-4 rounded-lg break-words whitespace-pre-wrap max-w-full overflow-hidden
//                                 ${msg.sender === 'user'
//                                 ? 'bg-blue-500 text-white'
//                                 : 'bg-gray-200 text-gray-900'}
//                             `}
//                             >
//                             {msg.text}
//                             </div>
//                         </div>
//                         ))}
//                     </div>
//                 )
//             }

//             {
//                 !showContent ? (
//                     <div className="fixed bottom-0 flex justify-center mb-10 w-full sm:flex-1 sm:static sm:w-full sm:mb-0 sm:items-start"> 
//                         <div className="mt-2 flex w-5/6 md:max-w-2xl gap-2 border rounded-lg px-3 py-2 shadow-sm bg-white dark:bg-zinc-900">
//                             <Button variant="ghost" size="icon" type="button">
//                                 <label className="cursor-pointer">
//                                     <Paperclip className="w-5 h-5 text-zinc-500" />
//                                     <input
//                                         type="file"
//                                         className="hidden"
//                                         onChange={handleFileChange}
//                                     />
//                                 </label>
//                             </Button>
//                             <Input
//                                 type="text"
//                                 placeholder="Type your message..."
//                                 value={message}
//                                 onChange={(e) => setMessage(e.target.value)}
//                                 className="flex-1 border-none bg-transparent focus:outline-none text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 "
//                             />
//                             {selectedFile && (
//                                 <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-md">
//                                     <Folder className="w-5 h-5 text-blue-500" />
//                                     <span className="text-sm text-zinc-900 dark:text-zinc-100 truncate max-w-[150px]">
//                                         {selectedFile.name}
//                                     </span>
//                                     <button onClick={handleFileRemove} className="text-red-500">
//                                         <X className="w-4 h-4" />
//                                     </button>
//                                 </div>
//                             )}
//                             <Button type="submit" variant="ghost" size="icon" onClick={handleSend} disabled={isSendDisabled}>
//                                 <Send className="w-5 h-5 text-zinc-500" />
//                             </Button>
//                         </div>
//                     </div>
//                 ): (
//                     <div className="fixed bottom-0 flex justify-center mb-10 w-full"> 
//                         <div className="mt-2 flex w-5/6 md:max-w-2xl gap-2 border rounded-lg px-3 py-2 shadow-sm bg-white dark:bg-zinc-900">
//                             <Button variant="ghost" size="icon" type="button">
//                                 <label className="cursor-pointer">
//                                     <Paperclip className="w-5 h-5 text-zinc-500" />
//                                     <input
//                                         type="file"
//                                         className="hidden"
//                                         onChange={handleFileChange}
//                                     />
//                                 </label>
//                             </Button>
//                             <Input
//                                 type="text"
//                                 placeholder="Type your message..."
//                                 value={message}
//                                 onChange={(e) => setMessage(e.target.value)}
//                                 className="flex-1 border-none bg-transparent focus:outline-none text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 "
//                             />
//                             {selectedFile && (
//                                 <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-md">
//                                     <Folder className="w-5 h-5 text-blue-500" />
//                                     <span className="text-sm text-zinc-900 dark:text-zinc-100 truncate max-w-[150px]">
//                                         {selectedFile.name}
//                                     </span>
//                                     <button onClick={handleFileRemove} className="text-red-500">
//                                         <X className="w-4 h-4" />
//                                     </button>
//                                 </div>
//                             )}
//                             <Button type="submit" variant="ghost" size="icon" onClick={handleSend} disabled={isSendDisabled}>
//                                 <Send className="w-5 h-5 text-zinc-500" />
//                             </Button>
//                         </div>
//                     </div>  
//                 )
//             }
//             </main>
//         </div>
//     )
// }







'use client'

import { useState, useEffect } from "react";
import { Paperclip, Send, Folder, X } from "lucide-react"; 
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { prompt } from "@/services/chatService"
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
        
      // Tạo URL cho hình ảnh để hiển thị
      const imageUrl = selectedFile ? URL.createObjectURL(selectedFile) : undefined;
      
      const userMsg: Message = { 
        sender: "user", 
        text: message.trim() || "Uploaded an image",
        image: imageUrl
      };
      setMessages((prev) => [...prev, userMsg]);
  
      const formData = new FormData();
      formData.append("message", message.trim());
      if (selectedFile) {
        formData.append("file", selectedFile);
      }
  
      try {
        const response = await prompt(formData);
        console.log("Full response:", response); // Debug
        
        // Parse response để lấy nội dung phù hợp
        let responseText = "Unable to process";
        
        // Trường hợp 1: Upload ảnh - có data.prediction
        if (response?.data?.prediction) {
          responseText = `Identified as: ${response.data.prediction}`;
        }

        // Trường hợp 2: Hỏi câu hỏi - có data.response_rag
        else if (response?.data?.response_rag) {
          responseText = response.data.response_rag;
        }
  
        const botMsg: Message = {
          sender: "bot",
          text: responseText
        };
  
        setMessages((prev) => [...prev, botMsg]);
        setMessage("");
        setSelectedFile(null);
      } catch (error) {
        console.error("Error sending data:", error);
        const errorMsg: Message = {
          sender: "bot",
          text: "Sorry, there was an error processing your request."
        };
        setMessages((prev) => [...prev, errorMsg]);
        setMessage("");
        setSelectedFile(null);
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
                    <div className="fixed bottom-0 flex justify-center mb-10 w-full"> 
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