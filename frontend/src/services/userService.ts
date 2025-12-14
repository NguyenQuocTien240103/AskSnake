import request from '@/utils/request'

export const getUserCurrent = async (): Promise<any> => {
    const res = await request.get('user/me')
    return res
}
export const getUsers = async (page: number, limit: number = 10): Promise<any> => {
    const res = await request.get('user/users',{
        params: { page, limit }
    })
    return res
}