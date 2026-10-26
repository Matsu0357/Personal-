# 英語音読ショート #01「It's Okay to Start Again」（試作）

企画: `../../../01_planning/ideas/01_english_scroll.md`／競合調査: `../../../01_planning/research/english-scroll-competitors.md`

## 型（シリーズ共通）
- 縦型 1080x1920・60秒以内
- 濃紺のニューススタジオ風の背景（細い格子）＋上に赤い「● READ ALOUD」バッジ
- 英文＋和訳が下から上へ流れ、読み上げ中の行を画面中央で黄色のバーとパネルでハイライト（和訳も黄色）
- 冒頭2.6秒：「これ、声に出して読める？」のフック
- 最後3秒：「今日の表現」3つ＋「読めたら🎤とコメントしてね」
- 文字は x=90〜900 に収める（TikTok・リールの右側ボタンをよける）。下の説明文にかかる 1700px より下には何も置かない

## 作り方
```
python3 build_audio.py      # 音声 → build/audio.wav, build/timeline.json
node render.js --preview 1,10,47   # 確認用の静止画
node render.js              # build/video.mp4
node render.js --thumb      # build/cover.png
```
- フォント（`assets/NotoSansJP.ttf`, `assets/Inter.ttf`）は Git に入れていない。Google Fonts から同じ名前で置く
- 台本は `script.json`。行は `{"en", "ja"}`、`words` が最後の「今日の表現」

## 音声（FishAudio）
- `script.json` の `voice.fish_reference_id` に FishAudio の声のID（モデルID）を入れ、`FISH_AUDIO_API_KEY` を設定して `python3 build_audio.py` を実行すると FishAudio で読み上げる
- 使うモデルは `FISH_AUDIO_MODEL`（既定 `s1`）。API の仕様が変わっていたら `tts_fish()` を直す
- 今の書き出し（v1）は **試作用に edge-tts の英語音声（en-US-AriaNeural）** を使っている。公開前に FishAudio で作り直す
- 声の選び方：はっきり・ややゆっくりの北米英語、ニュースキャスター風。速すぎたら FishAudio 側の速度か、`build_audio.py` の `gap_line` で調整

## 本番前にやること
- [ ] FishAudio の声を決めて作り直す（商用利用できるプランか確認）
- [ ] 英文・和訳をネイティブ／英語の得意な人に一度見てもらう
