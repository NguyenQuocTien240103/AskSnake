from fastapi import APIRouter, HTTPException, status
from pydantics.user import UserLogin, UserRegister  
from services.AuthService import AuthService

app_router = APIRouter()

@app_router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: UserLogin):
    user_dict = user.dict()
    try:
        access_token = await AuthService.get_access_token(user_dict['email'], user_dict['password'])
        return access_token
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