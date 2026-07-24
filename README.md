# Safe-to-Fail Doctrine

このpublic repositoryは、Agent operationが参照するcanonicalな
Safe-to-Fail Doctrineを所有する。

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

この境界は、invocation内でDoctrine取得Evidenceを保持することを禁止しない。
deliveryへ残すEvidenceは、target自身の入力、runtime firing、validation、artifact、
または観測結果に限定する。

## Skill packages

- implementation planning: [`skills/doctrine-planner/`](skills/doctrine-planner/)
- standard and terminology selection: [`skills/prefer-standards/`](skills/prefer-standards/)
- installed copies: Agent runtimeが読み込むlocal cache

packageの変更はrepository側を先に更新し、testsとskill validationを通した同一内容を
installed copyへ反映する。installed copyだけの変更は記録済みとみなさない。

## Current edition

- version: 4
- language: Japanese (`ja`)
- status: canonical

## License

MIT License。詳細は[`LICENSE`](LICENSE)を参照。
