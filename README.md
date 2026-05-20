# tfp-code-review

> TFP の **共通 PR コードレビュー基盤** (レビュアー名: **NoraBot**)。
> 各リポジトリは submodule としてこれを取り込み、薄い workflow を 1 本コピーするだけで NoraBot (AWS Bedrock 上の Claude) による自動レビューが立ち上がる。

![reviewer](assets/icon.png)

> ⚠️ **PUBLIC リポジトリです** — このリポジトリは consumer 側の GitHub Actions が submodule として clone できるよう **public** で公開されています。コミット前に必ず本 README の **[公開リポジトリ運用上の注意](#公開リポジトリ運用上の注意)** を読んでください。社外秘情報を含めると **永久に取り戻せません**。

## これは何?

- AWS Bedrock 上の Claude (Sonnet 4.6 等) を使って **PR を自動レビュー** するための共通基盤リポジトリ
- 全社 / チーム共通のレビュー方針 (重要度ラベル / セキュリティ最低ライン / 出力フォーマット) と、言語別レビュー観点 (Go / TypeScript / PHP …) をここに集約
- 各 Repo は自分の **特有ルールだけ** を `.tfp/review.md` に書く

## 構成

```
tfp-code-review/
├── README.md                          ← この概要 (人間向け)
├── AI_SETUP.md                        ★ 外部 AI / LLM がこのページを読むだけで構成を再現できる単一ページ
├── CHANGELOG.md
├── prompts/CLAUDE.md                  全社共通システムプロンプト
├── instructions/
│   ├── _template.instructions.md      新言語追加時のテンプレ
│   ├── go.instructions.md             Go 用観点
│   ├── typescript.instructions.md     TypeScript 用観点
│   └── php.instructions.md            PHP 用観点
├── workflows/
│   └── claude-review.yml              各 Repo にコピーする workflow テンプレ
├── assets/
│   └── icon.png                       デフォルト reviewer アイコン
└── examples/
    └── consumer-repo/                 利用側 Repo のサンプル構成
        ├── .tfp/review.md
        └── .github/workflows/claude-review.yml
```

## 各 Repo 側の見え方

```
<your-repo>/
├── .tfp/
│   ├── code-review/                   ← この submodule (tfp-code-review @main)
│   └── review.md                      ← この Repo 固有のレビュールール (任意)
└── .github/workflows/claude-review.yml ← 薄い workflow (submodule から prompt を読む)
```

## ドキュメント (役割別)

| ファイル | 読むべき人 | 内容 | HTML (見やすい版) |
|---|---|---|---|
| [README.md](README.md) | 全員 (最初の入口) | 概要・ディレクトリ構成 | [docs/README.html](docs/README.html) |
| [QUICKSTART_PROMPT.md](QUICKSTART_PROMPT.md) | **新規 Repo に導入したい人** | コピペ用 LLM プロンプト + 手動 bash コマンド | [docs/QUICKSTART_PROMPT.html](docs/QUICKSTART_PROMPT.html) |
| [AI_SETUP.md](AI_SETUP.md) | LLM / 詳細手順を見たい人 | 単一ページで完結する正式セットアップ手順 | [docs/AI_SETUP.html](docs/AI_SETUP.html) |
| [USAGE.md](USAGE.md) | **導入済み Repo の利用者** | 日常操作 + プロジェクト個別設定の早見表 | [docs/USAGE.html](docs/USAGE.html) |
| [CHANGELOG.md](CHANGELOG.md) | アップデート確認 | バージョン履歴 | [docs/CHANGELOG.html](docs/CHANGELOG.html) |

> **MD を編集したら同じ PR で `docs/*.html` を再生成して commit** してください (CHANGELOG にも反映)。
>
> 一括再生成 (リポジトリルートで実行):
> ```bash
> for f in README.md AI_SETUP.md USAGE.md QUICKSTART_PROMPT.md CHANGELOG.md; do
>   python3 scripts/md2html.py "$f" --out-dir docs --icon assets/icon.png
> done
> ```
>
> `_html/` (gitignore 対象) は手元での試し生成用。チームに共有する HTML は `docs/` 配下のみ。

## 使い方 (新しい Repo に導入する場合)

**速い**: [QUICKSTART_PROMPT.md](QUICKSTART_PROMPT.md) を開いて、AI チャットに 1 つコピペ。
**詳しい**: [AI_SETUP.md](AI_SETUP.md) を上から順に実行。

どちらも最終的に同じ状態になります。構成を変更したら **両方とも更新** してください (docs と code は同じ PR で同期が原則)。

## 変更履歴

[CHANGELOG.md](CHANGELOG.md) を参照。

## バージョン管理方針

- 各 Repo は `main` ブランチを submodule で参照する **main pin** 運用
- 後方非互換な変更を入れるときは CHANGELOG に「Breaking」と明記し、各 Repo に告知してから main にマージする
- 緊急停止が必要な Repo は一時的に submodule を特定 commit に pin することも可能 (`git submodule set-branch` 等)

## 公開リポジトリ運用上の注意

このリポジトリは **public** です。コミットする前に以下を必ず確認してください。
**一度公開した内容は GitHub の history を含めて永久に取り戻せません。**

### コミットしてはいけない情報 (NG リスト)

| カテゴリ | 具体例 | 代わりに |
|---|---|---|
| 認証情報 | API key / token / password / secret 値 / `.env` の中身 | `secrets.XXX` で参照、値は GitHub Secrets に |
| 内部ホスト / URL | `*.internal.tfp` / `vpn.lifetech.local` / 社内 Slack URL | 「社内エンドポイント」とだけ記述 |
| 顧客名 / プロジェクトコードネーム | 顧客企業名 / 製品コードネーム | 一般化した表現に (例: 「保険業界向け」「金融系」) |
| 内部 Repo 名 | `lifetech-inc/xxxx` / 社内 GitLab パス | examples では汎用的な名前 (`<your-repo>` 等) |
| 個人情報 | メールアドレス / 個人 Slack handle / 顔写真 | git ユーザ情報のみ (Co-Authored-By 等) |
| ビジネスロジック | 業務固有の計算式 / 料率 / 業績算出ロジック | 一般的なベストプラクティスとして抽象化 |
| 内部攻撃面情報 | 内部 IP / 脆弱性チケット番号 / インシデント詳細 | 抽象化、もしくは記載しない |

### コミットしてよい情報 (OK リスト)

- 言語別ベストプラクティス (Effective Go / PSR / TS handbook 由来など、すでに公開されている知見の整理)
- 重要度ラベルの定義 ([must-fix] / [suggestion] / [nit])
- 出力フォーマット
- セットアップ手順 (`AI_SETUP.md` / `QUICKSTART_PROMPT.md` のような汎用手順)
- workflow テンプレ (secret の値は含めず、参照のみ)

### コミット前のセルフチェック

PR を出す前に以下を実行:

```bash
# 機密キーワードの検出
git diff main... | grep -iE "(password|secret|token|api[-_ ]?key|credential|aws_access_key)" && echo "⚠️ チェック必要"

# 社内固有名詞の検出 (組織名・顧客名は適宜追加)
git diff main... | grep -iE "(lifetech-inc|hoken-manager|<顧客固有名>)" && echo "⚠️ 一般化を検討"
```

検出されても誤検知のことが多いので、内容を確認して問題なければ進めて OK。検出されたまま push しないこと。

### Pull Request のレビュー必須化

main ブランチは branch protection で以下を有効化推奨:

- Require a pull request before merging
- Require approvals: **1 名以上** (社員レビュー必須)
- Require review from Code Owners (CODEOWNERS 配置時)
- Restrict who can push to matching branches (org メンバーのみ)

### 第三者 (org 外) からの PR

- public リポジトリなので **誰でも** PR を送れます
- マージ可否は **完全にメンテナ判断**。自動マージ禁止
- 不審な PR (悪意あるコード混入の試み等) は close + report
- ありがたい改善提案は普通にレビューしてマージしてよい

### Public 化を取り止めるとき

社内事情で private に戻す必要が出た場合:

1. Settings → General → Danger Zone → Change visibility → Make private
2. **取り止めても、それまで public だった期間に fork / clone した人がいたら取り戻せない** ことを認識
3. consumer 側 (各 Repo の workflow) は private 化後 secret 認証 (PAT / Deploy Key) が必須になるので、合わせて切替が必要

---

## Contribution

PR は main ブランチに対して。

- 社員: 通常通り PR → レビュー → マージ
- org 外: 改善提案ありがたいですが、内部運用に依存する変更はマージ判断が遅れることがあります
- すべての PR は **上記 NG リストに該当する情報が含まれていないか** をレビュー時に必ず確認

CI で `prompts/CLAUDE.md` と `instructions/*.instructions.md` の構文を最低限チェックする (TODO)。

## ライセンス

社内利用を主目的とした内部ツールです。LICENSE ファイルは現状未配置 (= デフォルト = 第三者の再配布 / 改変権なし)。
社外で再利用したい人がいる場合は org オーナーに相談してください。
