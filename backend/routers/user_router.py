from pydantics.user import UserBase  
from fastapi import APIRouter, HTTPException, Depends, status, Query
from services.UserService import UserService
from typing import Annotated  
from pydantics.user import UserBase, UserRole

app_router = APIRouter()

@app_router.get("/me",status_code=status.HTTP_200_OK)
async def get_users_me(current_user: Annotated[dict, Depends(UserService.get_current_user)]):
    try:
        # print(current_user)
        # return UserBase(email=current_user['email'])
        return UserRole(email=current_user['email'], role=current_user['role'])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@app_router.get("/users",status_code=status.HTTP_200_OK)
async def get_users(current_user: Annotated[dict, Depends(UserService.get_current_user)], page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    user_id = current_user['_id']
    role = current_user['role']
    if role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")
    try:
        result = await UserService.get_users(page, limit)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")