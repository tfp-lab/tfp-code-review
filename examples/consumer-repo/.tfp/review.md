# <Repo 名> 固有のレビュールール (サンプル)

> このファイルは `tfp-code-review` submodule の共通ルールに **追加** で読み込まれます (後勝ち)。
> 全社共通ルール (`.tfp/code-review/prompts/CLAUDE.md` / `.tfp/code-review/instructions/*`) と矛盾する場合、ここに書いた内容が優先されます。

## このリポジトリの背景

- 言語: Go (主) / TypeScript (frontend)
- 主目的: <1〜2 行で>
- 特殊事情: <あれば>

## 追加ルール

- 例: 新規ハンドラ / サービス / DB 層は **interface + struct + `New*()` の 3 点セット** で書くこと。`/.claude/skills/project-conventions/SKILL.md` 参照
- 例: `cmd/legacy/` 配下は段階的に書き換える方針なので、新スタイル convention 違反でも警告のみ ([nit])

## 除外ルール (共通から外す観点)

- 例: [nit] レベルの指摘は出さない (大量 PR で読み切れないため)
- 例: 「context を struct field に持つな」ルールは特定の framework を使うため緩和

## 参考リンク

- 開発ガイド: <Slack / Notion / etc.>
- 関連 Repo: <list>
