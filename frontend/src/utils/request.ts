import axios from 'axios'

const request = axios.create({
    baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
    headers: {'X-Custom-Header': 'foobar'},
    withCredentials: true
});


// Add a request interceptor    
request.interceptors.request.use(function (config) {
    // Do something before request is sent
    return config;
}, function (error) {
// Do something with request error
    return Promise.reject(error);
});

// Add a response interceptor
request.interceptors.response.use(function (response) {
    // Any status code that lie within the range of 2xx cause this function to trigger
    // Do something with response data
    return response;
}, async function  (error) {
// Any status codes that falls outside the range of 2xx cause this function to trigger
// Do something with response error
    const originalRequest = error.config;

    if (error.response?.status === 401) {

        if (error.config.url?.includes('login') || 
            error.config.url?.includes('register') || 
            error.config.url?.includes('refresh-token') ||
            originalRequest._retry) {
            return Promise.reject(error); 
        }

        originalRequest._retry = true;

        try {
            await request.post("/auth/refresh-token");
            return request(originalRequest);
        } catch (refreshError) {
            console.error("Refresh token expired. Redirecting to login...");
            // window.alert("session is expired")
            // window.location.href = '/login';
            return Promise.reject(refreshError);
        }

    }

    return Promise.reject(error);
});

export default request;