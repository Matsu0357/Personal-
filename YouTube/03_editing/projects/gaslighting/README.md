# 試作3本目：それ、ガスライティングかも。（Inspire and Thrive 型）

参考: `../../../01_planning/research/inspire-and-thrive.md`

## コンセプト
- 型：心の健康のテーマを、**黒地・白い棒人間・キーワードだけ赤** のシンプルなアニメで、「〇つのサイン」形式で解説
- テーマ：ガスライティング（診断名ではないので、医療的な断定をしなくて済む。元チャンネルでも伸びているテーマ）
- 守ったこと：
  - 「診断ではない」と冒頭で明言。「当てはまったら〇〇」とは言わない
  - 定義は研究（Sweet, 2019）に沿って「力の差のある関係で、くり返し起きるパターン」とした
  - 最後に、できること（記録する・人に話す）と相談窓口（内閣府のDV相談ナビ #8008、DV相談＋ 0120-279-889）を出す
- ナレーション：やわらかい女性の声（ja-JP-NanamiNeural）
- 長さ：5分41秒

## 出典
- Paige L. Sweet (2019) "The Sociology of Gaslighting." American Sociological Review 84(5): 851–875
- 映画『ガス燈』（Gaslight, 1944）
- 内閣府 男女共同参画局「配偶者からの暴力被害者支援情報」 https://www.gender.go.jp/policy/no_violence/e-vaw/index.html
- 相談窓口の番号は公開前に必ず最新のものを確認すること

## ファイル
| ファイル | 内容 |
| --- | --- |
| `script.json` | 台本。`"card": true` と `num`・`big`・`key`（赤くする語）で「サイン1」のカード |
| `build_audio.py` | ナレーション＋BGM（静かな和音 → 最後に明るい和音）＋カードごとのチャイム |
| `render.html` | 絵。棒人間（pose: stand / bow / shrink / point / think / write / phone / slump / open、mood: worried / stern / happy）、吹き出し、考え事の雲 |
| `render.js` | 動画とサムネイルの書き出し（`--preview` `--thumb`） |
| `metadata.md` | タイトル・説明文・設定 |

## 本番で変えること
- ナレーションの音声を、ライセンスがはっきりしたものへ（VOICEVOX・Azure 公式TTS・ElevenLabs など）
- 可能なら公認心理師などの監修を入れ、説明文に明記する
