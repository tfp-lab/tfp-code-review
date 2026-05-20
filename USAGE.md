# USAGE.md — Norabot の使い方 & プロジェクト個別設定の早見表

> このドキュメントは **tfp-code-review を導入済みの Repo で、日常的に Norabot レビュー機能を使う人** 向けです。
> Norabot は本基盤の AI レビュアー (Claude / Bedrock) の呼称です。
> 初期セットアップは [AI_SETUP.md](AI_SETUP.md)、自動コピペで一発導入したい人は [QUICKSTART_PROMPT.md](QUICKSTART_PROMPT.md) を参照してください。

---

## TL;DR (やりたいこと → やること)

| やりたいこと | やること |
|---|---|
| **PR を出してレビューしてほしい** | いつも通り PR を作るだけ。自動で走ります |
| **もう一度レビューさせたい** | PR コメントに `@norabot review` |
| **特定の観点で見てほしい** | コメントに `@norabot セキュリティ観点で再確認して` |
| **特定ファイルだけ見てほしい** | コメントに `@norabot src/handler/foo.go だけ詳しく見て` |
| **指摘に反論したい** | 該当指摘へのリプライで `@norabot` 付きで質問 |
| **このリポジトリだけのルールを足したい** | `.tfp/review.md` を編集して PR |
| **全社のルールを変えたい** | tfp-code-review に PR (main へ) |
| **共通ルール更新を取り込みたい** | `git submodule update --remote .tfp/code-review && git commit` |
| **モデルや region を変えたい** | `.github/workflows/claude-review.yml` の env を編集 |
| **アイコンを変えたい** | `.tfp/icon.png` を置く (Repo 専用) or tfp-code-review の `assets/icon.png` を差し替え (全社) |

---

## 1. プロジェクト個別設定 — どこに何を置くか早見表

「自分の Repo 特有のルールはどこに書けばいいか」を 1 表に集約しました。**まずこの表だけ覚えれば OK**。

### 1-1. ファイル配置の早見表

| ファイル / ディレクトリ | 役割 | 必須? | 置く場所 | 編集する人 |
|---|---|---|---|---|
| `.tfp/code-review/` | 共通基盤の submodule (中身は読み取り専用扱い) | **必須** | Repo ルート | (触らない) |
| `.tfp/review.md` | この Repo 固有のレビュールール | 推奨 (空でも置いとくと混乱しない) | Repo ルート | この Repo の担当 |
| `.tfp/icon.png` | この Repo 専用 reviewer アイコン (上書き) | 任意 | Repo ルート | この Repo の担当 |
| `.github/workflows/claude-review.yml` | 実動 workflow | **必須** (`workflows/` テンプレからコピー) | 標準 | この Repo の担当 (model 切替等) |
| `.gitmodules` | submodule 情報 (自動生成) | 自動 | Repo ルート | (触らない) |

### 1-2. レビュー観点を書く場所の早見表

「どんなルールをどこに書くか」で迷ったら以下の表を見る:

| ルールの種類 | 書く場所 | 例 |
|---|---|---|
| **全社・全リポジトリで共通** | tfp-code-review の `prompts/CLAUDE.md` | "重要度ラベル必須"、"日本語で書く"、"出力フォーマット" |
| **特定言語の共通観点** | tfp-code-review の `instructions/<lang>.instructions.md` | Go の "errors.Is を使え"、PHP の "PDO プレースホルダ必須" |
| **このリポジトリだけの慣習** | この Repo の `.tfp/review.md` | "このリポジトリは独自 ORM `xxxorm` を使うので X の指摘は不要" |
| **このリポジトリの新スタイル convention** | この Repo の `.tfp/review.md` | "新規ファイルは interface + struct + `New*()` の 3 点セット" |
| **このリポジトリの除外ルール** | この Repo の `.tfp/review.md` | "[nit] レベルの指摘は出さない" |
| **PR タイトル / コミット規約** | この Repo の `.tfp/review.md` (Repo 固有なら) or 共通 (全社統一なら) | "チケット番号 prefix `dev_677：` 必須" |

> **判断に迷ったら**: 「他の Repo にも適用したいか?」で考えると整理しやすい。Yes → 共通 (tfp-code-review)、No → `.tfp/review.md`。

### 1-3. 言語別観点の追加

新しい言語 (Kotlin / Rust / etc.) のレビュー観点を全社で追加したい場合:

1. tfp-code-review の `instructions/_template.instructions.md` をコピー
2. `instructions/<lang>.instructions.md` として保存
3. frontmatter の `applyTo` を対象拡張子に変更 (例: `**/*.kt`)
4. 観点を埋める
5. PR を出して main へマージ
6. 各 Repo は `git submodule update --remote .tfp/code-review` で取り込む

特定 Repo だけで一時的に書くなら `.tfp/review.md` 内に「Kotlin はこう見ろ」と直接書いても可。

---

## 2. `.tfp/review.md` テンプレ集

コピペで使える、Repo 種別ごとの `.tfp/review.md` テンプレ。

### 2-1. 何も特殊事情がない Repo

```markdown
# <Repo 名> 固有のレビュールール

このリポジトリでは特殊事情なし。共通ルールに従う。
```

これだけで OK。空でも問題ありませんが、ファイル自体を置いておくと「ルール上書きの仕組みがある」と他メンバーに伝わります。

### 2-2. Go プロジェクト (新スタイル convention あり)

```markdown
# <Repo 名> 固有のレビュールール

## 言語
Go (主)

## 追加ルール
- 新規ファイルは **interface + struct + `New*()` の 3 点セット** で書くこと ([must-fix])
- パッケージレベル関数で業務ロジックを書く古いスタイルは新規追加禁止
- 既存古ファイルへの追記は古いスタイル継続で OK (surgical-changes)

## PR 規約
- PR タイトル: `dev_677：自己報告詳細取得` のように **チケット番号 prefix + コロン + 日本語簡潔説明**
```

### 2-3. レガシーディレクトリを抱える Repo

```markdown
# <Repo 名> 固有のレビュールール

## レガシー扱いの領域
以下のディレクトリは段階的に書き換える方針。新スタイル convention 違反でも警告のみ ([nit]) で扱うこと。

- `cmd/legacy/`
- `internal/v1/`
- `pkg/old_*/` (ワイルドカード対象)
```

### 2-4. ノイズが多い Repo (指摘を絞りたい)

```markdown
# <Repo 名> 固有のレビュールール

## 除外ルール
- [nit] レベルの指摘は出さない (PR 量が多く読みきれないため)
- gofmt / goimports で機械修正できる範囲は指摘しない (CI 任せ)
- 同種の指摘は最大 1 件にまとめる
```

### 2-5. 特殊フレームワーク / 独自 ORM を使う Repo

```markdown
# <Repo 名> 固有のレビュールール

## 環境
- ORM: `xxxorm` (独自)
- HTTP: `yyyrouter` (echo ベース)

## 共通ルールの上書き
- 「`database/sql` の慣用句に沿え」系指摘は不要 (`xxxorm` 経由で別 API)
- "ctx を struct field に持つな" は緩和 (`xxxorm` の Query Builder が前提とするため)
```

---

## 3. PR コメントでの操作

### 3-1. 自動レビュー (デフォルト)

PR を `opened` / `synchronize` / `reopened` すると自動で走ります。止めたい場合は draft PR にしておく。

### 3-2. アノテーション (`@norabot`)

PR の **Issue コメント欄** に `@norabot` (大文字小文字どちらでも可) を含むコメントを投稿するとトリガー。

```
@norabot review
```

```
@norabot セキュリティとパフォーマンスに絞って再レビュー。
特に N+1 と認可漏れを重点的に。
```

```
@norabot src/handler/foo.go だけ詳しく見て。
他は無視していい。
```

### 3-3. 指摘へのリプライ

指摘スレッド内で `@norabot` を含むリプライを投稿すれば対話できます。

```
@norabot
この指摘は他ハンドラと書き方を揃えているので、ここで修正すると
全体の一貫性が崩れます。別 issue 化が妥当な認識ですが、見解をください。
```

---

## 4. レビューコメントの読み方

レビューコメントは以下のフォーマットで返ります。

```markdown
![reviewer](<url>)

**この PR のサマリ**: 〜〜

## 指摘事項

### [must-fix]
- `path/to/file.ext:42` 〜〜

### [suggestion]
- `path/to/file.ext:88` 〜〜

### [nit]
- `path/to/file.ext:120` 〜〜

## 良かった点
- 〜〜
```

### 重要度の対応

| ラベル | マージ前の対応 |
|---|---|
| `[must-fix]` | **必ず直す**。直せない事情があれば PR で議論しレビュアー人間と合意 |
| `[suggestion]` | 基本的に直す。スコープ外なら別 issue 化 |
| `[nit]` | 任意 |

### 却下する場合

LLM レビューは万能ではありません。**理由を一文書いて却下** すれば OK。後から見たとき「なぜ無視したか」が分かるようにする。

---

## 5. モデル / リージョンの切替

`.github/workflows/claude-review.yml` 上部の env を編集して PR を出すだけ。

```yaml
env:
  ANTHROPIC_MODEL: jp.anthropic.claude-sonnet-4-6   # ここ
  AWS_REGION: ap-northeast-1                         # ここ
```

候補 (東京リージョン):

- `jp.anthropic.claude-sonnet-4-6` — 推奨
- `jp.anthropic.claude-sonnet-4-5` — フォールバック
- `jp.anthropic.claude-opus-4-7` — 大きい PR / じっくり見たいとき
- `jp.anthropic.claude-haiku-4-5` — 軽量・高速

---

## 6. 共通基盤の更新を取り込む

tfp-code-review に変更が入ったら、各 Repo で:

```bash
git submodule update --remote .tfp/code-review
git add .tfp/code-review
git commit -m "Update tfp-code-review submodule"
git push
```

PR をマージすれば以降のレビューに反映。

### Renovate を使う場合

`renovate.json` に以下を入れれば自動 PR 化:

```json
{
  "submodules": { "enabled": true }
}
```

---

## 7. アイコンを変える

| やりたいこと | やること |
|---|---|
| 全社で変える | tfp-code-review の `assets/icon.png` を差し替えて PR |
| この Repo だけ別アイコン | `.tfp/icon.png` を Repo ルートに置く (workflow が自動で優先) |

> GitHub Actions bot のアバター自体を変えるには **GitHub App 化が必要** (本構成範囲外)。

---

## 8. トラブルシューティング (簡易)

詳細は [AI_SETUP.md](AI_SETUP.md) §6 を参照。

| 症状 | 一次対処 |
|---|---|
| レビューが付かない | Actions タブで失敗していないか確認 |
| `Submodule not initialized` | `git submodule update --init --recursive` |
| `AccessDeniedException` | Bedrock Model access が Granted か確認 |
| 共通観点が古い | submodule を `update --remote` で最新化 |
| Repo 固有ルールが効かない | `.tfp/review.md` のパスとマークアップ確認 |

---

## 9. 関連ドキュメント

| パス | 内容 |
|---|---|
| [README.md](README.md) | tfp-code-review の概要 |
| [AI_SETUP.md](AI_SETUP.md) | LLM 用セットアップ手順 |
| [QUICKSTART_PROMPT.md](QUICKSTART_PROMPT.md) | 一発導入用コピペプロンプト |
| [USAGE.md](USAGE.md) | (本ファイル) 使い方 + 早見表 |
| [CHANGELOG.md](CHANGELOG.md) | 変更履歴 |
