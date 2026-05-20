# Changelog

すべての変更はこのファイルに記録する。形式は [Keep a Changelog](https://keepachangelog.com/) に準拠。

## [Unreleased]

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
