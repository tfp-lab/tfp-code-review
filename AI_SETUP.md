# AI_SETUP.md — LLM 単独でセットアップ可能な手順書 (v0.7+)

> このページは **AI / LLM (Claude / Copilot 等) がこのファイルだけ読めば、新しい Repo に同じレビュー構成をセットアップできる** ことを目的とした単一ページの手順書です。
>
> **最重要原則**: tfp-code-review の構成を変更したら、**必ずこのファイルを最初に更新** してください。次回以降の作業者 (人 or AI) はこのページを正本として動きます。古いままだと組織全体が壊れていきます。

---

## 0. v0.7.0 からの破壊的変更 (移行が必要な人だけ読む)

v0.6 までは **submodule + workflow 全文コピー** 方式でしたが、v0.7 から **Reusable workflow** 方式に全面移行しました。

| 項目 | v0.6 まで | v0.7 以降 |
|---|---|---|
| 共通改修の反映 | submodule bump + workflow 全文コピーが必要 | **何もしない (即反映)** |
| 各 Repo の必要ファイル | `.gitmodules` + `.tfp/code-review/` (submodule) + `.github/workflows/claude-review.yml` (200 行) + `.tfp/review.md` | `.github/workflows/claude-review.yml` (約 25 行 caller) + `.tfp/review.md` |
| `.tfp/code-review/` submodule | 必須 | **削除 (不要)** |
| バージョン pin | submodule SHA | `@main` / `@v1` 等 |

既存導入済み Repo で v0.7 へ移行するには:

```bash
cd <target-repo>
# submodule 削除
git submodule deinit -f .tfp/code-review || true
git rm -f .tfp/code-review || true
rm -rf .git/modules/.tfp
# 新 caller workflow を取得
curl -fsSL https://raw.githubusercontent.com/tfp-lab/tfp-code-review/main/workflows/claude-review.yml \
  -o .github/workflows/claude-review.yml
git add -A
git commit -m "Migrate to tfp-code-review v0.7 Reusable workflow"
```

---

## 1. 前提条件 (Pre-requisites)

実行前に以下を満たしていることを確認してください。

- ターゲット Repo が GitHub Actions を使える (Settings → Actions → Allow が有効)
- ターゲット Repo の Secrets に **`AWS_BEARER_TOKEN_BEDROCK`** が登録済み
  - 未登録なら: AWS Bedrock コンソール → API keys で Bearer Token を発行 → Repo の Settings → Secrets → Actions に登録
- AWS Bedrock の **東京リージョン (ap-northeast-1)** で Claude Sonnet 4.6 へのアクセスが Granted
- ターゲット Repo のデフォルトブランチが `main` (異なる場合は手順中の `main` を読み替え)

---

## 2. このリポジトリの提供物

このリポジトリ (`tfp-lab/tfp-code-review`) は以下を提供します:

| ファイル | 役割 | 各 Repo は |
|---|---|---|
| **`.github/workflows/review.reusable.yml`** | **Reusable workflow 本体**。各 Repo はこれを `uses:` で呼ぶ | 編集不要・参照のみ |
| `prompts/CLAUDE.md` | 全社共通のシステムプロンプト | reusable workflow 内で参照 |
| `instructions/<lang>.instructions.md` | 言語別レビュー観点 | reusable workflow 内で参照 |
| `workflows/claude-review.yml` | **caller のテンプレート** (各 Repo にコピーする 25 行 yaml) | これをコピー |
| `assets/icon.png` | reviewer のデフォルトアイコン | reusable workflow 内で参照 |
| `examples/consumer-repo/` | 利用側 Repo のサンプル | 参照用 |

---

## 3. ターゲット Repo の最終形

セットアップ後、ターゲット Repo は以下の状態になります (たった 2 ファイル):

```
<target-repo>/
├── .tfp/
│   └── review.md                             ← この Repo 固有ルール (任意)
└── .github/workflows/claude-review.yml       ← 25 行の caller (uses: で reusable を呼ぶだけ)
```

> **submodule なし**。`.gitmodules` も不要。

---

## 4. セットアップ手順 (LLM 用 — 上から順に実行)

### Step 1: ターゲット Repo のルートに移動

```bash
cd <target-repo-absolute-path>
```

### Step 2: caller workflow をコピー

```bash
mkdir -p .github/workflows
curl -fsSL https://raw.githubusercontent.com/tfp-lab/tfp-code-review/main/workflows/claude-review.yml \
  -o .github/workflows/claude-review.yml
```

`.github/workflows/claude-review.yml` の中身は約 25 行で、以下のような最小 caller です:

```yaml
name: NoraBot PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]
  issue_comment:
    types: [created]

permissions:
  contents: read
  pull-requests: write
  issues: write
  id-token: write

jobs:
  review:
    uses: tfp-lab/tfp-code-review/.github/workflows/review.reusable.yml@main
    secrets:
      AWS_BEARER_TOKEN_BEDROCK: ${{ secrets.AWS_BEARER_TOKEN_BEDROCK }}
```

### Step 3: (任意) Repo 固有のモデル / リージョン上書き

デフォルト (Sonnet 4.6 / 東京) で良ければスキップ。変更したい場合のみ:

```yaml
jobs:
  review:
    uses: tfp-lab/tfp-code-review/.github/workflows/review.reusable.yml@main
    secrets:
      AWS_BEARER_TOKEN_BEDROCK: ${{ secrets.AWS_BEARER_TOKEN_BEDROCK }}
    with:
      model: jp.anthropic.claude-opus-4-7      # 他のモデルへ
      aws_region: us-east-1                     # 他リージョンへ
```

### Step 4: Repo 固有ルール (`.tfp/review.md`) を作成 (任意)

```bash
mkdir -p .tfp
```

`.tfp/review.md` テンプレ:

```markdown
# <Repo 名> 固有のレビュールール

> このファイルは tfp-code-review 共通ルールに **追加** で読み込まれます (後勝ち)。
> 共通ルールと矛盾する場合、ここに書いた内容が優先されます。

## 言語
<Go / TypeScript / PHP …>

## 追加ルール
- (例) このリポジトリは独自 ORM `xxxorm` を使うため、`database/sql` 慣用句を求める指摘は不要

## 除外ルール
- (例) [nit] レベルの指摘は出さない
```

無ければ無くてもよい。共通ルールだけで動きます。

### Step 5: commit & push

```bash
git add .github/workflows/claude-review.yml .tfp/review.md
git commit -m "Add NoraBot PR review (tfp-code-review reusable workflow)"
git push
```

### Step 6: テスト PR を出して動作確認

```bash
git switch -c test/norabot-trial
echo "// trigger" >> README.md
git add -A && git commit -m "test: trigger NoraBot"
git push -u origin HEAD
gh pr create --title "test: NoraBot trial" --body "Verifying setup"
```

数十秒で「**NoraBot is reviewing…**」コメントが PR トップに出れば成功。1〜3 分でレビュー本文に書き換わります。

---

## 5. 更新手順 (構成アップデート版を取り込む)

**v0.7 以降は何もしないでも反映されます**。caller は `@main` で reusable workflow を参照しているため、tfp-code-review main に push されれば次回 trigger から最新版で動きます。

特定バージョンに pin したい場合のみ caller の `@main` を `@v1.0.0` に変更:

```yaml
uses: tfp-lab/tfp-code-review/.github/workflows/review.reusable.yml@v1.0.0
```

---

## 6. トラブルシューティング

| 症状 | 対処 |
|---|---|
| PR を出してもレビューが付かない | (1) `.github/workflows/claude-review.yml` がデフォルトブランチに存在するか / (2) Actions タブでジョブが失敗していないか / (3) `AWS_BEARER_TOKEN_BEDROCK` secret が空でないか |
| `Claude Code is not installed on this repository` | reusable workflow 内で `github_token: ${{ secrets.GITHUB_TOKEN }}` が渡されているか確認 (v0.7 では既定で渡している) |
| `AccessDeniedException` (Bedrock) | (1) Model access が Granted か / (2) リージョンが正しいか / (3) Bearer token に必要な IAM 権限があるか |
| `permission_denials_count > 0` | reusable workflow の `--allowedTools` に呼ばれたツール名を追加 |
| 共通観点が古い | reusable workflow が `@main` を使っているか確認。tag pin している場合は最新 tag に上げる |

---

## 7. このページ自体の更新ルール

tfp-code-review の構成を変更したら、変更内容と矛盾しないようこのファイルを必ず更新。具体的には:

- ファイル / ディレクトリの追加・移動・削除
- reusable workflow の inputs / secrets / 必須 permissions の変更
- 認証方式の変更 (Bearer Token / OIDC / API Key)
- セットアップ手順の変更

更新したら CHANGELOG.md にもエントリを追加。

---

## 8. デザイン上の決定事項 (なぜ Reusable workflow?)

- **submodule をやめた理由**: 共通改修するたびに各 Repo で submodule pointer 更新 + workflow ファイル更新の二重 push が必要で、運用が重かった
- **Reusable workflow の利点**: caller (各 Repo) は約 25 行の薄い yaml だけ。共通改修は tfp-code-review main 1 箇所で完結し、即全 Repo に反映
- **`@main` pin の理由**: 「構成アップデートがあれば自動で反映」という運用要件にもっとも単純に応える。安定性優先の Repo は `@v1.0.0` 等に pin 可能
- **`.tfp/review.md` の優先度**: 共通プロンプトに **追加** される (後勝ち)

---

## 9. 関連ドキュメント

- [README.md](README.md) — 人間向けのリポジトリ概要
- [QUICKSTART_PROMPT.md](QUICKSTART_PROMPT.md) — コピペ一発でセットアップ (LLM プロンプト + bash 一式)
- [USAGE.md](USAGE.md) — 導入済み Repo での日常操作 + プロジェクト個別設定の早見表
- [CHANGELOG.md](CHANGELOG.md) — 変更履歴
- [.github/workflows/review.reusable.yml](.github/workflows/review.reusable.yml) — Reusable workflow 本体
- [workflows/claude-review.yml](workflows/claude-review.yml) — caller テンプレート (各 Repo にコピーする 25 行)
- [prompts/CLAUDE.md](prompts/CLAUDE.md) — 共通システムプロンプト
- [instructions/](instructions/) — 言語別レビュー観点
