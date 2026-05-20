# tfp-code-review

> TFP の **共通 PR コードレビュー基盤**。各リポジトリは submodule としてこれを取り込み、薄い workflow を 1 本コピーするだけで Claude (Bedrock 経由) による自動レビューが立ち上がる。

![reviewer](assets/icon.png)

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

## Contribution

PR は main ブランチに対して。CI で `prompts/CLAUDE.md` と `instructions/*.instructions.md` の構文を最低限チェックする (TODO)。

## ライセンス

社内利用のみ (要確認)。
