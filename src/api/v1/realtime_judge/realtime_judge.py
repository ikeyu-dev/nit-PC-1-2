from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix="/realtime",
    tags=["v1"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/judge",
)
async def get_realtime_judge(hand_shape: str):
    """
    手の形を受け取り、処理を行うエンドポイント
    """
    if hand_shape not in ["Rock", "Paper", "Pointing_UP"]:
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Must be Rock, Paper, or Pointing_UP, but f{hand_shape}"
            },
        )
    return JSONResponse(
        status_code=200,
        content={"message": f"Received hand shape: {hand_shape}"},
    )
