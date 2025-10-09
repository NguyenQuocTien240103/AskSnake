// import request from '@/utils/request'

// type LoginType = {
//     email: string,
//     password: string,
// }

// type RegisterType = {
//     email: string, 
//     password: string,
//     confirm_password: string,
// }

// export const login = async ({email, password} : LoginType): Promise<any> => {
//     const res = await request.post('auth/login',{
//         email,
//         password,
//     })
//     return res
// }


// export const register = async ({email, password, confirm_password} : RegisterType): Promise<any> => {
//     const res = await request.post('auth/register',{
//         email,
//         password,
//         confirm_password
//     })
//     return res
// }

// export const logout = async (): Promise<any> => {
//     const res = await request.get('auth/logout')
//     return res
// }


import {createAxiosInstance, setupInterceptors } from '@/utils/request'

type LoginType = {
    email: string,
    password: string,
}

type RegisterType = {
    email: string, 
    password: string,
    confirm_password: string,
}

export const login = async ({email, password} : LoginType): Promise<any> => {
    const request = createAxiosInstance();
    const res = await request.post('auth/login',{
        email,
        password,
    })
    return res
}


export const register = async ({email, password, confirm_password} : RegisterType): Promise<any> => {
    const request = createAxiosInstance();
    const res = await request.post('auth/register',{
        email,
        password,
        confirm_password
    })
    return res
}

export const logout = async (): Promise<any> => {
    const request = createAxiosInstance();
    const res = await request.get('auth/logout')
    return res
}