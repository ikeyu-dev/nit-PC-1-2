from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import httpx
import os

valid_hand_shapes = {"Rock", "Paper", "Pointing_UP"}

router = APIRouter(
    prefix="/realtime",
    tags=["v1"],
    responses={404: {"description": "Not found"}},
)

# ラズパイのAPIエンドポイント（環境変数から取得、デフォルトはlocalhost）
RASPI_API_URL = os.getenv("RASPI_API_URL", "http://localhost:8000")


@router.get(
    "/judge",
)
async def get_realtime_judge(hand_shape: str):
    """
    手の形を受け取り、ラズパイのAPIに送信するエンドポイント
    """
    if hand_shape not in valid_hand_shapes:
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Must be Rock, Paper, or Pointing_UP, but got {hand_shape}"
            },
        )

    # ラズパイのAPIに手の形を送信
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.post(
                f"{RASPI_API_URL}/motor/control",
                json={"hand_shape": hand_shape}
            )

            if response.status_code == 200:
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": f"Received hand shape: {hand_shape}",
                        "raspi_response": response.json()
                    },
                )
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "message": f"Raspi API error: {response.status_code}",
                        "detail": response.text
                    },
                )
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Received hand shape: {hand_shape}",
                "warning": "Raspi API timeout (continuing anyway)"
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Received hand shape: {hand_shape}",
                "warning": f"Could not connect to Raspi API: {str(e)}"
            },
        )
