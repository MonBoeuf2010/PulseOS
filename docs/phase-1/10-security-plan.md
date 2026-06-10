# 10 — Security & Compliance Plan

> Security is not a feature of PulseOS; for the enterprise segment it **is** the product (`03` P5). A single tenant-crossover or meeting leak is company-ending. This plan is written to pass a hostile CISO review.

## 1. Threat model (who attacks us, and why)

| Threat actor | Goal | Primary defenses |
|---|---|---|
| External attacker | Steal user/corporate data, ransom | Zero-trust, encryption, WAF, least privilege, monitoring |
| Malicious tenant/user | Cross-tenant access, scrape others' data | Strict tenancy isolation (RLS + app + vector), authz tests |
| **Prompt-injection via ingested content** | Hijack agents, exfiltrate context, poison outputs | Untrusted-content handling, instruction/data separation (see `07`) |
| Misinformation/brigading actor | Manipulate community intelligence/reputation | Verification, reputation, AI moderation, rate limits, anomaly detection |
| Insider | Misuse access to user/corporate data | Least privilege, audit logging, access reviews, just-in-time access |
| Account takeover | Hijack a user/company account | MFA, WebAuthn, device fingerprinting, session/IP anomaly detection |

## 2. Tenancy isolation (the non-negotiable, day-one requirement)

The brief is explicit: *no shared vector databases, no tenant crossover, strict isolation.* Implementation, defense-in-depth:

1. **Logical isolation by default** with `tenant_id` on every row + **Postgres Row-Level Security** enforced at the DB, not just the app. App bugs cannot bypass RLS.
2. **Vector isolation:** embeddings carry `tenant_id`; every similarity query is tenant-scoped. **No cross-tenant vector search, ever.** Public-signal embeddings live in a separate, explicitly-public namespace (safe to share; contain no private data).
3. **AI context isolation:** an agent prompt for tenant A can never contain tenant B's data; memory/retrieval is tenant-keyed; gateway enforces context scoping.
4. **Enterprise tier:** optional **physical isolation** — dedicated DB/schema, dedicated namespaces, or fully private deployment (VPC/single-tenant) for the highest-bar customers.
5. **Automated isolation tests** in CI: adversarial tests that *attempt* cross-tenant reads/searches and must fail. Isolation is continuously verified, not assumed.

## 3. Zero-trust architecture
- No implicit trust by network location; every request authenticated + authorized.
- Service-to-service auth (mTLS / signed tokens) internally.
- Least-privilege IAM; short-lived credentials; just-in-time elevation for human access.
- Segmented network; private subnets for data stores; no public DB exposure.

## 4. Identity, authN, authZ
- **AuthN:** email + OAuth (Google/Apple); **MFA** (TOTP MVP) → **WebAuthn / hardware keys** (R2, required for enterprise/sensitive connectors).
- **AuthZ:** **RBAC** with org/team/role model from day 1; resource-level checks; deny-by-default. ABAC where needed (e.g., meeting-level access).
- **Sessions:** short-lived tokens + refresh; device fingerprinting; **IP/session anomaly detection**; forced re-auth on risk signals; remote session revocation.

## 5. Data protection
- **At rest:** AES-256 (DB, backups, object storage, search). KMS-managed keys; per-tenant key options for enterprise.
- **In transit:** TLS 1.3 everywhere, internal included.
- **Secrets:** AWS Secrets Manager + **rotation**; no secrets in code/images; scanned in CI.
- **Field-level encryption** for the most sensitive personal/financial data.
- **Data minimization:** collect only what powers a recommendation; prefer derived signals over raw sensitive data; default retention limits.

## 6. AI-specific security (expands `07` §6)
- Treat **all ingested/community/web content as untrusted data, never instructions**; strict instruction/data separation; output validation.
- Tool/action allow-listing; **no autonomous high-impact actions** without explicit user confirmation.
- Prompt-injection + jailbreak **red-team suite** in CI; monitored in prod.
- PII redaction before sending to model providers where feasible; provider data-processing terms vetted (no training on our data); **provider isolation** honored.
- Output guardrails: no leaking of system prompts, other tenants' data, or chain-of-thought containing sensitive context.

## 7. Application security
- WAF (managed rules + custom); rate limiting per IP/user/endpoint; bot/DDoS mitigation (CloudFront/Shield).
- OWASP Top 10 controls; input validation; parameterized queries (no raw SQL with user input); output encoding (XSS); CSRF protection; secure headers/CSP.
- Dependency + container scanning (SCA), SAST, secret scanning, **DAST** pre-release — all in CI.
- Signed artifacts; SBOM; supply-chain controls (the brief flags supply-chain as a no-go for *us to perform*; here it's *defending against* supply-chain attacks on us).

## 8. Audit logging & monitoring
- **Immutable, tamper-evident audit log** of security-relevant + data-access events (who accessed what tenant data, when, why).
- Centralized logging + SIEM; alerting on anomalies; **detection of unusual access patterns** (insider + external).
- Sentry for app errors; Prometheus/Grafana for security SLOs; on-call + incident runbooks.

## 9. Privacy & compliance roadmap

| Standard | When | What it requires from us |
|---|---|---|
| **GDPR / CCPA** | MVP (architecture-aligned) | Lawful basis + consent for personal connectors; **right to access/edit/delete** (already a product feature via AI memory); data export; DPA; data-processing register; breach notification process |
| **SOC 2 Type II** | R4 (start controls early) | 6–12 mo observation window → start control discipline at MVP so the clock can run |
| **ISO 27001** | R4+ | ISMS, risk register, control set |
| **Sector (e.g., finance/health)** | only if we enter regulated verticals | Avoid until deliberately chosen |

- **Privacy by design + default.** Inspect/edit/delete memory is both a UX trust feature and a compliance control (deletions propagate to embeddings/search/backups per policy).
- **Data residency** options for enterprise (regional deployments at Stage 3/4).
- **No data sale; no training on customer data by providers** (contractually enforced).

## 10. Governance & process
- Security owner from early (fractional/advisor pre-funding; dedicated hire by ~Series A — see `13`).
- Periodic **third-party pen tests** (before enterprise sales; then annually).
- Vulnerability disclosure / bug bounty (R2+).
- Access reviews quarterly; least-privilege audits; offboarding checklist.
- **Incident response plan** with severity tiers, comms templates, and post-mortems (blameless).

## 11. The brutally honest security caveats
- **Personal financial data raises the stakes enormously.** If/when we ingest bank/brokerage data, the blast radius of a breach is severe. Recommendation: **delay deep financial-data ingestion until security maturity (and ideally SOC2) is real**; start with lower-sensitivity signals. The MVP can deliver value (cost-of-living, industry, calendar, public-finance signals) without holding the crown-jewels data.
- **Compliance is a multi-quarter effort.** Do not promise SOC2/ISO before the controls + observation window exist. Start the *discipline* at MVP so the clock can run; claim the *certification* only when earned.
- **The biggest realistic breach vector is prompt injection + over-trusted AI actions.** This is novel, under-tooled, and where we must invest disproportionately.
