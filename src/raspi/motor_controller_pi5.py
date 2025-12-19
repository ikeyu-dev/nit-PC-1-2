"""
モーター制御モジュール（ラズパイ5対応版）
左モーター（後輪）を制御して、手の形に応じて動作を変える
- Rock（グー）: 停止
- Paper（パー）: 後退
- Pointing_UP（人差し指）: 直進

rpi-lgpioを使用
"""
import lgpio
import time
from enum import Enum


class HandShape(Enum):
    ROCK = "Rock"
    PAPER = "Paper"
    POINTING_UP = "Pointing_UP"


class MotorController:
    def __init__(self):
        # ピン設定
        # 左モーター
        self.L_IN1 = 17  # ICの5番
        self.L_IN2 = 27  # ICの6番
        self.L_PWM = 4   # ICの4番 (Vref)

        # 右モーター
        self.R_IN1 = 23
        self.R_IN2 = 24
        self.R_PWM = 18

        # GPIOチップをオープン
        self.h = lgpio.gpiochip_open(0)

        # 左モーターのピンを出力モードに設定
        lgpio.gpio_claim_output(self.h, self.L_IN1)
        lgpio.gpio_claim_output(self.h, self.L_IN2)
        lgpio.gpio_claim_output(self.h, self.L_PWM)

        # 右モーターのピンを出力モードに設定
        lgpio.gpio_claim_output(self.h, self.R_IN1)
        lgpio.gpio_claim_output(self.h, self.R_IN2)
        lgpio.gpio_claim_output(self.h, self.R_PWM)

        # PWM設定（周波数100Hz）
        lgpio.tx_pwm(self.h, self.L_PWM, 100, 0)
        lgpio.tx_pwm(self.h, self.R_PWM, 100, 0)

        # 現在の状態
        self.current_state = None
        print("Motor controller initialized (lgpio) - Both motors")

    def stop(self):
        """停止"""
        # 左モーター停止
        lgpio.gpio_write(self.h, self.L_IN1, 0)
        lgpio.gpio_write(self.h, self.L_IN2, 0)
        lgpio.tx_pwm(self.h, self.L_PWM, 100, 0)
        # 右モーター停止
        lgpio.gpio_write(self.h, self.R_IN1, 0)
        lgpio.gpio_write(self.h, self.R_IN2, 0)
        lgpio.tx_pwm(self.h, self.R_PWM, 100, 0)
        self.current_state = "stop"
        print("Motor: STOP")

    def forward(self, speed=40):
        """
        直進（モーターは逆回転）
        speed: 0-100の速度
        """
        # 左モーター前進（逆回転）
        lgpio.gpio_write(self.h, self.L_IN1, 0)
        lgpio.gpio_write(self.h, self.L_IN2, 1)
        lgpio.tx_pwm(self.h, self.L_PWM, 100, speed)
        # 右モーター前進（逆回転）
        lgpio.gpio_write(self.h, self.R_IN1, 0)
        lgpio.gpio_write(self.h, self.R_IN2, 1)
        lgpio.tx_pwm(self.h, self.R_PWM, 100, speed)
        self.current_state = "forward"
        print(f"Motor: FORWARD (speed={speed}%)")

    def backward(self, speed=40):
        """
        後退（モーターは順回転）
        speed: 0-100の速度
        """
        # 左モーター後退（順回転）
        lgpio.gpio_write(self.h, self.L_IN1, 1)
        lgpio.gpio_write(self.h, self.L_IN2, 0)
        lgpio.tx_pwm(self.h, self.L_PWM, 100, speed)
        # 右モーター後退（順回転）
        lgpio.gpio_write(self.h, self.R_IN1, 1)
        lgpio.gpio_write(self.h, self.R_IN2, 0)
        lgpio.tx_pwm(self.h, self.R_PWM, 100, speed)
        self.current_state = "backward"
        print(f"Motor: BACKWARD (speed={speed}%)")

    def control_by_hand_shape(self, hand_shape: str):
        """
        手の形に応じてモーターを制御
        - Rock（グー）: 停止
        - Paper（パー）: 後退
        - Pointing_UP（人差し指）: 直進
        """
        try:
            shape = HandShape(hand_shape)

            if shape == HandShape.ROCK:
                self.stop()
            elif shape == HandShape.PAPER:
                self.backward()
            elif shape == HandShape.POINTING_UP:
                self.forward()

            return True
        except ValueError:
            print(f"Invalid hand shape: {hand_shape}")
            return False

    def cleanup(self):
        """リソースの解放"""
        self.stop()
        time.sleep(0.1)
        lgpio.gpiochip_close(self.h)
        print("Motor controller cleaned up")


# シングルトンインスタンス
_motor_controller = None


def get_motor_controller() -> MotorController:
    """モーターコントローラーのシングルトンインスタンスを取得"""
    global _motor_controller
    if _motor_controller is None:
        _motor_controller = MotorController()
    return _motor_controller
