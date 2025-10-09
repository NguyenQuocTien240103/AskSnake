// import request from '@/utils/request'

// export const getUserCurrent = async (token: string): Promise<any> => {
//     const res = await request.get('user/me',{
//         headers:{
//             Cookie: `access_token=${token}`,
//         }
//     })
//     return res
// }


import {createAxiosInstance, setupInterceptors } from '@/utils/request'


export const getUserCurrent = async (token: string): Promise<any> => {
    console.log(token)
    const request = createAxiosInstance(token);
    setupInterceptors(request);
    // const res = await request.get('user/me',{
    //     headers:{
    //         Cookie: `access_token=${token}`,
    //     }
    // })

    const res = await request.get('user/me')
    return res
}
