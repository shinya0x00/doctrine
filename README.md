# Safe-to-Fail Doctrine

このpublic repositoryは、Agent operationが参照するcanonicalな
Safe-to-Fail Doctrineを所有する。

## Intended use

これは、個人または小規模チームがGitHub中心の開発で、Agent operationへ
opt-inで適用するためのDoctrineである。GitHubをsourceとし、
正準の本文は日本語で記述し、適用先のcurrent designは`DESIGN.md`、
materialな判断はADRが所有することを、現在の意図的な前提とする。

ここで`canonical`とは、この運用で参照する唯一のsource authorityであることを
意味する。成熟度、security certification、compliance certificationを意味しない。
GitLab、Jira、air-gapped環境などへの可搬性は現在の保証範囲に含まない。

## Canonical source

- discovery pointer: [`main/DOCTRINE.md`](https://github.com/shinya0x00/doctrine/blob/main/DOCTRINE.md)
- activation: pull requestによる`main/DOCTRINE.md`の更新merge
- run snapshot: invocation開始時に観測した`main`のexact commit SHA

consumerはGitHub APIで`main`のHEAD SHAを一度だけ取得し、
`DOCTRINE.md?ref=<exact-commit-sha>`を全文取得する。そのrunでは同じSHAを
Doctrine版としてconsumer内部のinvocation stateに固定する。

Doctrineのtitle、repository、URL、exact commit SHA、`doctrine_ref`、Rule番号は、
implementation targetのspecification、README、Decision、Record、CLI output、
acceptance artifact、またはdelivery artifactへ投影しない。consumerはRuleを、
target固有のscope、implementation order、attachment point、validation、
stop condition、unknown、completion conditionへ変換する。

moving refである`main`は最新版を発見するpointerであり、runのEvidence reference
ではない。HEAD解決またはexact-ref取得に失敗したconsumerは、
そのplanning transitionを内部で停止し、source identityをtargetへ投影しない。
取得済みのstale snapshotへの自動fallbackはしない。停止するのはこのsourceに
依存するtransitionだけであり、依存しない作業まで停止する理由にはならない。

この境界は、invocation内でDoctrine取得Evidenceを保持することを禁止しない。
deliveryへ残すEvidenceは、target自身の入力、runtime firing、validation、artifact、
または観測結果に限定する。

### Trust and provenance boundary

各invocationは開始時点の最新`main`を信頼して採用する。exact commit SHAへの固定が
保証するのは、同じrunの途中で本文がすり替わらないことだけである。そのcommitが
承認済みか、安全か、別のrunも同じ版を使うかまではこの仕組みだけでは保証しない。

source identityやexact SHAはinvocation内にだけ保持し、targetの永続artifactへは残さない。
そのため、target artifactのみからcross-runでpolicy versionを復元するprovenance auditは
現在サポートしない。それが必要な運用では、別のアクセス制御された監査設計が必要になる。

## Current assurance

現在のassuranceは、pull requestによる変更管理と、このrepositoryに含まれる自動テストである。
独立したreview、署名済みrelease、release policy、後方互換性の保証は現在は提供しない。
これらを必須とする組織的なgovernanceやsecurity boundaryとしての利用は対象外である。

## Skill packages

- implementation planning: [`skills/doctrine-planner/`](skills/doctrine-planner/)
- standard and terminology selection: [`skills/prefer-standards/`](skills/prefer-standards/)
- installed copies: Agent runtimeが読み込むlocal cache

packageの変更はrepository側を先に更新し、testsとskill validationを通した同一内容を
installed copyへ反映する。installed copyだけの変更は記録済みとみなさない。
installed copyは実行用のcacheであり、このrepositoryがcanonical sourceである。

## Planner linter boundary

`doctrine-planner`のlinterは、planの構造とfield type、exact source referenceの形、
implementation optionの参照関係、milestoneの順序、runtime attachmentの接続を
決定論的に検査する。`verdict: proceed`は、これらの機械的な条件を満たしたという
Evidenceである。

一方で、optionが実際に同じacceptance conditionを満たすか、選択が最も単純か、
complexityの理由が真実か、validationが実行可能か、runtimeが発火したか、あるいは
作業が安全に完了したかは証明しない。lint通過は、planの正しさや完了そのものの
代わりにはならない。

## Validation

repository rootで次を実行する。追加dependencyは必要ない。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/doctrine-planner/scripts -v
```

[`test.yml`](.github/workflows/test.yml)は、pull requestと`main`へのpushで同じテストを実行し、
型崩れを含む既知のlinter regressionを自動的に検出する。CIの成功はこのテスト範囲の
Evidenceであり、Doctrine全体の意味的な正しさやgovernanceを証明するものではない。

## Current edition

- version: 4
- language: Japanese (`ja`)
- status: canonical

## License

MIT License。詳細は[`LICENSE`](LICENSE)を参照。
