# AI_SETUP.md — LLM 単独でセットアップ可能な手順書

> このページは **AI / LLM (Claude / Copilot 等) がこのファイルだけ読めば、新しい Repo に同じレビュー構成をセットアップできる** ことを目的とした単一ページの手順書です。
>
> **最重要原則**: tfp-code-review の構成を変更したら、**必ずこのファイルを最初に更新** してください。次回以降の作業者 (人 or AI) はこのページを正本として動きます。古いままだと組織全体が壊れていきます。

---

## 0. 前提条件 (Pre-requisites)

実行前に以下を満たしていることを確認してください。

- ターゲット Repo が GitHub Actions を使える (Settings → Actions → Allow が有効)
- ターゲット Repo の Secrets に **`AWS_BEARER_TOKEN_BEDROCK`** が登録済み
  - もし未登録なら: AWS Bedrock コンソール → API keys で Bearer Token を発行し、Repo の Settings → Secrets → Actions に `AWS_BEARER_TOKEN_BEDROCK` として登録
- AWS Bedrock の **東京リージョン (ap-northeast-1)** で Claude Sonnet 4.6 へのアクセスが Granted
- ターゲット Repo のデフォルトブランチが `main` (異なる場合は手順中の `main` を読み替えてください)

---

## 1. このリポジトリの提供物

このリポジトリ (`tfp-lab/tfp-code-review`) は以下を提供します:

| ファイル | 役割 | 各 Repo は |
|---|---|---|
| `prompts/CLAUDE.md` | 全社共通のシステムプロンプト (レビュー姿勢・重要度ラベル・出力フォーマット) | submodule で参照するだけ |
| `instructions/<lang>.instructions.md` | 言語別レビュー観点 (Go / TypeScript / PHP) | 同上 |
| `workflows/claude-review.yml` | GitHub Actions ワークフローのテンプレート | これをコピーして自 Repo に置く |
| `assets/icon.png` | reviewer のデフォルトアイコン | submodule 経由で表示 |
| `examples/consumer-repo/` | 利用側 Repo のサンプル | 参照用 |

---

## 2. ターゲット Repo の最終形

セットアップ後、ターゲット Repo は以下の状態になります。

```
<target-repo>/
├── .tfp/
│   ├── code-review/                          ← submodule (tfp-lab/tfp-code-review @ main)
│   └── review.md                             ← この Repo 固有ルール (任意)
├── .github/workflows/claude-review.yml       ← 薄い workflow (submodule init + prompt 読込み)
└── .gitmodules                               ← submodule 情報
```

---

## 3. セットアップ手順 (LLM 用 — 上から順に実行)

各ステップは **コマンド実行** または **ファイル作成** で完結します。AI はこの順序を変えないでください。

### Step 1: ターゲット Repo のルートに移動

```bash
cd <target-repo-absolute-path>
```

### Step 2: submodule を追加

```bash
git submodule add https://github.com/tfp-lab/tfp-code-review.git .tfp/code-review
git submodule update --init --recursive
```

成功すると以下が確認できます:
- `.gitmodules` ファイルが生成される
- `.tfp/code-review/AI_SETUP.md` (この同じファイル) が読める

### Step 3: workflow をコピー

```bash
mkdir -p .github/workflows
cp .tfp/code-review/workflows/claude-review.yml .github/workflows/claude-review.yml
```

### Step 4: workflow の env を Repo 環境に合わせて編集

`.github/workflows/claude-review.yml` 上部の `env:` セクションを確認し、必要に応じて変更:

```yaml
env:
  ANTHROPIC_MODEL: jp.anthropic.claude-sonnet-4-6   # デフォルト: 東京リージョン Sonnet 4.6
  AWS_REGION: ap-northeast-1                         # デフォルト: 東京
  AWS_BEARER_TOKEN_BEDROCK: ${{ secrets.AWS_BEARER_TOKEN_BEDROCK }}  # 触らなくて OK
```

別モデル / 別リージョンを使う場合のみここを変更します。デフォルトで OK ならスキップ。

> 認証は **Bedrock API Key (Bearer Token)** 方式を採用しています。OIDC (IAM Role assume) は使いません。
> `claude-code-action@v1` は `AWS_BEARER_TOKEN_BEDROCK` をネイティブサポートしています
> (公式 docs/cloud-providers.md は古く OIDC のみと書かれていますが、ソース上は対応済み)。
> モデル ID は workflow 内で `claude_args: --model ${{ env.ANTHROPIC_MODEL }}` の形で
> action に渡される実装になっています。

### Step 5: Repo 固有ルール (`.tfp/review.md`) を作成

```bash
mkdir -p .tfp
```

`.tfp/review.md` を以下のテンプレで作成 (Repo 固有事情を書く場所):

```markdown
# <Repo 名> 固有のレビュールール

> このファイルは tfp-code-review submodule の共通ルールに **追加** で読み込まれます (後勝ち)。
> 全社共通のルール (`/.tfp/code-review/prompts/CLAUDE.md` / `/.tfp/code-review/instructions/*`) と矛盾する場合、ここに書いた内容が優先されます。

## このリポジトリの背景

- 言語: <Go / TypeScript / PHP …>
- 主目的: <1〜2 行で>
- 特殊事情: <あれば>

## 追加ルール

- (例) このリポジトリは独自 ORM `xxxorm` を使うため、`database/sql` の慣用句を求める指摘は不要
- (例) `cmd/legacy/` 配下は段階的に書き換える方針。新スタイル convention 違反でも警告のみ ([nit])

## 除外ルール (共通から外す観点)

- (例) [nit] レベルの指摘は出さない (大量 PR で読みきれないため)

## 参考リンク

- 開発ガイド: <Slack / Notion / etc.>
```

(空でも OK。空ならファイル自体作らなくてもよい)

### Step 6: 動作確認用の commit

```bash
git add .gitmodules .tfp .github/workflows/claude-review.yml
git commit -m "Add tfp-code-review submodule for Claude PR review"
```

### Step 7: ブランチを push してテスト PR を作成

```bash
git push -u origin <branch-name>
gh pr create --title "Add Claude PR review (Bedrock)" --body "Setup via tfp-code-review"
```

PR が open になると数十秒〜数分で reviewer (ハムスターアイコン付き) のコメントが付くはずです。
付かない場合は §6 のトラブルシューティング参照。

---

## 4. 更新手順 (構成アップデート版を取り込む)

tfp-code-review に変更が入った場合、ターゲット Repo で以下を実行するだけ:

```bash
cd <target-repo>
git submodule update --remote .tfp/code-review
git add .tfp/code-review
git commit -m "Update tfp-code-review submodule"
git push
```

これで PR を出して main にマージすれば、以降のレビューに最新ルールが適用されます。

### 自動化 (任意)

依存ボット (Renovate / Dependabot) で submodule の更新 PR を自動生成することも可能。Renovate なら以下を `renovate.json` に追加:

```json
{
  "submodules": {
    "enabled": true
  }
}
```

---

## 5. 各ファイルの役割 (リファレンス)

### tfp-code-review 側

- **`prompts/CLAUDE.md`** — 全社共通システムプロンプト。レビュー姿勢・重要度ラベル `[must-fix]`/`[suggestion]`/`[nit]` の定義・出力フォーマット・セキュリティ最低ライン
- **`instructions/_template.instructions.md`** — 新言語のレビュー観点を追加するときのテンプレ
- **`instructions/<lang>.instructions.md`** — 言語別の詳細観点。`applyTo` frontmatter で対象拡張子を指定
- **`workflows/claude-review.yml`** — テンプレート workflow。各 Repo はこれをそのままコピー
- **`assets/icon.png`** — reviewer アバター画像 (各 Repo で `.tfp/icon.png` を置けば override 可能、ただし現状 workflow は assets/icon.png を直接参照)

### ターゲット Repo 側

- **`.tfp/code-review/`** — submodule。実体は tfp-lab/tfp-code-review の clone
- **`.tfp/review.md`** — この Repo 固有のルール。任意
- **`.github/workflows/claude-review.yml`** — 実際に動くワークフロー
- **`.gitmodules`** — submodule の管理情報 (自動生成)

---

## 6. トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| PR を作ってもレビューが付かない | workflow がデフォルトブランチに無い / Actions が disable | Settings → Actions で許可。`gh run list -R <owner>/<repo>` で実行状況を確認 |
| `Submodule path '.tfp/code-review' not initialized` | チェックアウト時に submodule init していない | workflow 内で `submodules: recursive` 必須。`git submodule update --init --recursive` を手元でも実行 |
| `AccessDeniedException` (Bedrock) | (1) `AWS_BEARER_TOKEN_BEDROCK` 未設定 (2) Bedrock の Model access が Granted でない (3) リージョン不一致 | 順番に確認 |
| `Either ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN is required` | workflow の `with:` に `use_bedrock: "true"` が無い | テンプレ最新版を再コピー (`cp .tfp/code-review/workflows/claude-review.yml .github/workflows/`) |
| `403 Authorization header is missing` | claude-code 内部の Bedrock 認証で Bearer Token が空文字 | secret `AWS_BEARER_TOKEN_BEDROCK` の値が空でないか確認。再生成も検討 |
| `ResourceNotFoundException: model not found` | `ANTHROPIC_MODEL` の inference profile ID が誤り | AWS コンソール → Bedrock (東京) → Inference profiles で正確な ID を確認 |
| アイコンが PR コメントに出ない | private リポジトリの raw URL 問題 | tfp-code-review を public 化、もしくは PR コメントの絵文字フォールバックを許可 |
| レビューが英語で来る | prompt の言語指示が弱い | `.tfp/review.md` で「日本語で書け」を強調 |

---

## 7. このページ自体の更新ルール (重要)

このリポジトリ (`tfp-code-review`) の構成を変更したら、**変更内容と矛盾しないようこのファイルを必ず更新** してください。具体的には以下のタイミング:

- ファイル / ディレクトリの追加・移動・削除
- workflow の env 名・必須 secret 名・トリガー条件の変更
- 言語別 instructions の追加 / 命名規則変更
- バージョニング方針の変更 (main pin → tag pin など)
- セットアップ手順の変更

更新したら CHANGELOG.md にもエントリを追加。次回以降の AI / 人間がこのページだけ読めば最新手順で作業できる状態を維持します。

---

## 8. デザイン上の決定事項 (なぜ submodule? なぜ `.tfp/`?)

(背景情報。LLM が判断に迷ったときの指針)

- **submodule を採用した理由**: Repo 内に物理ファイルとして配置でき、`cat .tfp/code-review/prompts/CLAUDE.md` で目視確認・debug がしやすい。Reusable workflow だと prompt ファイルを Action からファイル参照しにくい
- **`.tfp/` 名前空間にした理由**: `.github/` を汚さない。将来 `.tfp/lint/` `.tfp/security/` など他種別を加える余地を残す
- **main pin の理由**: 「構成アップデートがあれば見て更新」という運用要件にもっとも単純に応える。安定性優先の Repo は個別に commit pin することも可能
- **`.tfp/review.md` の優先度**: 共通プロンプトに **追加** される (後勝ち)。共通ルールを完全置換するわけではなく、追加・上書きで動く

---

## 9. 関連ドキュメント

- [README.md](README.md) — 人間向けのリポジトリ概要・ドキュメント index
- [QUICKSTART_PROMPT.md](QUICKSTART_PROMPT.md) — **コピペ一発でセットアップ** (LLM プロンプト + bash 一式)
- [USAGE.md](USAGE.md) — 導入済み Repo での日常操作 + プロジェクト個別設定の早見表
- [CHANGELOG.md](CHANGELOG.md) — 変更履歴
- [prompts/CLAUDE.md](prompts/CLAUDE.md) — 共通システムプロンプト本体
- [instructions/](instructions/) — 言語別レビュー観点
- [workflows/claude-review.yml](workflows/claude-review.yml) — workflow テンプレ
- [examples/consumer-repo/](examples/consumer-repo/) — 利用側 Repo のサンプル
