# 英語音読ショート「中級英語リーディング」制作フォルダ

| 回 | タイトル | 台本データ | 書き出し |
| --- | --- | --- | --- |
| #01 | It's Okay to Start Again | `episodes/01.json` | `05_exports/english_scroll_01_v4.mp4`（82.7秒） |
| #02 | The Power of Saying "No" | `episodes/02.json` | `05_exports/english_scroll_02_v2.mp4`（80.1秒） |

企画: `../../../01_planning/ideas/01_english_scroll.md`／競合調査: `../../../01_planning/research/english-scroll-competitors.md`

## 型（シリーズ共通）
収益化の設計: `../../../01_planning/plans/tiktok-monetization.md`
- 縦型 1080x1920・**1分以上（約80秒）**。TikTok の Creator Rewards Program は1分以上の動画だけが対象
- 構成: フック → ① 通し読み → ② リピート練習（台本の `repeat` に書いた3文を「🎧 LISTEN → あなたの番 🎤」）→ ③ 今日の表現
- 濃紺のニューススタジオ風の背景（細い格子）＋上に赤い「● READ ALOUD」バッジ
- 英文＋和訳が下から上へ流れ、読み上げ中の行を画面中央で黄色のバーとパネルでハイライト（和訳も黄色）
- 冒頭2.6秒：「これ、声に出して読める？」のフック
- リピート練習：「あなたの番」の間は文の長さ＋0.5秒。始まりに合図の音
- 最後3秒：「今日の表現」3つ＋「読めたら🎤とコメントしてね」
- 文字は x=90〜900 に収める（TikTok・リールの右側ボタンをよける）。下の説明文にかかる 1700px より下には何も置かない

## 作り方
```
python3 build_audio.py 02           # 音声 → build_02/audio.wav, build_02/timeline.json
node render.js 02 --preview 1,10,47  # 確認用の静止画
node render.js 02                    # build_02/video.mp4
node render.js 02 --thumb            # build_02/cover.png
```
- フォント（`assets/NotoSansJP.ttf`, `assets/Inter.ttf`）は Git に入れていない。Google Fonts から同じ名前で置く
- 台本は `episodes/XX.json`（新しい回は前の回をコピーして書きかえる）。行は `{"en", "ja"}`、`words` が最後の「今日の表現」

## 音声（FishAudio）
- 声: `933563129e564b19a115bedd57b7406a`（各回の台本の `voice.fish_reference_id`）
- APIキーは**リポジトリに入れない**。クラウド環境の設定（ネットワークシークレット、なければ環境変数 `FISH_AUDIO_API_KEY`）に保存する。自分のPCで作るときは `export FISH_AUDIO_API_KEY=...` してから `python3 build_audio.py`
- キーが使えないときは警告を出して edge-tts で作る
- 使うモデルは `FISH_AUDIO_MODEL`（既定 `s1`）。API の仕様が変わっていたら `tts_fish()` を直す
- v1 は試作用の edge-tts 音声。**v2 から FishAudio**
- 速さは `voice.fish_speed`（0.8）。そのままだと約220語/分で中級には速いので、少し落としている。行間は `build_audio.py` の `gap_line`

## 本番前にやること
- [x] FishAudio の声を決めて作り直す（v2）
- [x] FishAudio が商用利用できるプランか確認（商用プラン契約済み）
- [ ] 英文・和訳をネイティブ／英語の得意な人に一度見てもらう
