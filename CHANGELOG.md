# Changelog

すべての変更はこのファイルに記録する。形式は [Keep a Changelog](https://keepachangelog.com/) に準拠。

## [Unreleased]

## [0.2.1] - 2026-05-20

### Changed
- `_html/` を git 管理対象に変更 (これまで `.gitignore` 除外)。設定手順や使い方をブラウザで直接見せられるよう、HTML を成果物として同梱
- README にドキュメント MD と HTML を併記する index 表を追加
- 運用ルール: MD を編集したら同じ PR で HTML も再生成して commit (CHANGELOG にも反映)

## [0.2.0] - 2026-05-20

### Added
- `USAGE.md`: 導入済み Repo の日常操作ガイド + 「プロジェクト個別設定の早見表」(どんなルールをどこに書くかの対応表 / `.tfp/review.md` テンプレ集)
- `QUICKSTART_PROMPT.md`: LLM 一発導入用プロンプト + AI 不要の bash コマンド一式 (新規導入 / 共通追従 / アンインストール)
- `scripts/md2html.py`: ドキュメント MD → HTML 変換ツール (`_html/` は gitignore)

### Changed
- `README.md`: ドキュメント役割別の index を追加
- `AI_SETUP.md`: 関連ドキュメント節に USAGE.md / QUICKSTART_PROMPT.md を追加
- `.gitignore`: `_html/` `__pycache__/` を追加

## [0.1.0] - 2026-05-20

### Added
- 初回リリース
- `prompts/CLAUDE.md` (全社共通システムプロンプト)
- `instructions/_template.instructions.md` (新言語追加テンプレ)
- `instructions/go.instructions.md` (Go レビュー観点 14 項目)
- `instructions/typescript.instructions.md` (雛形)
- `instructions/php.instructions.md` (雛形)
- `workflows/claude-review.yml` (Bedrock + Claude Code Action のワークフローテンプレ)
- `assets/icon.png` (reviewer アバター)
- `examples/consumer-repo/` (利用側 Repo サンプル)
- `AI_SETUP.md` (LLM 自走用の単一ページ手順書)
- `README.md` (人間向け概要)

### Notes
- 認証方式: AWS Bedrock (`AWS_BEARER_TOKEN_BEDROCK` secret)
- デフォルトモデル: `jp.anthropic.claude-sonnet-4-6` (東京リージョン APAC cross-region inference profile)
- デフォルトリージョン: `ap-northeast-1`
- バージョニング: 各 Repo は `main` pin
- 初の利用側: lifetech-business-perf-api
