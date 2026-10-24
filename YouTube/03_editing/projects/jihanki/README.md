# 試作1本目：もし自販機の「あたり」が3回連続で出たら…4本目は絶対に押すな

参考: `../../../01_planning/ideas/04_ryker_strategy.md`（Bradikinin型）

## コンセプト
- 型：身近なもの（自販機）× 期待を一つだけ裏切る（あたりが3回）× ルールで仕組みを明かしていく
- 結末を先に決めた：**語り手は自販機の中にいる**。4本目を押した人は中の人と交代する。「あたり」は交代要員の募集
- 見た目：画像生成AIは使わず、**すべてコード（Canvas）で描いたアニメーション**。黒・白・赤＋自販機の青白い光
- 長さ：4分13秒

## ファイル
| ファイル | 内容 |
| --- | --- |
| `script.json` | 台本（シーン・ナレーション・大きな文字）。**ここを書き換えれば別の話になる** |
| `build_audio.py` | 台本 → ナレーション音声（1行ずつ）→ `build/timeline.json` と効果音入りの `build/audio.wav` |
| `render.html` | シーンごとの絵（Canvasで描画）。`renderFrame(t)` で t 秒目を描く |
| `render.js` | Playwrightで1コマずつ描いて、ffmpegで `build/video.mp4` にする。`--preview` `--thumb` もあり |
| `metadata.md` | タイトル案・説明文・設定 |

## 作り直し方
```bash
# フォント（初回のみ。Google FontsのNoto Sans JP）
mkdir -p assets && for w in 500 900; do
  u=$(curl -sS "https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@$w" | grep -o 'https://[^)]*' | head -1)
  curl -sS -o assets/NotoSansJP-$w.ttf "$u"; done
pip install edge-tts
python3 build_audio.py        # 音声（約1分）
node render.js --preview 30   # 確認用の画像
node render.js                # 動画（約10〜15分）
node render.js --thumb        # サムネイル
```

## 本番で変えること
- **ナレーションの音声**：今は試作用に edge-tts（Microsoft Edgeの読み上げ）を使用。これは非公式の使い方なので、収益化する動画では **VOICEVOX（クレジット表記）・Azure の公式TTS・ElevenLabs** などライセンスがはっきりしたものに替える
- BGM：今は合成した環境音のみ。著作権フリーのBGMを足すと雰囲気が上がる
