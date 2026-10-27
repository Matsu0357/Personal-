# パソコンの Claude Code に貼り付ける作業指示

パソコンのターミナルで動いている Claude Code に、下の枠の中をそのまま貼り付けてください。
ブラウザを操作するには、事前に Chrome 拡張機能「Claude in Chrome」を入れ、Claude Code で `/chrome` を実行して接続しておきます。

```
TikTok アカウント「1分でわかる時計史」のプロフィール設定と予約投稿を、Chrome を操作して手伝ってください。

準備:
- GitHub の matsu0357/personal- リポジトリの claude/sleepy-gauss-u5p218 ブランチを、まだなければホームフォルダに clone してください（あれば pull）。
- 使うファイルは watch-channel/tiktok/README.md（手順とプロフィール文）、watch-channel/tiktok/icon.png、watch-channel/tiktok/schedule.csv、watch-channel/videos/*.mp4 です。まず README.md を読んでください。

やること:
1. Chrome で https://www.tiktok.com/tiktokstudio を開く。ログインが必要なら、私が自分でログインするので待ってください。パスワードは扱わないでください。
2. プロフィールを README.md のとおりに設定する（表示名・自己紹介・プロフィール写真）。ユーザー名は変更しない。保存の前に、入力内容を見せて確認を取ってください。
3. schedule.csv の上から順に、TikTok Studio のアップロード画面で予約投稿する。各動画で、キャプション貼り付け・「AI生成コンテンツ」ラベルをオン・予約日時の設定をする。
   - 最初の1本は、「スケジュール」ボタンを押す前に画面を見せて、私の確認を取ってください。
   - 2本目以降は続けてよいですが、まず5本までにして、いったん報告してください。
   - 予約できる日付の上限に達したら、そこで止めて報告してください。
   - 予約した行は schedule.csv の「状態」列を「予約済み」にしてください。
4. CAPTCHA、本人確認、エラー、警告が出たら、自分で回避しようとせず止めて私に知らせてください。
```
