from pydantics.user import UserBase  
from fastapi import APIRouter, HTTPException, Depends, status
from services.UserService import UserService
from typing import Annotated  
from pydantics.user import UserBase

app_router = APIRouter()

@app_router.get("/me",status_code=status.HTTP_200_OK)
async def get_users_me(current_user: Annotated[dict, Depends(UserService.get_current_user)]):
    try:
        # print(current_user)
        return UserBase(email=current_user['email'])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")