"""
ラズパイ側のFastAPIサーバー
手の形を受け取ってモーターを制御する
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import signal
import sys

# ラズパイ5用のモーターコントローラーをインポート
try:
    from motor_controller_pi5 import get_motor_controller
    print("Using Raspberry Pi 5 motor controller")
except ImportError:
    from motor_controller import get_motor_controller
    print("Using standard motor controller")

app = FastAPI(title="Raspi Motor Control API")

# モーターコントローラーの初期化
motor = get_motor_controller()


class HandShapeRequest(BaseModel):
    hand_shape: str


@app.post("/motor/control")
async def control_motor(request: HandShapeRequest):
    """
    手の形を受け取ってモーターを制御
    - Rock（グー）: 停止
    - Paper（パー）: 直進
    - Pointing_UP（人差し指）: 後退
    """
    hand_shape = request.hand_shape

    if hand_shape not in ["Rock", "Paper", "Pointing_UP"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid hand_shape: {hand_shape}. Must be Rock, Paper, or Pointing_UP"
        )

    success = motor.control_by_hand_shape(hand_shape)

    if success:
        return JSONResponse(
            status_code=200,
            content={
                "message": "Motor controlled successfully",
                "hand_shape": hand_shape,
                "motor_state": motor.current_state
            }
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to control motor"
        )


@app.get("/motor/status")
async def get_motor_status():
    """モーターの現在の状態を取得"""
    return {
        "motor_state": motor.current_state
    }


@app.post("/motor/stop")
async def stop_motor():
    """モーターを停止"""
    motor.stop()
    return {
        "message": "Motor stopped",
        "motor_state": motor.current_state
    }


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Raspi Motor Control API",
        "version": "1.0.0"
    }


def cleanup_handler(signum, frame):
    """シグナルハンドラー：終了時のクリーンアップ"""
    print("\nShutting down...")
    motor.cleanup()
    sys.exit(0)


# シグナルハンドラーの登録
signal.signal(signal.SIGINT, cleanup_handler)
signal.signal(signal.SIGTERM, cleanup_handler)


if __name__ == "__main__":
    import uvicorn
    print("Starting Raspi Motor Control API on port 8000...")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        motor.cleanup()
