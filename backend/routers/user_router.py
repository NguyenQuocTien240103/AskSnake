from pydantics.user import UserBase  
from fastapi import APIRouter, HTTPException, status, Annotated
from services.UserService import UserService

app_router = APIRouter()

@app_router.get("/me",status_code=status.HTTP_200_OK)
async def get_users_me(current_user: Annotated[UserBase, Depends(UserService.get_current_user)]):
    try:
        return current_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")