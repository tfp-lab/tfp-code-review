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

## 使い方 (新しい Repo に導入する場合)

[**AI_SETUP.md**](AI_SETUP.md) を上から順に実行するだけ。

人間の手でやる場合も、AI に丸投げする場合も、このページが正本。
構成を変更したら、**まず AI_SETUP.md を更新**。次回以降の作業者 (人 or AI) が新しい手順で動く。

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
