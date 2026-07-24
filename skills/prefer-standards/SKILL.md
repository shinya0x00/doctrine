---
name: prefer-standards
description: Prefer industry or de facto standards and established original names before custom mechanisms or coined terminology. Use when designing, reviewing, or renaming domain concepts, protocols, schemas, APIs, event or record formats, statuses, verdicts, commands, identifiers, errors, public vocabulary, or other abstractions; when a proposal introduces a custom mechanism, metaphor, alias, or project-specific term; or when checking whether code and documentation use official names consistently. Do not use for product branding, ordinary copyediting, or merely reading an existing glossary without deciding a concept boundary, mechanism, or name.
---

# Prefer Standards

関連するprior artが存在すると仮定する。custom mechanismを設計する前にstandardを調べ、名前のあるconceptには確立されたoriginal nameを使う。新語と独自形式には、採用側ではなく発明側へ立証責任を置く。

## Canonical control source

判断を伴うinvocationの開始時に、次のcanonical sourceを解決する。

- discovery pointer: `https://github.com/shinya0x00/doctrine/blob/main/DOCTRINE.md`
- head API path: `repos/shinya0x00/doctrine/git/ref/heads/main`
- content API path: `repos/shinya0x00/doctrine/contents/DOCTRINE.md?ref=<exact-commit-sha>`

`main`のcommit SHAを一度だけ取得し、そのexact commitから`DOCTRINE.md`を全文読む。そのrunでは同じSHAを固定し、「発明よりstandardを、新語より既存名を優先する」というRuleの規則・確認・非目的をcontrol sourceとして使う。

Doctrineのtitle、repository、URL、commit SHA、Rule番号はinvocation内部にだけ保持する。targetのREADME、DESIGN、ADR、schema、code comment、CLI output、reportなどへ投影しない。targetには、調べたprior art、具体的なcapability gap、採用理由、正式名称などtarget固有の根拠だけを残す。

sourceの解決または全文取得に失敗した場合、新しいcustom mechanismまたはpublic termを正当化しない。不足しているEvidenceを示し、その判断に依存しない作業だけを続ける。

## Workflow

### 1. 名前を外して要件を定義する

候補名や既存案をいったん外し、必要なbehavior、data、boundary、invariant、interoperability、互換性を普通の言葉で記述する。

repositoryを扱う場合は、先にcode、schema、public API、README、DESIGN、既存の用語集を検索し、会話上の説明ではなく現在の実態を確認する。同じ語が複数の意味を持つ場合は、standard探索前に意味ごとの境界事例を作る。

### 2. prior artをread-onlyで調べる

対象分野に応じて、次を優先して調べる。

1. standards bodyのnormative specificationと公式registry
2. de facto standardの公式specification、reference、registry
3. 対象platformまたはecosystemの公式convention
4. 広く実装されたmatureなprior art
5. target repositoryの既存convention

技術情報はprimary sourceを優先し、現行version、正式名称、extension point、適用範囲を確認する。検索結果の件数や名前の類似だけでstandardとみなさない。

### 3. semanticsとcapabilityを比較する

各candidateについて、次を比較する。

- authorityとcanonical reference
- standardが実際に定義するsemantics
- requirementを満たす部分
- 満たさない具体的なcapability
- officialなextension、profile、registry、vendor extensionの余地
- interoperability、migration、maintenanceへの影響

比較には必要に応じて[prior-art review template](references/prior-art-review.md)をscratchで使う。targetに既存のDecision形式がある場合は、その形式を優先する。

「用途が特殊」「柔軟性が足りない」「将来困る」など、観測可能な差へ分解されていない理由でstandardを棄却しない。

### 4. 最も狭いcustomizationを選ぶ

- requirementを満たすstandardがある場合、そのまま採用する。
- core semanticsが一致する場合、standardのprofileまたはextensionとして表現する。
- custom designが必要な場合、最も近いstandardを土台にできない具体的理由を残す。
- 無関係なstandardを権威付けのbadgeとして追加しない。

既存実装の置換コストが高い場合、正しいtermへの即時renameだけを答えにしない。canonical term、compatibility alias、deprecation、migration boundaryを分けて提案する。

### 5. 名前を選ぶ

次の順で選ぶ。

1. standard、registry、protocol、platformが定めるofficial nameまたはmachine token
2. 対象分野で意味が確立したoriginal name
3. 既存語を組み合わせた、意味をそのまま説明する名前
4. 既存語では誤解を避けられない場合だけ新語

正式名称、identifier、schema key、field name、status、verdict、command、path、exact errorを翻訳または言い換えない。日本語では、そのtokenの意味と選択理由を説明する。

新語を選ぶ場合は、必ず次を残す。

- 一文の定義
- 検討した既存語
- 各既存語が誤りになる具体的なsemantics
- 普通の説明的な複合語では足りない理由
- public surfaceへ追加する必要性

product、company、campaignなどのbrand namingはこのSkillの対象外とする。ただしbrand名をprotocol token、status、field nameへ流用するときは対象に含める。

### 6. public vocabularyを点検する

次のどれかに該当する場合、既存名への置換を優先する。

- 一般的なconceptを理解する前にproject固有語を覚える必要がある
- ecosystemで同じ意味を持つ語を別名にしている
- 内部の比喩がpublic API、CLI、schema、statusへ漏れている
- 一つの造語から派生語が連鎖している
- glossaryが、避けられたaliasを解読するためだけに必要になっている
- 独自用語への同意が、機能を使う前提になっている

既存名を採用してもtarget固有の差が消えるとは限らない。差は名前ではなく、profile、constraint、extension、configuration、または明示的なbehaviorとして表す。

### 7. canonical ownerだけを更新する

userが変更を依頼している場合だけmutationする。既存のDESIGN、ADR、schema、API specification、glossaryなどから、そのFactを所有するartifactを特定し、そこだけをcanonicalに更新する。他の文書は必要なreferenceまたはProjectionとして合わせる。

`CONTEXT.md`、独自の用語集形式、独自のDecision形式を自動作成しない。既存のcanonical ownerがない場合は、targetで既に使われている最も近いartifactを選ぶか、materialな選択ならownerを確定してから記録する。

単純なrenameごとにADRを増やさない。custom mechanism、public contract、互換性、長期migrationなど、理由とtrade-offを将来保持する必要がある判断だけを、target既存のDecision方式で記録する。

### 8. 結果を短く提示する

最初に推奨案を示し、その後に次を必要な量だけ示す。

- 採用するstandardまたはestablished term
- canonical reference
- requirementとのfit
- 残るcapability gap
- profile、extension、custom designの必要性
- 避けるaliasとmigration上の扱い
- Evidence不足または未確認事項

custom designまたは新語を認める場合は、比較した候補と棄却理由を省略しない。standardを採用する場合は、不要な独自概念や用語を何個減らせるかも示す。

## Boundaries

- 構築そのものを禁止しない。最初から自作することを避ける。
- standardへの完全一致を目的化しない。要件を満たさない差は隠さない。
- standardを見つけたことと、targetへ適用できることを同一視しない。
- established termを使うために、異なるconceptを同じものとして潰さない。
- user-facingな日本語説明までofficial Englishだけにしない。
- reviewまたは説明だけを依頼された場合、artifactを変更しない。
