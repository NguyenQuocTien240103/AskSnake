import request from '@/utils/request'

export const prompt = async (payload: any): Promise<any> => {
    const res = await request.post('chat/prompt', payload)
    return res
}
export const promptPublic = async (payload: any): Promise<any> => {
    const res = await request.post('chat/prompt-public', payload)
    return res
}
export const deleteChat = async (chatId: string): Promise<any> => {
    const res = await request.delete(`chat/${chatId}`)
    return res
}
export const renameChat = async (chatId: string, newName: string): Promise<any> => {
    const res = await request.put(`chat/rename/${chatId}`, { newName })
    return res
}