# Changelog

すべての変更はこのファイルに記録する。形式は [Keep a Changelog](https://keepachangelog.com/) に準拠。

## [Unreleased]

## [0.3.1] - 2026-05-20

### Fixed
- workflow が `Either ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN is required` で失敗する不具合を修正
  - 原因: action の `use_bedrock` を `with:` ではなく env (`CLAUDE_CODE_USE_BEDROCK`) で渡していたため、`anthropics/claude-code-action@v1` が Bedrock モードと認識せず、デフォルトの API キー認証パスに落ちていた
  - 修正: `with: use_bedrock: "true"` に変更。`AWS_BEARER_TOKEN_BEDROCK` は workflow の job env で渡す形に整理 (action が env から自動で読み取る)
  - モデル ID は `claude_args: --model ${{ env.ANTHROPIC_MODEL }}` で渡すように変更 (action は `ANTHROPIC_MODEL` env を直接参照しない)

### Added
- AI_SETUP.md トラブルシューティングに以下のエラー対処を追加
  - `Either ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN is required` (workflow テンプレ古い)
  - `403 Authorization header is missing` (Bearer Token 空文字)
- 認証方式を AI_SETUP.md に明記 (Bedrock API Key / Bearer Token、OIDC は不使用)

### Notes
- `anthropics/claude-code-action@v1` は公式 docs では Bedrock = OIDC のみと記載されているが、実装上は `AWS_BEARER_TOKEN_BEDROCK` をネイティブサポート (`base-action/src/validate-env.ts` 参照)。本リポジトリはこの実装挙動に依存

## [0.3.0] - 2026-05-20

### Changed
- リポジトリを **public** に変更 (consumer 側 GitHub Actions が `GITHUB_TOKEN` で submodule clone 可能になるため)
- README に「公開リポジトリ運用上の注意」セクションを追加:
  - コミットしてはいけない情報 (NG リスト 7 カテゴリ)
  - コミットしてよい情報 (OK リスト)
  - コミット前のセルフチェックコマンド
  - Branch protection 推奨設定
  - 第三者 PR への対応方針
  - Public 化を取り止める場合の影響
- README 冒頭に PUBLIC バナー
- Contribution / ライセンスセクションを Public 前提に書き直し

### Notes
- このリリース時点で機密情報の漏洩なしを確認済み (`grep -i secret/password/api_key` クリア)
- 一度 public にした内容は git history を含めて取り戻せないため、以降は NG リストの順守必須

## [0.2.2] - 2026-05-20

### Changed
- HTML 配置を `_html/` (gitignore) → **`docs/` (git 管理)** に変更。配布用は `docs/` のみで一本化
- `scripts/md2html.py` の CSS を全面刷新 (Linear / Anthropic docs 風)。indigo accent / Inter + Hiragino / 引用ブロックの callout 化 / テーブル radius / モバイル最適化 / `text-wrap: balance` / `prefers-color-scheme: dark` 強化
- `scripts/md2html.py` に `--out-dir` オプション追加 (出力ディレクトリ指定)

### Fixed
- 0.2.1 の `_html/` を git 追跡する判断を撤回 (試し生成と公開用が混在していた)。`docs/` を公開専用に分離

## [0.2.1] - 2026-05-20

### Changed
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
