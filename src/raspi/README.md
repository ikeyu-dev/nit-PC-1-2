# ラズパイ側のモーター制御API

## 概要
手の形に応じてモーターを制御するFastAPIサーバー

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. サーバーの起動
```bash
cd src/raspi
python main.py
```

サーバーは `http://0.0.0.0:8000` で起動します。

## API エンドポイント

### POST /motor/control
手の形を受け取ってモーターを制御

**リクエストボディ:**
```json
{
  "hand_shape": "Rock" | "Paper" | "Pointing_UP"
}
```

**動作:**
- `Rock`（グー）: 停止
- `Paper`（パー）: 直進
- `Pointing_UP`（人差し指）: 後退

**レスポンス:**
```json
{
  "message": "Motor controlled successfully",
  "hand_shape": "Rock",
  "motor_state": "stop"
}
```

### GET /motor/status
モーターの現在の状態を取得

**レスポンス:**
```json
{
  "motor_state": "forward"
}
```

### POST /motor/stop
モーターを停止

**レスポンス:**
```json
{
  "message": "Motor stopped",
  "motor_state": "stop"
}
```

### GET /
ルートエンドポイント（API情報）

**レスポンス:**
```json
{
  "message": "Raspi Motor Control API",
  "version": "1.0.0"
}
```

## システム構成

```
PC（手の形認識）
  ↓
  realtime_judge.py
  ↓
  http://localhost:7001/realtime/judge
  ↓
  API Router (src/api/v1/realtime_judge/realtime_judge.py)
  ↓
  http://<RASPI_IP>:8000/motor/control
  ↓
  ラズパイのFastAPIサーバー (src/raspi/main.py)
  ↓
  モーター制御 (src/raspi/motor_controller.py)
  ↓
  GPIO → モーター
```

## 環境変数

PC側のAPIサーバーで、ラズパイのIPアドレスを指定：

```bash
export RASPI_API_URL="http://192.168.1.100:8000"
```

デフォルトは `http://localhost:8000` です。

## テスト

### cURLでのテスト
```bash
# 直進
curl -X POST http://localhost:8000/motor/control \
  -H "Content-Type: application/json" \
  -d '{"hand_shape": "Paper"}'

# 後退
curl -X POST http://localhost:8000/motor/control \
  -H "Content-Type: application/json" \
  -d '{"hand_shape": "Pointing_UP"}'

# 停止
curl -X POST http://localhost:8000/motor/control \
  -H "Content-Type: application/json" \
  -d '{"hand_shape": "Rock"}'

# 状態確認
curl http://localhost:8000/motor/status

# 停止
curl -X POST http://localhost:8000/motor/stop
```

## GPIO ピン配置

### Raspberry Pi 4以前

- L_IN1: GPIO 17 (ICの5番)
- L_IN2: GPIO 27 (ICの6番)
- L_PWM: GPIO 4 (ICの4番/Vref)

### Raspberry Pi 5

- L_IN1: GPIO 17 (ICの5番)
- L_IN2: GPIO 27 (ICの6番)
- L_PWM: GPIO 4 (ICの4番/Vref)
- R_IN1: GPIO 23
- R_IN2: GPIO 24
- R_PWM: GPIO 18

## 注意事項

- このコードはラズパイ上で動作します
- GPIO制御のため、`sudo`権限が必要な場合があります
- サーバー終了時（Ctrl+C）に自動的にGPIOをクリーンアップします
