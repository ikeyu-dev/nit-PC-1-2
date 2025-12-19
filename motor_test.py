import time
import RPi.GPIO as GPIO

# --- ピン設定（基板の配線に合わせて変更） ---
# 左モーター
L_IN1 = 17  # ICの5番
L_IN2 = 27  # ICの6番
L_PWM = 4  # ICの4番 (Vref)

# 右モーター（配線した番号を入れてください）
R_IN1 = 23
R_IN2 = 24
R_PWM = 18

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# ピンの準備
GPIO.setup(L_IN1, GPIO.OUT)
GPIO.setup(L_IN2, GPIO.OUT)
GPIO.setup(L_PWM, GPIO.OUT)
GPIO.setup(R_IN1, GPIO.OUT)
GPIO.setup(R_IN2, GPIO.OUT)
GPIO.setup(R_PWM, GPIO.OUT)

# PWM（速度制御）の準備：周波数100Hz
pwm_left = GPIO.PWM(L_PWM, 100)
pwn_right = GPIO.PWM(R_PWM, 100)
pwm_left.start(0)  # 最初は速度0で待機
pwn_right.start(0)

print("GO: Forward")
# 前進の設定（IN1=HIGH, IN2=LOW）
GPIO.output(L_IN1, GPIO.HIGH)
GPIO.output(R_IN1, GPIO.HIGH)
GPIO.output(L_IN2, GPIO.LOW)
GPIO.output(R_IN2, GPIO.LOW)
# 速度を100%にする（これをしないと動きません）
pwm_left.ChangeDutyCycle(40)
pwn_right.ChangeDutyCycle(40)
time.sleep(2)

print("Slow Down")
# 速度を50%に落とす
pwm_left.ChangeDutyCycle(20)
pwn_right.ChangeDutyCycle(20)
time.sleep(2)

print("Brake")
# ブレーキ（両方HIGH）
GPIO.output(L_IN1, GPIO.HIGH)
GPIO.output(L_IN2, GPIO.HIGH)
GPIO.output(R_IN1, GPIO.HIGH)
GPIO.output(R_IN2, GPIO.HIGH)
time.sleep(1)

print("Back")
# 後退（IN1=LOW, IN2=HIGH）
GPIO.output(L_IN1, GPIO.LOW)
GPIO.output(R_IN1, GPIO.LOW)
GPIO.output(L_IN2, GPIO.HIGH)
GPIO.output(R_IN2, GPIO.HIGH)
# 速度100%
pwm_left.ChangeDutyCycle(40)
pwn_right.ChangeDutyCycle(40)
time.sleep(2)

print("Stop")
# 停止（両方LOW）& PWM停止
GPIO.output(L_IN1, GPIO.LOW)
GPIO.output(R_IN1, GPIO.LOW)
GPIO.output(L_IN2, GPIO.LOW)
GPIO.output(R_IN2, GPIO.LOW)
pwm_left.ChangeDutyCycle(0)
pwn_right.ChangeDutyCycle(0)

# 終了処理
pwm_left.ChangeDutyCycle(0)
pwn_right.ChangeDutyCycle(0)
time.sleep(0.1)  # PWM停止を待つ
pwm_left.stop()
pwn_right.stop()
time.sleep(0.1)  # 完全に停止を待つ
GPIO.cleanup()
