---
applyTo: "**/*.{ts,tsx}"
description: "TypeScript / TSX コードのレビュー観点 (雛形)"
---

# TypeScript コードレビュー観点

> 雛形。本格運用する Repo が出てきたら充実させます。
> 全社共通方針は `/.tfp/code-review/prompts/CLAUDE.md`、Repo 固有は `/.tfp/review.md`。

## 1. 型安全性

- `any` を新規追加しない。やむを得ない場合は `unknown` + narrowing
- `as` キャストは最小限。原則 type guard / `instanceof` で narrowing
- non-null assertion (`!`) は避ける。`?.` / `??` を使う

## 2. async / Promise

- async 関数は必ず Promise を return か await。投げっぱなし禁止
- `Promise.all` / `Promise.allSettled` の使い分けを意識
- await 漏れ (Promise が宙に浮いている) を [must-fix]

## 3. null / undefined

- API 境界で型を厳密に。`string | null` / `string | undefined` を曖昧にしない
- optional chaining と nullish coalescing を活用

## 4. import / モジュール

- 相対パスの深さ (`../../../`) が深いと `tsconfig` の paths を検討
- barrel file (`index.ts`) は循環依存の温床になりがち。注意

## 5. React (TSX 限定)

- 大量再レンダリングを起こす useState / useEffect 依存配列の誤りを指摘
- key prop の脱落
- inline 関数の再生成によるメモ化破壊
- accessibility (ARIA / alt 属性) の欠落

## 6. テスト

- Jest / Vitest / Playwright どれを使っているかは Repo 依存
- mock の使い過ぎを警告 (実装の詳細に依存しすぎないか)

## 7. セキュリティ

- `dangerouslySetInnerHTML` (XSS リスク)
- `eval` / `Function` constructor
- ユーザー入力を URL / fetch にそのまま埋め込み

詳細は将来追記予定。
