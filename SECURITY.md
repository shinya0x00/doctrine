# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| `main` | Yes |

このrepositoryは、Agent operationが参照するDoctrine、skill package、plan linter、
およびGitHub Actions workflowを公開する。公開repositoryであるため、公開情報だけで
到達できる入力と、pull requestから実行される未信頼コードを脅威モデルに含める。

## Threat Model and Trust Boundaries

- pull request由来のtest codeは未信頼であり、repository credentialや不要な権限を取得できない。
- plan pathとplan JSONはcallerが与える入力であり、ファイル境界、サイズ、解析深度を越えてはならない。
- GitHub Actionsは必要最小限のread権限で実行し、checkout credentialをtest codeへ残さない。
- mainの変更はpull request経由に限定し、削除やnon-fast-forwardの変更を許可しない。

## Security Invariants

- secret、token、private keyをsource、artifact、log、公開記録へ露出しない。
- path、symlink、特殊ファイル、巨大入力、解析エラーは安全側の結果で処理する。
- explicit authorizationのないprivileged operation、destructive mutation、default branchへのdirect pushを実行しない。
- workflow、action、dependencyの変更は、公開された変更履歴と成功した自動検査を通す。

## Reportable Findings and Severity Context

次の問題は、到達可能性と影響を添えて報告対象とする。

- credential、token、private key、secretの露出または不要な権限付与
- path traversal、symlink traversal、unsafe file handling、bounded resource controlの欠落
- pull request codeへのworkflow credential、権限、network authorityの意図しない露出
- action、dependency、source provenanceの検証を回避する経路
- authorizationなしのrepository mutation、default branch保護の迂回、destructive operation

テストの意味的な網羅性、自然言語の品質、security certificationの不在だけでは、単独の
security findingとはしない。ただし、それが上記のtrust boundaryやsecurity invariantを
壊す場合は報告対象になる。

## Reporting a Vulnerability

GitHubのprivate vulnerability reportingを使って、非公開で報告する。

- 公開Issue、公開discussion、公開PRへ脆弱性の詳細を書かない。
- 再現条件、影響範囲、対象revision、最小限の再現手順、回避策をprivate reportに含める。
- 実際のsecretや個人情報は貼らず、無害化した値を使う。
- 報告への返信や修正状況は、GitHubのprivate report内で扱う。

## Out of Scope and Known Limitations

- 現行rulesetはpull requestと`test`成功を要求するが、独立したreview承認は要求しない。
- このrepositoryはsecurity certification、compliance certification、独立review、署名済みreleaseを保証しない。
- Doctrineやskillの自然言語が期待どおり解釈されること自体は、linterの構造検査だけでは保証しない。
- 上記の制限は、secret露出、unsafe path、workflow権限逸脱、未承認mutationの報告を除外しない。
