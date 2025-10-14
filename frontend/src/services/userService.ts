import request from '@/utils/request'

export const getUserCurrent = async (): Promise<any> => {
    const res = await request.get('user/me')
    return res
}
