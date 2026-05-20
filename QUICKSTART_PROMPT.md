# QUICKSTART_PROMPT.md — 一発導入プロンプト + Fallback コマンド

> 「自分の Repo にもこの構成入れたい」と思った瞬間、**このページから 1 つコピペすれば終わる** ようにするのが目的です。

---

## 0. これは何?

このページは 2 種類の "コピペ素材" を提供します。

1. **Section A**: AI / LLM (Claude Code / Cursor / Copilot Chat 等) に **丸投げするための日本語プロンプト**
2. **Section B**: AI が動かない / 手元で全部やりたい人用の **bash コマンド一式**

どちらも、(★) tfp-code-review に追加変更があればこのページが正本として更新されます。古い手順を信じないでください。

---

## Section A — AI に丸投げする (推奨)

### A-1. このまま貼るだけ

ターゲット Repo のルートで AI チャット (Claude Code / Cursor / Copilot Chat) を開き、以下を **そのままコピペ** してください。

````
このリポジトリに TFP 共通レビュー基盤 (tfp-code-review) を導入してください。
正本の手順書は GitHub の以下です。最初にこれを必ず取得して読んでから作業してください。

  https://raw.githubusercontent.com/tfp-lab/tfp-code-review/main/AI_SETUP.md

要件:
- submodule として `.tfp/code-review` に取り込む
- `workflows/claude-review.yml` を `.github/workflows/claude-review.yml` にコピー
- このリポジトリ固有のルールは `.tfp/review.md` に書く (空でも作成)
- 作業内容を `git add` + `git commit` まで実施。`git push` はしないで人間に確認を取る

このリポジトリの主言語と特殊事情は私 (人間) に確認してください。
わからない場合は本ページの Section B (bash コマンド一式) を参照して
forced-mode で実行しても構いません。
````

これで AI は AI_SETUP.md を読み、submodule 追加 → workflow コピー → `.tfp/review.md` 作成 → commit までやってくれます。

### A-2. もう少しお節介なバージョン (AI に推測させたくない)

````
このリポジトリに TFP 共通レビュー基盤 (tfp-code-review) を導入してください。

正本: https://raw.githubusercontent.com/tfp-lab/tfp-code-review/main/AI_SETUP.md

実行ステップ:
1. 上記 URL の AI_SETUP.md を取得して読む
2. このリポジトリの言語構成を git ls-files の拡張子から推定し、私に確認
3. AI_SETUP.md の手順を実行 (submodule 追加 / workflow コピー / .tfp/review.md 作成)
4. `.tfp/review.md` には以下を書き込む
   - 主言語
   - 特殊事情 (独自フレームワーク・レガシー領域・除外ルール) — 私に質問しながら埋める
   - PR コミット規約 — 既存 git log のパターンを参考に提案
5. commit までやって push はしない

途中でわからなくなったら本ページ (QUICKSTART_PROMPT.md) の Section B を参照。
````

### A-3. 既存導入済み Repo で「最新の共通ルールに追従」だけしたい

````
このリポジトリには既に `.tfp/code-review` submodule があります。
共通ルールを最新版に追従させてください。

実行:
1. git submodule update --remote .tfp/code-review
2. tfp-code-review の最新 CHANGELOG.md を確認し、Breaking 変更があれば私に報告
3. `.tfp/review.md` の内容が共通ルール変更と矛盾していないか軽く点検
4. git add .tfp/code-review && git commit -m "Update tfp-code-review submodule"
````

---

## Section B — bash コマンド一式 (AI 不要)

AI が動かない / シェルだけで完結したい場合の手順。**ターゲット Repo のルートで実行** してください。

### B-1. 新規導入 (まだ submodule 入っていない Repo)

```bash
# 1. submodule 追加
git submodule add https://github.com/tfp-lab/tfp-code-review.git .tfp/code-review
git submodule update --init --recursive

# 2. workflow をコピー
mkdir -p .github/workflows
cp .tfp/code-review/workflows/claude-review.yml .github/workflows/claude-review.yml

# 3. .tfp/review.md を作成 (最低限のテンプレ)
mkdir -p .tfp
cat > .tfp/review.md <<'EOF'
# $(basename "$PWD") 固有のレビュールール

このリポジトリでは特殊事情なし。共通ルールに従う。

(必要に応じて以下を埋める)

## 言語
<Go / TypeScript / PHP …>

## 追加ルール

## 除外ルール
EOF

# 4. commit (push は手動で確認してから)
git add .gitmodules .tfp .github/workflows/claude-review.yml
git commit -m "Add tfp-code-review submodule for Claude PR review"

# 5. (任意) push して PR を出す
# git push -u origin <your-branch>
# gh pr create --title "Add Claude PR review" --body "Setup via tfp-code-review"
```

### B-2. 共通ルール追従 (既に導入済み)

```bash
git submodule update --remote .tfp/code-review
git add .tfp/code-review
git commit -m "Update tfp-code-review submodule"
git push
```

### B-3. workflow がコピー先と古くなっていないか確認

```bash
# テンプレと現行 workflow を diff
diff .tfp/code-review/workflows/claude-review.yml .github/workflows/claude-review.yml
```

差分が「env (model / region) のカスタマイズだけ」なら OK。それ以外の構造的な差があれば、テンプレ最新版を取り込み直す:

```bash
# モデル指定だけ保存して再コピー
cp .github/workflows/claude-review.yml /tmp/claude-review.yml.bak
cp .tfp/code-review/workflows/claude-review.yml .github/workflows/claude-review.yml
# /tmp/claude-review.yml.bak を見て env だけ手で書き戻す
```

### B-4. アンインストール

```bash
git submodule deinit -f .tfp/code-review
git rm -f .tfp/code-review
rm -rf .git/modules/.tfp
git rm -f .gitmodules .github/workflows/claude-review.yml .tfp/review.md
git commit -m "Remove tfp-code-review submodule"
```

---

## Section C — 動作確認チェックリスト

導入後、以下を確認:

- [ ] `.gitmodules` に `[submodule ".tfp/code-review"]` が記録されている
- [ ] `cat .tfp/code-review/AI_SETUP.md` でドキュメントが読める
- [ ] `cat .github/workflows/claude-review.yml` で workflow が存在
- [ ] `cat .tfp/review.md` でファイルが存在 (空でも OK)
- [ ] リポジトリ Settings → Secrets に `AWS_BEARER_TOKEN_BEDROCK` が登録済み
- [ ] テスト PR を 1 本出してレビューコメントが付くこと

---

## Section D — 困ったらここを見る

| 症状 | 対処 |
|---|---|
| AI が AI_SETUP.md を読めない (権限なし) | tfp-code-review が public でないなら一時的に Section B の bash で手動 |
| submodule init が SSH エラー | URL を https:// に揃える: `git config -f .gitmodules submodule.".tfp/code-review".url https://github.com/tfp-lab/tfp-code-review.git` |
| `.tfp/review.md` のテンプレが古い | tfp-code-review の `examples/consumer-repo/.tfp/review.md` を見る |
| Workflow が動かない | `gh run list -L 5` でログ確認、Actions タブで失敗メッセージを見る |

それ以外は [AI_SETUP.md](AI_SETUP.md) §6 トラブルシューティングへ。

---

## Section E — このページ自体の更新ルール

tfp-code-review の構成を変更したら、**このページも一緒に更新** してください。とくに:

- AI_SETUP.md の手順が変わったら、Section A の指示文を見直す
- bash コマンドの順序が変わったら Section B を更新
- Breaking 変更時は CHANGELOG.md にも追記

このページが古いと、AI / 人間とも壊れた手順で動きます。**docs と code は同じ PR で同期** が原則。
