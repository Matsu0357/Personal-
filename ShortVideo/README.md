# ShortVideo

ショート動画（YouTube Shorts / TikTok / Instagram Reels など）の制作と、関連するチャットを管理するフォルダです。

| フォルダ | 用途 |
| --- | --- |
| `00_chats` | チャットの記録（1チャット = 1ファイル） |
| `01_planning/ideas` | ネタ・アイデアメモ |
| `01_planning/research` | リサーチ・競合調査 |
| `01_planning/scripts` | 台本・構成案 |
| `02_assets/footage` | 撮影素材・録画データ |
| `02_assets/images` | 画像素材 |
| `02_assets/audio/bgm` | BGM |
| `02_assets/audio/sfx` | 効果音 |
| `02_assets/audio/voiceover` | ナレーション |
| `03_editing/projects` | 編集プロジェクトファイル |
| `03_editing/subtitles` | 字幕ファイル（.srt など） |
| `04_thumbnails` | カバー画像・サムネイル |
| `05_exports` | 書き出し済み動画（縦型 9:16） |
| `06_publishing/metadata` | タイトル・説明文・ハッシュタグ |
| `06_publishing/schedule` | 投稿スケジュール |
| `07_analytics/reports` | 再生数・振り返り |
| `99_archive` | 公開済み・不要になったデータ |

## チャットの管理ルール

- ショート動画に関するチャットは、`00_chats/` に記録を残します。
- ファイル名は `YYYY-MM-DD_テーマ.md`（例: `2026-10-26_フォルダ作成.md`）。
- 新しいチャットは `00_chats/_template.md` をコピーして作成します。
- 一覧は `00_chats/README.md` の「チャット一覧」に1行ずつ追記します。
- チャットで作った台本・素材などは上記の各フォルダに置き、記録からリンクします。

> 空フォルダをGitで管理するため、各フォルダに `.gitkeep` を置いています。
