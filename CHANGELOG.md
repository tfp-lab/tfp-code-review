# Changelog

すべての変更はこのファイルに記録する。形式は [Keep a Changelog](https://keepachangelog.com/) に準拠。

## [Unreleased]

## [0.7.2] - 2026-05-20 (Hotfix)

### Fixed
- `Repository path '/home/runner/work/_temp/tfp-code-review' is not under '$GITHUB_WORKSPACE'` で reusable workflow が失敗していた問題を修正
  - 原因: 0.7.1 で tfp-code-review を `path: ${{ runner.temp }}/tfp-code-review` に置こうとしたが、`actions/checkout@v4` は `$GITHUB_WORKSPACE` 配下にしかチェックアウトできない仕様
  - 修正: tfp-code-review を workspace 内のサブディレクトリ `_tfp-code-review/` に変更
  - 2 度目の checkout が caller のファイルを消さないよう `clean: false` を追加
  - prompt 内の参照パスを `_tfp-code-review/...` に統一

## [0.7.1] - 2026-05-20 (Hotfix)

### Fixed
- `fatal: not a git repository (or any of the parent directories): .git` で reusable workflow が失敗していた問題を修正
  - 原因: 0.7.0 で caller を `path: caller` でサブディレクトリにチェックアウトしていたため、`$GITHUB_WORKSPACE` 直下に `.git` が無く、claude-code-action が `git fetch` 等で 128 エラーを起こしていた
  - 修正: caller リポジトリは workspace ルートにチェックアウト、tfp-code-review は `${{ runner.temp }}/tfp-code-review` に切り出し
  - prompt 内のパス参照を絶対パス (`${{ runner.temp }}/...`) と workspace ルート相対 (`.tfp/review.md`) に修正

## [0.7.0] - 2026-05-20 (BREAKING)

### BREAKING / Architecture
- **submodule 方式 → Reusable workflow 方式に全面移行**
  - 動機: 共通改修のたびに各 Repo で submodule pointer 更新 + workflow 全文コピーの二重 push が必要だった
  - v0.7 では各 Repo は **約 25 行の caller workflow** だけ持ち、`uses: tfp-lab/tfp-code-review/.github/workflows/review.reusable.yml@main` で本基盤を呼び出す
  - 共通改修は tfp-code-review main を更新するだけで **全 Repo に即反映**
  - 各 Repo で submodule (`.tfp/code-review/`) と `.gitmodules` は **不要**

### Added
- `.github/workflows/review.reusable.yml` (Reusable workflow 本体): `workflow_call` で外部から呼び出し可能。inputs で model / region 上書き可、secrets で `AWS_BEARER_TOKEN_BEDROCK` を inherit
- `workflows/claude-review.yml` を新規 Repo にコピーする 25 行の caller テンプレに置き換え
- 移行手順を AI_SETUP.md / QUICKSTART_PROMPT.md に追加 (v0.6 → v0.7)

### Changed
- AI_SETUP.md: ターゲット Repo の最終形を「caller 1 ファイル + .tfp/review.md」に簡素化
- README.md: アーキテクチャ図を Reusable workflow 構成に更新
- USAGE.md: 「共通基盤の更新を取り込む」を「何もしなくて OK」に書き換え

### Migration (v0.6 から)
利用側 Repo で:
```bash
git submodule deinit -f .tfp/code-review
git rm -f .tfp/code-review
rm -rf .git/modules/.tfp
curl -fsSL https://raw.githubusercontent.com/tfp-lab/tfp-code-review/main/workflows/claude-review.yml \
  -o .github/workflows/claude-review.yml
git add -A && git commit -m "Migrate to tfp-code-review v0.7"
```

## [0.6.0] - 2026-05-20

### Added
- **インラインレビュー対応** (CodeRabbit 風): prompt で `mcp__github_inline_comment__create_inline_comment` の利用を必須化。must-fix / suggestion レベルの具体指摘は差分行に直接 post される。サマリコメントは目次・件数のみ
- **`<details>` 折りたたみ表示**: must-fix は `open` 属性で展開、suggestion / nit は折りたたみ。長いレビューでも見やすい
- **件数を見出しに表示** (例: 🔴 must-fix (3 件)) で全体感が即座に把握可能
- **長いコメントの自動分割**: 60,000 文字を超える場合、final rebrand step が段落単位で chunk 分割し、続きを別コメントとして post (`> 📄 NoraBot レビュー (続き 2/3)` ヘッダ付き)
  - 1 段落だけで上限超のときはハード切り
- **同種指摘の集約ルール** を prompt に追加 (3 件以上は代表 + 行番号リスト)

### Changed
- アイコン URL を **tfp-code-review main 固定 URL** に変更 (PR head SHA 依存だと private リポジトリで 404 する可能性)
- prompt にアイコン省略禁止を強調 (「最初の 2 行は必ず以下」と冒頭固定)

### Fixed
- レビュー本体が 60,000 文字を超えた際にコメント切り詰めで指摘が消えていた問題 → 分割 post で全件残る

## [0.5.1] - 2026-05-20

### Added
- **リアルタイム rebrand watcher**: Run NoraBot step の **前** に bash バックグラウンドプロセスを起動し、`Claude Code is working…` が PR コメントに出た瞬間 (~2 秒以内) に `NoraBot is reviewing…` へ書き換える。Claude 実行中にユーザーが Claude 表記を見続ける問題を解消
- watcher は Run NoraBot 完了後の Stop watcher step で kill。watcher のログは Actions ログにも出力 (debug 用)
- 最終 rebrand step は backup として残し、置換ルールを強化:
  - `Claude Code is working…` → `NoraBot is reviewing…` を最優先
  - `Claude Code Action` → `NoraBot` 追加
  - 1 件で break せず全該当コメントを置換

### Notes
- bash 並列実行 (`nohup ... &` + PID 記録) を使うため、self-hosted runner / Windows runner では動作未保証 (ubuntu-latest 前提)
- 完全 CodeRabbit 風 (アバター・bot 名変更、`pulls.createReview` API 利用) には GitHub App 化が必要なため未対応

## [0.5.0] - 2026-05-20

### Added
- **NoraBot ブランディング post-job rebrand step**: action が出力する `"Claude finished @user's task"` 等の固定文言を実行後に文字列置換 (`actions/github-script@v7` で 30 件直近コメントから github-actions[bot] のトラッキングコメントを特定し更新)
  - 置換対象: `Claude finished` → `NoraBot finished`、`Claude encountered an error` → `NoraBot encountered an error`、`Claude Code is working` → `NoraBot is working`、`Generated with [Claude Code](https://claude.ai/code)` → `Generated with NoraBot`
- **Copilot 風レビューフォーマット** をデフォルトプロンプトに採用:
  - 重要度ラベルに絵文字 (🔴 must-fix / 🟡 suggestion / 🔵 nit)
  - サマリ / 指摘事項 / 良かった点 の 3 ブロック構造
  - フッターに「Reviewed by NoraBot (Claude Sonnet 4.6 via AWS Bedrock)」のクレジット行

### Notes
- bot のアバター画像と GitHub UI 上の名前 (`github-actions[bot]`) は **GitHub App 化なしには変更不可** (技術的制約)。コメント本文先頭のアイコン + 「## NoraBot のレビュー」見出し + フッタークレジットで識別性を確保
- post-job step は `if: always()` で実行されるため、レビュー本体が失敗しても rebrand は試みる
- 既存コメントが残っている PR では新規コメントだけ rebrand される (既存は手動置換が必要なら `gh issue edit` 等で)

## [0.4.5] - 2026-05-20

### Fixed
- `App token exchange failed: 401 Unauthorized - Claude Code is not installed on this repository` エラーを解消
  - 原因: 0.4.3 で `github_token` 入力を削除した結果、action は OIDC 経由で **公式 Claude GitHub App** (https://github.com/apps/claude) の token を取得しようとする実装になっていた。consumer 側 Repo にこの App が install されていない場合は 401 で失敗
  - 修正: workflow テンプレに `github_token: ${{ secrets.GITHUB_TOKEN }}` を復活
  - 副作用: コメント投稿者は `github-actions[bot]` になり、Claude App ブランディング (`claude[bot]` 名乗り) は使えない。コメント本文のアイコン画像 + "NoraBot のレビュー" ヘッダで識別する方針

### Notes
- 公式 FAQ の「github_token: Only include this if you're connecting a custom GitHub app」は **Claude App を install 済みの環境前提** の表現で、未 install リポジトリではむしろ必須

## [0.4.4] - 2026-05-20

### Fixed
- 0.4.3 で `id-token: write` を削除したまま `github_token` も削除したため、action が OIDC token 交換に失敗して即死する不具合を修正
  - 原因: action のソース (`src/github/token.ts:setupGitHubToken()`) は `github_token` 入力が空のとき `core.getIDToken()` で OIDC token を取得する実装。これには `id-token: write` permission が必須
  - 修正: `permissions:` に `id-token: write` を復活
  - 0.4.3 の「`id-token: write` 削除」は誤った最適化だったため取り消し

### Notes
- `github_token` を渡さない方が Claude App ブランディング (`claude[bot]` 名乗り + sticky/tracking 機能) が正しく動く
- どうしても `id-token: write` を許容できない環境では、代替として `github_token: ${{ secrets.GITHUB_TOKEN }}` を `with:` に追加する選択肢あり (ただし `github-actions[bot]` 名で post され UX が劣化)

## [0.4.3] - 2026-05-20

### Fixed
- 「Action は走るが PR に何も表示されない」「進捗が見えない」問題を抜本対処
  - 原因 1: `use_sticky_comment` は `pull_request` event 限定で `issue_comment` では効かない (公式 docs.usage.md 明記)
  - 原因 2: `permission_denials_count: 2` が CI ログに出ており、Claude が PR コメント投稿用 MCP ツールを呼んだが allowlist 未指定で拒否されていた
  - 原因 3: `github_token: ${{ secrets.GITHUB_TOKEN }}` を渡すと `github-actions[bot]` 名で動き、sticky/tracking 機能の前提 (`claude[bot]`) が崩れる (FAQ 明記)
- 修正:
  - `track_progress: "true"` を追加 → tag mode + tracking comment を強制。「NoraBot is working...」的な進捗コメントが即座に post され、完了後にレビュー本文へ更新される (issue_comment / pull_request 両対応)
  - `claude_args` に `--allowedTools mcp__github_comment__update_claude_comment,mcp__github_inline_comment__create_inline_comment,Bash(gh pr view:*),Bash(gh pr diff:*),Bash(gh api:*)` を追加
  - `github_token` 入力を削除 (公式 FAQ「Only include this if you're connecting a custom GitHub app」)
  - prompt に「**必ず `mcp__github_comment__update_claude_comment` を呼べ**」と明示
- `use_sticky_comment: "true"` は削除 (issue_comment では効かないため track_progress に置き換え)

## [0.4.2] - 2026-05-20

### Fixed
- `@norabot review` での再レビュー時、PR の差分ではなく default branch がレビューされていた問題を修正
  - 原因: `actions/checkout@v4` に `ref` 未指定だと issue_comment トリガー時に default branch を checkout する仕様
  - 修正: `actions/github-script@v7` で PR head SHA を API 取得し、checkout の `ref` に渡す `Resolve PR head SHA` step を追加
- アイコン URL が default branch SHA を指していた問題を修正 (issue_comment 時 `github.event.pull_request.head.sha` が null になる)
  - 修正: 上記 `steps.prsha.outputs.result` を使うよう変更
- 不要な `id-token: write` 権限を削除 (Bearer Token 認証では OIDC を使わないため)

### Removed
- `env.REVIEWER_ICON_URL` (icon step 内で組み立てる方式に統一したため不要)

## [0.4.1] - 2026-05-20

### Fixed
- レビューが PR コメントとして表示されない不具合を修正
  - 原因: `use_sticky_comment` 未設定 (デフォルト `false`) では action は inline comment しか post せず、Claude が `mcp__github_inline_comment__create_inline_comment` を呼ばない場合は `No buffered inline comments` で終了し PR に何も書かれていなかった。CI 自体は success ステータスで終わるため検出が難しい
  - 修正: workflow に `use_sticky_comment: "true"` を追加。Claude の最終出力テキストを 1 件の通常 PR コメント (issue comment) として post するモードに切替
- `if:` 条件を簡略化。GitHub Actions の `contains()` は case-insensitive のため `@norabot` 1 つで `@NoraBot` `@NORABOT` 全部マッチ。`@NoraBot` の重複条件を削除

## [0.4.0] - 2026-05-20

### Added
- レビュアーに **NoraBot** という呼称を導入。トリガーは `@norabot` (大文字小文字どちらでも OK)
- workflow に `trigger_phrase: "@norabot"` 入力を追加 (action 側のメンション検出を独自フレーズに切替)
- 出力フォーマット冒頭に「`# NoraBot のレビュー`」見出しを追加
- prompt に「**通常 PR コメント (issue comment) として 1 件 post せよ**」を明記 — inline 専用だと PR トップに表示されない問題を回避

### Changed
- workflow の `name:` を「NoraBot PR Review (Bedrock)」に変更
- `prompts/CLAUDE.md` の役割記述を NoraBot ベースに書き換え
- `USAGE.md` の `@claude` 言及を `@norabot` に置換
- 出力先頭の画像 alt を `reviewer` → `NoraBot`

### Notes
- bot 自体のアバター (GitHub 上の `github-actions[bot]`) は **GitHub App 化なしには変更不可**。表示名 / アバターは引き続き github-actions[bot]、ただしコメント本文は NoraBot 名乗り + アイコン画像 markdown で識別可能
- 既存 `@claude` で投稿されたコメントは **トリガーされなくなる** ので注意

### Migration (利用側 Repo)
1. `git submodule update --remote .tfp/code-review`
2. `cp .tfp/code-review/workflows/claude-review.yml .github/workflows/claude-review.yml` (workflow を最新版に更新)
3. commit & push

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
