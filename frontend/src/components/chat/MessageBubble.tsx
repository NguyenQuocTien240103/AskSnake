import { useTypewriter } from '@/hooks/useTypewriter';

interface MessageBubbleProps {
    role: "human" | "bot";
    content: string;
    image?: string;
    file_name?: string;
    isLatest?: boolean;
}

export function MessageBubble({ role, content, image, file_name, isLatest = false }: MessageBubbleProps) {
    const { displayedText, isTyping } = useTypewriter(
        role === 'bot' && isLatest ? content : content,
        role === 'bot' && isLatest ? 5 : 0
    );

    const textToDisplay = role === 'bot' && isLatest ? displayedText : content;
    const imageUrl = file_name ? `http://localhost:8000/static/${file_name}` : image;

    if (imageUrl) {
        return (
            <div className="flex flex-col items-end max-w-full">
                <div className="mb-3">
                    <img 
                        src={imageUrl} 
                        alt="Uploaded" 
                        className="max-w-64 max-h-64 rounded-lg object-cover shadow-md"
                    />
                </div>
                {content && content !== "Uploaded an image" && (
                    <div className={`
                        p-3 rounded-lg break-words whitespace-pre-wrap max-w-full overflow-hidden shadow-sm
                        ${role === 'human'
                        ? 'bg-blue-500 text-white rounded-br-sm'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-bl-sm'}
                    `}>
                        {textToDisplay}
                        {isTyping && <span className="animate-pulse">|</span>}
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className={`
            p-4 rounded-lg break-words whitespace-pre-wrap max-w-xs md:max-w-md overflow-hidden shadow-sm
            ${role === 'human'
            ? 'bg-blue-500 text-white rounded-br-sm'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-bl-sm'}
        `}>
            <div>
                {textToDisplay}
                {isTyping && <span className="animate-pulse ml-1">|</span>}
            </div>
        </div>
    );
}
