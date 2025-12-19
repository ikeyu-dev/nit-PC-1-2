"""
モーター制御モジュール
左モーター（後輪）を制御して、手の形に応じて動作を変える
- Rock（グー）: グー → stop() が呼ばれる → 車は停止
- Paper（パー）: パー → forward() が呼ばれる → モーターが順回転 → 車は直進
- Pointing_UP（人差し指）: 人差し指 → backward() が呼ばれる → モーターが逆回転 → 車は後退

ラズパイ5対応: rpi-lgpioを使用
"""
try:
    import RPi.GPIO as GPIO
    GPIO_LIB = "RPi.GPIO"
except (ImportError, RuntimeError):
    # ラズパイ5の場合、rpi-lgpioを使用
    import lgpio as GPIO
    GPIO_LIB = "lgpio"
    print("Using lgpio for Raspberry Pi 5")

import time
from enum import Enum


class HandShape(Enum):
    ROCK = "Rock"
    PAPER = "Paper"
    POINTING_UP = "Pointing_UP"


class MotorController:
    def __init__(self):
        # ピン設定
        self.L_IN1 = 17  # ICの5番
        self.L_IN2 = 27  # ICの6番
        self.L_PWM = 4   # ICの4番 (Vref)

        # GPIO設定
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # ピンの準備
        GPIO.setup(self.L_IN1, GPIO.OUT)
        GPIO.setup(self.L_IN2, GPIO.OUT)
        GPIO.setup(self.L_PWM, GPIO.OUT)

        # PWM設定（周波数100Hz）
        self.pwm_left = GPIO.PWM(self.L_PWM, 100)
        self.pwm_left.start(0)

        # 現在の状態
        self.current_state = None

    def stop(self):
        """
        停止
        グー → stop() が呼ばれる → 車は停止
        """
        GPIO.output(self.L_IN1, GPIO.LOW)
        GPIO.output(self.L_IN2, GPIO.LOW)
        self.pwm_left.ChangeDutyCycle(0)
        self.current_state = "stop"
        print("Motor: STOP")

    def forward(self, speed=40):
        """
        直進
        パー → forward() が呼ばれる → モーターが順回転 → 車は直進
        speed: 0-100の速度
        """
        GPIO.output(self.L_IN1, GPIO.HIGH)
        GPIO.output(self.L_IN2, GPIO.LOW)
        self.pwm_left.ChangeDutyCycle(speed)
        self.current_state = "forward"
        print(f"Motor: FORWARD (speed={speed}%)")

    def backward(self, speed=40):
        """
        後退
        人差し指 → backward() が呼ばれる → モーターが逆回転 → 車は後退
        speed: 0-100の速度
        """
        GPIO.output(self.L_IN1, GPIO.LOW)
        GPIO.output(self.L_IN2, GPIO.HIGH)
        self.pwm_left.ChangeDutyCycle(speed)
        self.current_state = "backward"
        print(f"Motor: BACKWARD (speed={speed}%)")

    def control_by_hand_shape(self, hand_shape: str):
        """
        手の形に応じてモーターを制御
        - Rock（グー）: グー → stop() が呼ばれる → 車は停止
        - Paper（パー）: パー → forward() が呼ばれる → モーターが順回転 → 車は直進
        - Pointing_UP（人差し指）: 人差し指 → backward() が呼ばれる → モーターが逆回転 → 車は後退
        """
        try:
            shape = HandShape(hand_shape)

            if shape == HandShape.ROCK:
                self.stop()
            elif shape == HandShape.PAPER:
                self.forward()
            elif shape == HandShape.POINTING_UP:
                self.backward()

            return True
        except ValueError:
            print(f"Invalid hand shape: {hand_shape}")
            return False

    def cleanup(self):
        """リソースの解放"""
        self.stop()
        time.sleep(0.1)
        self.pwm_left.stop()
        GPIO.cleanup()
        print("Motor controller cleaned up")


# シングルトンインスタンス
_motor_controller = None


def get_motor_controller() -> MotorController:
    """モーターコントローラーのシングルトンインスタンスを取得"""
    global _motor_controller
    if _motor_controller is None:
        _motor_controller = MotorController()
    return _motor_controller
