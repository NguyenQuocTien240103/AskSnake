import request from '@/utils/request'

export const getAllHistoryPredict = async (): Promise<any> => {
    const res = await request.get('history_pre/all_history')
    return res
}
export const getDetailHistoryPredict = async (label: string): Promise<any> => {
    const res = await request.get(`history_pre/detail_history`,{
        params: { label }
    })
    return res
}