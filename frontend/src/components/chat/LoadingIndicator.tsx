export function LoadingIndicator() {
    return (
        <div className="flex justify-start mb-3">
            <div className="bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 p-4 rounded-lg rounded-bl-sm shadow-sm">
                <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                        <span className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    </div>
                    <span className="text-sm"></span>
                </div>
            </div>
        </div>
    );
}
