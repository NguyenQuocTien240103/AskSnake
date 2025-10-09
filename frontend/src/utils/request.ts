// import axios from 'axios'
// // import Cookies from 'js-cookie'

// const request = axios.create({
//     baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
//     headers: {'X-Custom-Header': 'foobar'},
//     withCredentials: true
// });


// // Add a request interceptor    
// request.interceptors.request.use(function (config) {
//     // Do something before request is sent
//     return config;
// }, function (error) {
// // Do something with request error
//     return Promise.reject(error);
// });

// // Add a response interceptor
// request.interceptors.response.use(function (response) {
//     // Any status code that lie within the range of 2xx cause this function to trigger
//     // Do something with response data
//     return response;
// }, async function  (error) {
// // Any status codes that falls outside the range of 2xx cause this function to trigger
// // Do something with response error
//     const originalRequest = error.config;

//     if (error.response?.status === 401) {

//         if (error.config.url?.includes('login') || error.config.url?.includes('register')) {
//             return Promise.reject(error); 
//         }

//         originalRequest._retry = true;

//         try {
//             console.log("abccccc")
//             const res = await request.post("/refresh-token");
//             return request(originalRequest);
//         } catch (error) {
//             console.error("Refresh token expired. Redirecting to login...");
//             window.alert("session is expired")
//             // window.location.href = '/login';
//         }

//     }
//     // try {
//     //     console.log("abccccc")
//     //     const res = await request.post("auth/refresh-token");
//     //     return request(originalRequest);
//     // } catch (error) {
//     //     console.error("Refresh token expired. Redirecting to login...");
//     //     window.alert("session is expired")
//     //     // window.location.href = '/login';
//     // }

//     return Promise.reject(error);
// });

// export default request;




import axios from 'axios';

export function createAxiosInstance(cookie?: string) {
  return axios.create({
    baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
    headers: {
      'X-Custom-Header': 'foobar',
      ...(cookie ? { cookie } : {}),
    },
    withCredentials: true,
  });
}


export function setupInterceptors(instance: ReturnType<typeof createAxiosInstance>) {
    instance.interceptors.response.use(
      response => response,
      async error => {
        const originalRequest = error.config;
  
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
  
          try {
            // Gọi API refresh token, cookie đã được gắn sẵn trong header
            await instance.post('auth/refresh-token');
            // retry request ban đầu
            return instance(originalRequest);
          } catch (refreshError) {
            console.error("Refresh token expired. Redirecting to login...");
            throw refreshError;
          }
        }        
        return Promise.reject(error);
      }
    );
  }
  