from fastapi import APIRouter, HTTPException, status, Response, Depends, UploadFile, File, Form
from pydantics.user import UserLogin, UserRegister, UserUpdatePassword  
from pydantics.token import AccessToken
from services.AuthService import AuthService
from services.UserService import UserService
from typing import Annotated
app_router = APIRouter()

@app_router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: UserLogin, response: Response):
    user_dict = user.dict()
    try:
        token = await AuthService.get_token(user_dict['email'], user_dict['password'])
        response.set_cookie(key="access_token", value=token.access_token, httponly=True)
        response.set_cookie(key="refresh_token", value=token.refresh_token, httponly=True)
        return {"message": "Login successful", "access_token": token.access_token, "refresh_token": token.refresh_token}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@app_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    user_dict = user.dict()
    try:
        await AuthService.register_user(user_dict['email'], user_dict['password'])
        return {"message": "User registered successfully"}
    except HTTPException as e:  
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@app_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, token: Annotated[str, Depends(AuthService.verify_refresh_token)]):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logout successful"}

@app_router.post("/update-password", status_code=status.HTTP_201_CREATED)
async def update_password(payload: UserUpdatePassword, current_user: Annotated[dict, Depends(UserService.get_current_user)]):
    payload_dict = payload.dict()
    old_password = payload_dict['old_password']
    new_password = payload_dict['new_password']
    try:
        await AuthService.update_password(current_user,old_password,new_password)
        return {"message": "Your password has been updated successfully!"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@app_router.post("/refresh-token", status_code=status.HTTP_200_OK)
async def get_new_access_token(response: Response, token: Annotated[AccessToken, Depends(AuthService.get_access_token)]):
    response.set_cookie(key="access_token", value = token.access_token, httponly=True)
    return {"message":  "Access token refreshed", "access_token": token.access_token}
