from fastapi import APIRouter, HTTPException, Depends, status, Query
from services.UserService import UserService
from services.HistoryPredict import HistoryPredictService
from typing import Annotated  
from pydantics.user import UserBase, UserRole

app_router = APIRouter()

@app_router.get("/all_history",status_code=status.HTTP_200_OK)
async def get_users_me(current_user: Annotated[dict, Depends(UserService.get_current_user)]):
    role = current_user['role']
    if role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden: Admins only")
    try:
        result = await HistoryPredictService.get_all_history_predict()
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@app_router.get("/detail_history",status_code=status.HTTP_200_OK)
async def get_users_me(current_user: Annotated[dict, Depends(UserService.get_current_user)], label: str = Query(..., description="Label of the history to retrieve")):
    role = current_user['role']
    if role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden: Admins only")
    try:
        result = await HistoryPredictService.get_detail_history_predict(label)
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")