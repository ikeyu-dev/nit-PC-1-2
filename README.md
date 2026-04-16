# 木曜 6 限 フィジカルコンピューティング工房 Ⅱ

## プロダクトについて

### テーマ

手の動きを使って，車を動かす．

Webカメラで手の形をリアルタイムに認識し、その形に応じてRaspberry Piで制御される車を動かすシステムです。

### 使用技術

-   **FastAPI**: RESTful APIサーバーの構築
-   **TensorFlow**: 手の形を分類する機械学習モデル
-   **Raspberry Pi**: モーター制御用のマイコンボード
-   **MediaPipe**: 手の骨格検出（ランドマーク抽出）
-   **OpenCV**: カメラ映像の取得と画像処理
-   **Docker**: 開発環境のコンテナ化

## システム構成

```
┌─────────────────────────────────────────────────────────────┐
│ PC (手の形認識システム)                                      │
│                                                             │
│  [Webカメラ]                                                 │
│      ↓                                                      │
│  [OpenCV + MediaPipe]  ← 手の骨格検出                        │
│      ↓                                                      │
│  [TensorFlow Model]    ← 手の形分類 (Rock/Paper/Pointing_UP) │
│      ↓                                                      │
│  [realtime_judge.py]   ← リアルタイム判別スクリプト           │
│      ↓                                                      │
│  HTTP Request                                               │
└──────┼──────────────────────────────────────────────────────┘
       │
       │ GET http://localhost:7001/realtime/judge?hand_shape={shape}
       │
┌──────▼──────────────────────────────────────────────────────┐
│ FastAPI Server (Docker)                                     │
│                                                             │
│  [src/api/main.py]                                          │
│      ↓                                                      │
│  [realtime_judge router]                                    │
│      ↓                                                      │
│  HTTP Request (httpx)                                       │
└──────┼──────────────────────────────────────────────────────┘
       │
       │ POST http://<RASPI_IP>:8000/motor/control
       │
┌──────▼──────────────────────────────────────────────────────┐
│ Raspberry Pi (モーター制御)                                  │
│                                                             │
│  [src/raspi/main.py]      ← FastAPIサーバー                  │
│      ↓                                                      │
│  [motor_controller.py]    ← モーター制御ロジック              │
│      ↓                                                      │
│  [RPi.GPIO]               ← GPIO制御                         │
│      ↓                                                      │
│  [モータードライバIC]       ← L298Nなど                       │
│      ↓                                                      │
│  [DCモーター] → 車の動作                                      │
└─────────────────────────────────────────────────────────────┘
```

## 機能

### 手の形と動作の対応

| 手の形 | クラス名 | 動作 |
|--------|---------|------|
| グー | Rock | 停止 |
| パー | Paper | 直進 |
| 人差し指を立てる | Pointing_UP | 後退 |

### 主要コンポーネント

#### 1. 手の形認識 (Deep Learning)

- **学習データ収集**: [src/deep-learning/collect.py](src/deep-learning/collect.py)
  - MediaPipeで手のランドマーク（21点の座標）を抽出
  - 各手の形ごとにデータを収集

- **モデル学習**: [src/deep-learning/model.py](src/deep-learning/model.py)
  - TensorFlowを使用した3クラス分類モデル
  - 入力: 21個のランドマークのx, y, z座標（63次元）
  - 出力: Rock, Paper, Pointing_UPの確率

- **リアルタイム判別**: [src/deep-learning/realtime_judge.py](src/deep-learning/realtime_judge.py)
  - Webカメラから映像を取得
  - MediaPipeで手を検出
  - 学習済みモデルで手の形を分類
  - 0.1秒ごとにAPIサーバーへリクエスト送信

#### 2. APIサーバー (FastAPI)

- **メインアプリケーション**: [src/api/main.py](src/api/main.py)
  - FastAPIアプリケーションの起動
  - ルーターの登録

- **リアルタイム判別ルーター**: [src/api/v1/realtime_judge/realtime_judge.py](src/api/v1/realtime_judge/realtime_judge.py)
  - エンドポイント: `GET /realtime/judge?hand_shape={shape}`
  - 手の形のバリデーション
  - Raspberry PiのAPIへHTTPリクエスト転送（httpx使用）
  - タイムアウト・エラーハンドリング

#### 3. Raspberry Pi モーター制御

- **FastAPIサーバー**: [src/raspi/main.py](src/raspi/main.py)
  - エンドポイント:
    - `POST /motor/control`: 手の形に応じてモーター制御
    - `GET /motor/status`: モーターの状態取得
    - `POST /motor/stop`: モーター停止

- **モーター制御ロジック**: [src/raspi/motor_controller.py](src/raspi/motor_controller.py)
  - RPi.GPIOを使用したPWM制御
  - GPIO 17, 27, 4を使用
  - forward(), backward(), stop()メソッド

- **Raspberry Pi 5対応**: [src/raspi/motor_controller_pi5.py](src/raspi/motor_controller_pi5.py)
  - lgpioライブラリを使用
  - Raspberry Pi 5の新しいGPIOシステムに対応
  - 左モーター: GPIO 17, 27, 4 / 右モーター: GPIO 23, 24, 18を使用

## 起動方法

### Raspberry Pi側

```bash
# raspiディレクトリに移動
cd ~/raspi

# 仮想環境の作成（初回のみ）
python3 -m venv venv --system-site-packages

# 仮想環境の有効化
source venv/bin/activate

# 依存関係のインストール（初回のみ）
sudo apt-get install python3-lgpio
pip install fastapi uvicorn

# サーバーの起動
python main.py
```

サーバーは `http://0.0.0.0:8000` で起動します。

### PC側

**ターミナル1: APIサーバー（Docker使用）**

```bash
# .envファイルを作成（初回のみ）
cp .env.example .env
# .envファイルを編集して<RASPI_IP>を実際のIPアドレスに変更

# Dockerコンテナのビルドと起動
docker-compose up --build
```

または、Dockerを使わない場合:

```bash
source venv/bin/activate
RASPI_API_URL="http://<RASPI_IP>:8000" uvicorn src.api.main:app --host 0.0.0.0 --port 7001 --reload
```

APIサーバーは `http://localhost:7001` で起動します。

**ターミナル2: 手の形認識プログラム**

```bash
source venv/bin/activate
python src/deep-learning/realtime_judge.py
```

カメラウィンドウが表示され、手の形を認識します。終了するには `q` キーを押してください。

## セットアップ（初回のみ）

### PC側

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### Raspberry Pi側

```bash
# raspiディレクトリを作成（またはSCPで転送）
mkdir -p ~/raspi
# PCからファイルを転送
scp -r src/raspi/* <USER>@<RASPI_IP>:~/raspi/

# ラズパイ側での初期設定は「起動方法」を参照
```

## 技術詳細

### MediaPipeによる手の検出

MediaPipeは手の21個のランドマーク（関節点）を検出します：
- 各ランドマークは3次元座標（x, y, z）を持つ
- 本システムではx, y, z座標を使用（63次元ベクトル）
- 検出精度が高く、リアルタイム処理が可能

### TensorFlowモデルの構造

- 入力層: 63次元（21ランドマーク × 3座標）
- 隠れ層: 全結合層（Dense）
- 出力層: 3クラス（Softmax活性化関数）
- 学習済みモデル: `src/deep-learning/model/hand_model.keras`

### FastAPIの非同期通信

- httpxライブラリで非同期HTTPリクエスト
- タイムアウト: 2秒
- エラー時もレスポンスを返す（警告メッセージ付き）

### GPIO制御

**Raspberry Pi 4以前:**
- RPi.GPIOライブラリ使用
- BCMモードでピン番号指定
- PWM周波数: 100Hz

**Raspberry Pi 5:**
- lgpioライブラリ使用
- 新しいGPIOシステム（RP1チップ）に対応
- PWM周波数: 100Hz

## 開発環境

- Python 3.12
- Docker & Docker Compose
- Raspberry Pi OS (Bookworm推奨)

## ライセンス

MIT License
