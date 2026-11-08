# Unity ＋ 公式 PLATEAU SDK 導入メモ

> **現状: このリポジトリに Unity プロジェクトはありません。Unity を使うかどうかも未定です。**
> このメモは、Unity を使うと決めたときの手順と確認項目です。採用が決まるまで、プロジェクトの作成や SDK の導入はしません。
> Unity と SDK のバージョンは**推測で決めず**、導入する時点で公式の情報を確認して記録します。

---

## 1. 導入前に決めること

| 項目 | 決定内容 | 確認した資料・日付 |
| --- | --- | --- |
| Unity を使うか | 未定 | |
| Unity のバージョン（エディタ） | 未定 | PLATEAU SDK for Unity の README・リリースノートの動作環境 |
| PLATEAU SDK for Unity のバージョン | 未定 | [PLATEAU SDK for Unity（GitHub）](https://github.com/Project-PLATEAU/PLATEAU-SDK-for-Unity) のリリース |
| レンダーパイプライン（Built-in / URP / HDRP） | 未定 | SDK の対応状況 |
| ビルド先（Windows / Mac / WebGL / スマホ） | 未定 | SDK と Unity の対応状況 |
| プロジェクトの置き場所 | 未定（案: `unity/`） | |

## 2. 導入手順（採用が決まってから）

1. 上の表を埋める。SDK の README で、対応する Unity のバージョンと導入方法を確認する。
2. Unity Hub で、決めたバージョンのエディタを入れる。
3. 決めた置き場所に新しいプロジェクトを作る。
4. プロジェクトを開いたら、まず「3. 確認項目」の設定をして、**SDK を入れる前に**一度コミットする。
5. SDK の README に書かれた方法で SDK を入れる。
6. SDK で、対象地域（[prototype-plan.md](prototype-plan.md) の前提）の建物を読み込んで表示する。
   - 読み込んだ都市モデルのファイルが大きい場合は、コミットしない（[data-management.md](data-management.md)）。
7. `Packages/manifest.json` と `Packages/packages-lock.json` の差分を確認してコミットする。
8. 使ったバージョンを、下の「記録」に書く。

## 3. 確認項目（チェックリスト）

- [ ] Unity のバージョンを `ProjectSettings/ProjectVersion.txt` で確認し、チーム全員が同じバージョンを使う
- [ ] Project Settings → Editor → Version Control の Mode が **Visible Meta Files**
- [ ] Project Settings → Editor → Asset Serialization の Mode が **Force Text**
- [ ] `.gitignore` に Unity の生成物（下の「5」）を追加した
- [ ] 新しいプロジェクトを、別のフォルダに clone して開き直しても、エラーなく開ける
- [ ] SDK で対象地域の建物を読み込み、シーンに表示できる
- [ ] 画面に出典表記（PLATEAU など）を入れる場所を決めた

## 4. Git で管理するもの

| 管理する | 説明 |
| --- | --- |
| `Assets/` | 自分で作ったスクリプト・シーン・素材。**各ファイルの `.meta` も必ず一緒にコミットする** |
| `Packages/manifest.json`・`Packages/packages-lock.json` | 使っているパッケージとバージョン |
| `ProjectSettings/` | プロジェクトの設定（Unity のバージョンもここに入る） |

`.meta` についての注意:

- `.meta` には、ファイル同士のつながり（参照）を保つための ID が入っている。消したり、本体だけコミットしたりすると、シーンやプレハブの参照が切れる。
- ファイルの移動や名前の変更は、Unity エディタの中で行う（`.meta` も一緒に動く）。
- 本体を消したら、対応する `.meta` も消す。

大きなファイル:

- SDK で取り込んだ都市モデルのメッシュやテクスチャは大きくなりやすい。配信元から作り直せるなら、コミットせずに手順を残す。
- 作品に必須で作り直せない大きな素材は、Git LFS を検討する（[data-management.md](data-management.md) の「5」）。

## 5. 除外する生成物（.gitignore に追加する内容）

Unity プロジェクトを `unity/` に作った場合の例です。置き場所を変えたら、先頭のフォルダ名を合わせます。

```gitignore
# Unity が自動で作るもの
/unity/[Ll]ibrary/
/unity/[Tt]emp/
/unity/[Oo]bj/
/unity/[Bb]uild/
/unity/[Bb]uilds/
/unity/[Ll]ogs/
/unity/[Uu]ser[Ss]ettings/
/unity/MemoryCaptures/

# IDE が作るもの
/unity/.vs/
/unity/.idea/
/unity/*.csproj
/unity/*.sln
/unity/*.suo
/unity/*.user

# ビルド成果物
*.apk
*.aab
*.unitypackage
```

## 6. 記録（導入したら書く）

| 項目 | 値 | 記録日 |
| --- | --- | --- |
| Unity エディタ | 未導入 | |
| PLATEAU SDK for Unity | 未導入 | |
| レンダーパイプライン | 未導入 | |
| 読み込んだ地域・データ | 未導入 | |
