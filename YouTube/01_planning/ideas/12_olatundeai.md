# 12. @olatundeai — Google Flow で一貫した画像を一括生成するプロンプト

- 元投稿: https://x.com/olatundeai/status/2114762856189034894（2026-10-26／いいね380・ブックマーク512・表示1.8万）
- 画像: `../research/images/x-posts2/olatundeai_q0_frames.jpg`（成片）、`misc.jpg`（Flowの画面：番号付きの画像が並ぶ）
- ステータス: 📚 手法メモ

## 使っている道具
Grok（リサーチ）→ **Claude（台本）** → **Google Flow（画像の自動生成）** → Minimax（ナレーション）→ CapCut（編集・字幕）

## Flow エージェントに入れたプロンプト
> I'm going to send you numbered prompts, one at a time. For each one, generate a single 16:9 image. Keep the art style and every character's design identical across all images. Do not add captions or subtitles unless the scene names specific text. Rename each image as its number (001.png, 002.png, ...)

日本語にすると：「番号付きのプロンプトを1つずつ送ります。それぞれ16:9の画像を1枚生成してください。すべての画像で画風と登場人物のデザインを同一に保つこと。場面で特定の文字が指定されない限り、字幕や文字は入れないこと。画像のファイル名は番号にすること（001.png, 002.png…）」

## ポイント
- 1本の動画に **50枚以上** の一枚絵（ニット帽の白い棒人間、部屋・スタジオ・グラフ）。動きは最小限、カットを頻繁に切り替えて見せる
- **画風とキャラの統一を毎回指示** ＋ **番号で管理** → そのまま編集ソフトに並べられる
- このやり方は、すでにある `gemini-illustration-batch` スキル（Geminiで一括生成し {project}_{NNN}.jpg で保存）とほぼ同じ
