# 10. @crazykaomei — 棒人間チャンネルの「型」をAIで複製（Stickman Video Director）

- 元投稿: https://x.com/crazykaomei/status/2114908822447989026（2026-10-27／いいね209・表示1.6万）
- 画像: `../research/images/x-posts2/crazykaomei_0_frames.jpg`（成片のコマ）、`misc.jpg`（左上：Ifverse）
- ステータス: 🟢 有力（品質アップの本命）

## 内容（中国語の要約）
- YouTubeで「2週間で5.5万人」伸びた棒人間チャンネル（画像は **Ifverse**、登録者5.42万、「What If Your Reaction Time Was 10x Faster?」455万再生）を複製しようとした
- Codexでは何度やってもうまくいかなかったが、**Renoise MCP**（有料の動画生成サービス。投稿はアフィリエイト付きの宣伝）につないだら10分で完成。参考動画をアップしただけで、ナレーション・字幕も自動
- 引用元：本人が作った **「火柴人（棒人間）Skill」= Stickman Video Director** を公開。人気動画数十本から抽出した台本構成を内蔵

## 成片の見た目
- 黒い丸頭＋赤いパーカーのキャラ、**影付きの2Dイラスト背景**（街・店内・空の棚）、表情のアップ、群衆の走るカット、英語字幕
- → 今の自作（コードで描いた白い棒人間）より、背景の情報量・光・構図が段違い

## Stickman Video Director（MIT、無料）
- https://github.com/kaomei/stickman-video-director （日本語README あり）
- Claude Code で使える「Skill」。2モード：
  - **Director**：台本・絵コンテ・クリップごとの動画プロンプトを出す → 自分で Google Flow / Kling / Runway などで生成し、CapCutで編集（30秒〜3分向け）
  - **Autopilot**：テーマから **イラスト絵コンテ＋部分アニメーション＋ナレーション＋字幕＋効果音** を自動で組み立てて完成動画まで（10分以上の長編向け）
- 画風：A1 白黒（今の Inspire 型に近い）／A2 モダンポップ／A3 原始時代／A4 ほっこり日常／A5 歴史カートゥーン／B1 ミニマル手描き
- 必要なもの：画像生成のAPI（Google Gemini など）、音声合成のAPI（ElevenLabs など）の利用料のみ
