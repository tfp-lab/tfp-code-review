---
applyTo: "**/*.go"
description: "Go コードのレビュー観点 (Effective Go / Google Go Style / Go Code Review Comments / Uber Go Style Guide を統合)"
---

# Go コードレビュー観点

このファイルは frontmatter で指定した通り **Go ファイル (`**/*.go`)** にのみ適用されます。
全社共通方針は `/.tfp/code-review/prompts/CLAUDE.md`、Repo 固有ルールは `/.tfp/review.md` を参照。

レビュアーは以下を **重要度順** に確認し、該当があればコメントしてください。
各項目に `[must-fix]` / `[suggestion]` / `[nit]` を付けて優先度を明示します。

---

## 1. エラーハンドリング (must-fix が多い領域)

- `if err != nil { return ..., err }` の直後に `else` を書かない。早期 return パターン
- エラーラップは `fmt.Errorf("context: %w", err)`。`%v` ではアンラップ不能
- 比較は `==` ではなく `errors.Is`、型アサーションは `errors.As`
- `panic` をライブラリ / リクエストハンドラ内で使わない (init / プログラマエラー検出を除く)
- エラーを **黙って捨てない** (`_ = doSomething()` は意図明示時のみ)
- カスタムエラー型は sentinel error (`var ErrXxx = errors.New(...)`) を活用

## 2. 命名

- **パッケージ名**: 短く、すべて小文字、アンダースコア / キャメルケース不可
- **ファイル名**: `snake_case.go`
- **エクスポート識別子**: `CamelCase`、非エクスポートは `camelCase`
- **頭字語 (HTTP / URL / ID / API)**: 全部大文字 or 全部小文字で統一 (`UserID` ◎, `UserId` ✗)
- **getter は `Get` を付けない** (`user.Name()` ◎, `user.GetName()` ✗)
- **interface に `-er` 接尾辞** (`Reader`, `Writer`)。1 メソッド interface を推奨
- ローカル変数はスコープが狭ければ `i`, `r`, `err` で十分

## 3. インターフェース

- **利用側 (consumer) で定義** する。実装側でエクスポート interface を先に定義しない
- **最小化**: メソッドが多い interface は分割
- **`interface{}` (any) の濫用回避**。型パラメータで表現できるなら generics
- 戻り値で interface、引数で具体型 (Postel's law)

## 4. 並行性 (goroutine / channel / sync)

- **goroutine のライフサイクル必須管理**。「いつ終わるか」不明な goroutine は禁止 ([must-fix])
- `context.Context` を **第一引数** で渡す (`func Do(ctx context.Context, ...) error`)
- `context.Background()` をライブラリ関数内で生成しない。呼び出し側から受け取る
- race condition の疑いがあれば `go test -race` を推奨
- `sync.Mutex` はゼロ値で使える。`new(sync.Mutex)` 不要
- channel の close は **送信側** で
- `select` の default 節を漫然と置かない (busy loop 原因)

## 5. defer / リソース解放

- ファイル / コネクション / ロックは取得直後に `defer Close()` / `defer Unlock()` ([must-fix])
- **ループ内 defer に注意**。関数を切り出して各イテレーションで return
- `defer` の引数は **defer 文の評価時点** で確定

## 6. 構造体

- **コンストラクタ `New*` パターン** で初期化を集約 (Repo 固有 convention 推奨)
- ポインタ vs 値レシーバの **一貫性**: 同 struct のメソッドはどちらかに統一
- mutating method はポインタレシーバ
- 大きい struct / interface 実装はポインタレシーバ
- タグ順 (json / db / validate) は既存ファイルに揃える
- ゼロ値で使えない struct は `New*` 経由で生成するよう docstring に明記

## 7. テスト

- **テーブル駆動テスト** が基本 (`tests := []struct{...}{ ... }`)
- `t.Helper()` を helper 関数の冒頭で
- 独立したテストは `t.Parallel()`
- assert ライブラリ選定はリポジトリ既存方針に従う (混在禁止)
- mock は **interface 経由** で差し替え。テスト用 struct 分岐ロジック禁止
- DB を伴うテストはトランザクションロールバック or testcontainers

## 8. context の扱い

- 関数の **第一引数** で受け取る (`ctx context.Context`)
- struct の field に context を保持しない (アンチパターン)
- `context.WithValue` の濫用回避。リクエストスコープのトレース情報など限定的に
- `ctx.Done()` を確実に監視。長時間処理 / ループ内では中断点

## 9. マジックナンバー / マジックストリング

- 意味のある定数は **必ず命名** して `const` 化
- HTTP ステータスコードは `http.StatusOK` 等の constant (`200` 直書き禁止)
- エラーメッセージで使う文字列も sentinel error / const 化

## 10. import 順とフォーマット

- `goimports` でグルーピング: 標準 → サードパーティ → 自プロジェクト の 3 ブロック
- 各ブロックは空行区切り
- `gofmt -s` で simplifying できる箇所は適用 (`s[a:len(s)]` → `s[a:]`)

## 11. ロギング

- 機微情報 (パスワード / トークン / 個人情報) を生でログ出力しない ([must-fix])
- 構造化ログ (key=value / JSON) 推奨
- リクエスト処理では trace id / request id をログに含める

## 12. SQL / DB アクセス

- **プレースホルダ必須** (`?` / `$1`)。文字列連結による SQL 構築は SQL injection ([must-fix])
- N+1 クエリの兆候 (ループ内 SELECT) を検出したら指摘 ([must-fix] or [suggestion])
- トランザクション境界を明確に。`defer tx.Rollback()` パターン推奨
- `sql.NullString` 等の null 対応型は entity 層で適切に

## 13. セキュリティ

- 入力バリデーション (型 / 範囲 / 形式) を境界で必ず
- 認可チェック (オブジェクトレベル) の漏れを疑う
- `crypto/rand` を使う。`math/rand` をセキュリティ用途で禁止 ([must-fix])
- ファイルアップロードは MIME / サイズ / パストラバーサル対策
- 外部 HTTP には timeout 必須 (`http.Client.Timeout`)

## 14. プロジェクト固有 convention

Repo 固有の convention は `/.tfp/review.md` を参照してください。
代表的なパターン:

- 「新規ファイルは interface + struct + `New*()` の 3 点セット」
- 「特定ディレクトリは段階的書き換え中で旧スタイル混在 OK」

これらは Repo 固有ファイルに書くのが原則であり、本共通ファイルには書きません。

---

## レビューコメントのテンプレート

```
[must-fix] L42: SQL を文字列連結で組み立てています。プレースホルダ (`?`) を使ってください。

理由: SQL injection の脆弱性。
修正案:
    db.Query("SELECT * FROM users WHERE id = ?", userID)
```

```
[suggestion] L88: ループ内で defer を使っています。

理由: ループの最後までリソースが解放されません。
修正案: 関数に切り出して各イテレーションで return。
```

```
[nit] L120: 変数名 `tmp` より `parsedAt` の方が意図が伝わります。
```
