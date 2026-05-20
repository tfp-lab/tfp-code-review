---
applyTo: "**/*.php"
description: "PHP コードのレビュー観点 (雛形)"
---

# PHP コードレビュー観点

> 雛形。本格運用する Repo が出てきたら充実させます。
> 全社共通方針は `/.tfp/code-review/prompts/CLAUDE.md`、Repo 固有は `/.tfp/review.md`。

## 1. 型宣言

- 引数 / 戻り値の型宣言 (PHP 7.4+) を活用。スカラー型 hint も
- `declare(strict_types=1);` をファイル冒頭に推奨

## 2. エラー処理

- 例外を握り潰さない (`catch (Exception $e) {}` は禁止)
- 例外型を具体化 (`Throwable` / `Exception` の濫用を避ける)
- `@` (suppress) 演算子を新規追加しない

## 3. SQL

- **PDO のプレースホルダ必須** (`?` / `:name`)。文字列連結 SQL は [must-fix]
- 検索条件の動的構築でプレースホルダを忘れないか
- N+1 クエリの兆候

## 4. セキュリティ

- XSS: 出力時の `htmlspecialchars` / template engine のエスケープ
- CSRF: フォーム送信に token があるか
- ファイルアップロード: MIME / サイズ / 拡張子チェック
- パストラバーサル: `realpath` / ホワイトリスト
- session 固定攻撃対策 (login 後の `session_regenerate_id`)

## 5. PSR / Coding Standard

- PSR-12 準拠 (Linter で機械修正できるものは指摘しない)
- composer の autoload (PSR-4) で名前空間とディレクトリ構造一致

## 6. テスト

- PHPUnit / Pest どちらを使うかは Repo 依存
- DB を伴うテストはトランザクション or fixture リセット

## 7. フレームワーク (Laravel / Symfony / 独自)

- 該当する場合は `/.tfp/review.md` で詳細を補足

詳細は将来追記予定。
