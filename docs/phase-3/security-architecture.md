# Phase 3 — Complete Security Architecture

> Authored from four seats: **CISO** (risk & program), **SOC 2 auditor** (control evidence), **GDPR/CCPA consultant** (privacy & rights), **Security architect** (controls & design). Cross-references Phase 1 §10 (security plan) and Phase 2 (schema/RLS). This is the document that must survive a hostile enterprise security review.

---

## 0. Security principles
1. **Zero trust** — no implicit trust by network, identity verified every request, least privilege everywhere.
2. **Defense in depth** — isolation enforced at app *and* DB (RLS) *and* infra (network) layers; no single control is load-bearing.
3. **Secure by default** — deny-by-default authz; encryption on by default; MFA available day one, enforced for sensitive scopes.
4. **Assume breach** — minimize blast radius (segmentation, short-lived creds, per-tenant keys), detect fast, recover cleanly.
5. **Privacy by design** — data minimization, purpose limitation, user-controlled memory, deletion as a first-class workflow.

---

## 1. Authentication

### 1.1 Methods
| Method | Use | Notes |
|---|---|---|
| Password | consumer fallback | **Argon2id** (memory-hard), per-user salt, pepper in KMS; breach-password check (HIBP k-anonymity); min entropy policy |
| OAuth/OIDC (Google, Apple) | consumer primary | PKCE; validate `iss`/`aud`/`nonce`; no implicit flow |
| **Passkeys / WebAuthn** | phishing-resistant primary (R2) | platform + roaming authenticators; resident keys; user-verification required |
| SAML/OIDC SSO + SCIM | enterprise | per-IdP config; JIT provisioning; SCIM deprovision on offboard |
| TOTP | second factor | RFC 6238; encrypted secret (pgcrypto/KMS); drift window ±1 |
| Recovery codes | break-glass | one-time, hashed, regenerated on use |

### 1.2 Token model
- **Access token:** JWT, ~15 min, asymmetric (EdDSA/RS256), claims `{sub, tid, roles, scopes, amr, sid, exp}`; **`amr`** records auth methods (for step-up decisions); signed by a key from the rotating JWKS.
- **Refresh token:** opaque, high-entropy, **rotating** (one-time use; reuse detection → revoke entire session family = token theft signal), stored only as SHA-256 hash, httpOnly+Secure+SameSite cookie or secure native store.
- **No long-lived tokens in browsers.** Service-to-service uses short-lived mTLS-bound tokens.

### 1.3 MFA & step-up
- MFA enrollable by all; **enforced** for: admin roles, enterprise tenants (policy), sensitive scopes (financial connectors, data export/delete, billing changes, meeting access).
- **Step-up auth (`amr` re-check)** required for high-risk actions even within a valid session.
- Risk-based: anomalous IP/device/geo velocity → force re-auth/MFA.

---

## 2. Authorization — RBAC + ABAC

### 2.1 RBAC (coarse)
Roles per tenant membership: `owner > admin > member > viewer`. Roles map to **permission sets** (e.g., `briefing:read`, `member:invite`, `billing:manage`, `meeting:create`, `moderation:decide`, `audit:read`). Deny-by-default; permissions are additive; checked at the API boundary **and** in the service.

### 2.2 ABAC (fine-grained)
Attribute-based policy for resource-level decisions RBAC can't express:
- Subject attributes: `role`, `dept`, `clearance`, `mfa_level`, `tenant_id` (from `memberships.attributes` + token).
- Resource attributes: `owner_id`, `visibility`, `access_policy` (e.g., meeting participant list), `tenant_id`, `regulated_flag`.
- Environment: `ip_risk`, `device_trust`, `time`, `geo/residency`.
- **Policy engine:** centralized decision (OPA/Cedar-style) — `permit(subject, action, resource, env)`; policies versioned, tested, audited. Example: *a meeting is readable only if `subject ∈ resource.access_policy.participants` AND `subject.mfa_level ≥ required` AND `subject.tenant_id = resource.tenant_id`.*

### 2.3 Database-enforced tenancy (defense in depth)
RBAC/ABAC live in the app; **RLS in Postgres is the backstop** so an app bug cannot leak across tenants. Every tenant-scoped table: `USING (tenant_id = current_setting('app.tenant_id')::uuid)`. The connection pooler sets `app.tenant_id` per transaction; a separate audited `break_glass` role is the only RLS bypass. **Adversarial cross-tenant tests run in CI and must fail-closed** (a passing cross-tenant read fails the build).

### 2.4 Enterprise permissions
- Custom roles, permission delegation, group/team scoping, resource sharing within tenant, data-room style access for meetings/broadcasts.
- SCIM-driven group→role mapping; admin audit of every grant; periodic access reviews (quarterly, evidenced for SOC2 CC6).

---

## 3. Session management
- Sessions tracked server-side (`sessions` table + Redis) for **revocation** (JWT alone can't be revoked → short TTL + session check on sensitive ops).
- Device fingerprinting + IP/geo + UA stored; **risk score** per session.
- **Anomaly responses:** impossible-travel, new device, IP reputation, concurrent-geo → step-up, notify user, or revoke.
- User-visible **active sessions** list with one-tap remote revoke; "log out everywhere".
- Idle + absolute timeouts; refresh-reuse detection nukes the session family.

---

## 4. Encryption & key management

### 4.1 At rest
- **AES-256** for all stores: Postgres (TDE / encrypted EBS + column-level `pgcrypto` for the most sensitive fields), backups, S3 (SSE-KMS), OpenSearch, Redis (at-rest enabled).
- **Per-tenant data keys (envelope encryption):** each tenant has a KMS CMK (`tenants.kms_key_id`); tenant data keys wrapped by the CMK. Enables **crypto-shredding**: destroy the tenant key → tenant data is irrecoverable (powerful GDPR-erasure + backup-deletion primitive).
- Field-level encryption for: MFA secrets, financial connector tokens, meeting recordings, PII flagged columns.

### 4.2 In transit
- **TLS 1.3** externally (HSTS, OCSP stapling, modern ciphers only); **mTLS** for service-to-service internally; no plaintext on any hop, including to data stores.

### 4.3 Key rotation
| Key | Rotation | Mechanism |
|---|---|---|
| KMS CMKs (tenant/data) | annual + on-demand | AWS KMS automatic rotation; re-wrap data keys |
| JWT signing (JWKS) | 90 days, overlap | dual-key publish; old key valid until tokens expire |
| Refresh/session secrets | continuous (rotating) | per-use rotation |
| DB/service credentials | ≤90 days | Secrets Manager rotation lambdas |
| TLS certs | automated | ACM auto-renew |
- **Crypto-agility:** algorithms behind config; rotation runbooks tested; no key in code or images ever.

### 4.4 Secret management
- **AWS Secrets Manager + KMS**; no secrets in env files committed, images, or logs.
- Secret scanning in CI (gitleaks) + pre-commit; rotation on suspected exposure; least-privilege IAM to read each secret; short-lived dynamic DB creds where possible.

---

## 5. Audit logging
- **Append-only, tamper-evident** `audit_log` (Phase 2): **hash-chained** (`row_hash = H(prev_hash || row)`) so deletion/modification is detectable; periodic anchor of the chain head to immutable store (S3 Object Lock / WORM).
- Logged: authn events, authz denials, data access to sensitive resources, admin/break-glass actions, exports/deletions, permission changes, config changes, security anomalies.
- Each entry: `actor, action, target, tenant, ip, ua, trace_id, ts`. **No secrets/PII payloads** in logs (tokenized).
- Retention ≥ 7y (compliance); access restricted (`audit:read`), itself audited. Centralized SIEM ingestion.
- **SOC 2 mapping:** provides evidence for CC7 (monitoring), CC6 (access), CC8 (change).

---

## 6. Threat detection & response
- **SIEM** correlation: auth anomalies, RLS-denied spikes, unusual data-access volume (exfil), privilege escalation attempts, geo/impossible-travel, brute force, token-reuse.
- **Detections (examples):** N failed logins → lockout + alert; refresh-token reuse → session-family revoke + alert; one principal reading many tenants → page on-call; mass export → step-up + review.
- **Behavioral baselining** per user/tenant; deviations raise `security.anomaly` events → automated response (step-up/revoke) + analyst queue.
- **IR plan:** severity tiers, on-call rotation, comms templates (incl. breach-notification clocks: GDPR 72h), blameless post-mortems, tabletop exercises quarterly.
- Vulnerability mgmt: continuous dependency/container scanning (SCA), SAST, DAST pre-release, secret scanning, annual third-party pen test + bug bounty (R2).

---

## 7. DDoS mitigation & edge defense
- **AWS Shield Advanced + CloudFront/WAF** at the edge: L3/L4 absorption, L7 rules (OWASP CRS + custom), bot control, geo/IP reputation blocking.
- **Rate limiting** layered: edge (WAF), gateway (per-IP), app (per-user/tenant/endpoint, Redis token bucket), and expensive-endpoint quotas (AI generation).
- Autoscaling + load shedding; circuit breakers; anycast; cost-control caps so an attack can't bankrupt us (AI endpoints especially — abuse of council generation is both a DoS *and* a cost attack).
- Anti-automation: CAPTCHA/Turnstile on signup/abuse-prone flows; account-takeover protections (credential-stuffing detection via velocity + breached-cred checks).

---

## 8. Privacy controls, data retention & deletion (GDPR/CCPA)

### 8.1 Legal basis & rights
- Lawful basis documented per processing purpose (consent for personal connectors; contract for service; legitimate interest for security — with balancing test).
- **Data subject rights as product features:** access/export, rectification (edit memory), erasure (delete), portability, restriction, objection; consent management + withdrawal; DPA + sub-processor register; ROPA maintained.

### 8.2 Retention schedule (default; tenant-configurable for enterprise)
| Data | Retention | Then |
|---|---|---|
| Signals (public) | 18 mo hot | archive/aggregate, drop raw |
| Personal connector data | minimal, purpose-bound | delete on disconnect + on erasure |
| Briefings/opportunities | rolling window + user-controlled | prune |
| Meetings | configurable (default 12 mo) | delete / crypto-shred per policy |
| Audit log | ≥7 y | WORM cold |
| Backups | 35 days PITR + periodic | crypto-shred via key destruction |

### 8.3 Deletion workflow (the hard part: backups + embeddings + search)
```
user.deletion_requested
  → verify identity + scope (self / tenant-admin authority)
  → orchestrator fan-out:
     • Postgres: cascade delete owned rows (RLS-scoped); tombstone where law requires record-of-erasure
     • Embeddings (pgvector): delete vectors for user/tenant items
     • OpenSearch: delete-by-query (tenant+user filter), force-merge
     • Object storage (recordings/exports): delete + version purge
     • Caches/Redis: purge keys
     • Backups: cannot selectively delete → **crypto-shred** (destroy per-tenant/per-user data key) so backup ciphertext is unrecoverable
  → emit signed deletion receipt (data_deletion_requests.receipt), retained as lawful proof
  → SLA: acknowledge ≤72h, complete ≤30 days (GDPR), receipt to user
```
- **Crypto-shredding** resolves the "right to erasure vs. immutable backups" conflict: we destroy keys, not backup tapes.
- Audit-log entries about a person are **minimized/tokenized**, retained as a compliance record of the erasure (a recognized exception to erasure).

### 8.4 Data residency & sub-processors
- `tenants.region` drives storage region; enterprise can pin EU/US residency (Stage 3 regional deployments).
- Model providers vetted: **no training on our data**, DPA in place, PII redaction before send, sub-processor list published + change-notified.

---

## 9. Every major attack vector (threat catalog)

| # | Vector | Surface | Primary controls |
|---|---|---|---|
| 1 | **Cross-tenant data access** | API/DB/vector/search | RLS + ABAC + mandatory tenant filters + CI isolation tests + per-tenant keys |
| 2 | **Prompt injection / indirect prompt injection** | ingested web/community/meeting content into agents | treat ingested content as untrusted *data* not instructions; instruction/data separation; tool allow-list; no autonomous high-impact actions; output validation; injection red-team in CI |
| 3 | **Account takeover** (credential stuffing, phishing) | auth | passkeys, MFA, breached-cred checks, velocity limits, anomaly detection, step-up |
| 4 | **Session/token theft** | tokens, XSS | short TTL, rotating refresh + reuse detection, httpOnly cookies, CSP, mTLS internal |
| 5 | **Broken authorization (IDOR/BOLA)** | object-level access | ABAC object checks + RLS; deny-by-default; contract + fuzz tests on every `/{id}` route |
| 6 | **Injection (SQLi/NoSQLi/command)** | inputs | parameterized queries/ORM, input validation, no string-built SQL, least-priv DB roles |
| 7 | **XSS / CSRF** | web | output encoding, strict CSP, SameSite cookies, anti-CSRF tokens, Trusted Types |
| 8 | **SSRF** | connectors/web fetch | egress allow-list, block link-local/metadata (169.254.169.254), DNS-rebinding guards, isolated fetch egress |
| 9 | **Supply chain** (deps, images, build) | CI/CD | pinned deps + lockfiles, SCA, SBOM, signed artifacts, provenance (SLSA), least-priv CI, no untrusted actions |
| 10 | **Secrets exposure** | repos/logs/images | Secrets Manager, scanning, rotation, no secrets in logs |
| 11 | **DDoS / cost-exhaustion (LLM)** | edge + AI endpoints | Shield/WAF, layered rate limits, generation quotas, cost caps, circuit breakers |
| 12 | **Insider / privilege misuse** | admin/db | least privilege, JIT access, break-glass audited, separation of duties, access reviews |
| 13 | **Data exfiltration** | bulk reads/exports | volume anomaly detection, export step-up + audit, egress monitoring, DLP on exports |
| 14 | **Model data leakage** | provider calls | redaction, no-train contracts, output guardrails (no system-prompt/other-tenant leakage), provider isolation |
| 15 | **Misinformation / manipulation / brigading** | community network | verification scoring, reputation weighting, AI moderation + appeals, rate/velocity limits, sybil resistance |
| 16 | **Meeting data leakage** | corporate/meetings | strict ABAC, per-tenant keys, participant-scoped access, encrypted media, watermarked exports |
| 17 | **Webhook spoofing/replay** | inbound (Stripe)/outbound | HMAC signatures, timestamp + nonce, idempotency, allow-listed IPs |
| 18 | **Phishing / social engineering** | humans | passkeys (phishing-resistant), security training, verified-domain comms, admin action confirmations |
| 19 | **Business-logic abuse** | free-tier/cost | fair-use caps, abuse detection, anti-automation, per-tenant quotas |
| 20 | **Physical/cloud-config** | infra | IaC + policy-as-code (no public buckets/DBs), CSPM, private subnets, encrypted everything, guardrail SCPs |

---

## 10. SOC 2 / ISO 27001 control mapping (program plan)
- **Start controls at MVP** so the SOC 2 Type II observation window (6–12 mo) can run before enterprise sales (R4).
- Trust Services Criteria coverage: **CC1** governance/policies, **CC2** comms, **CC3** risk assessment (this doc + Phase 1 risk), **CC4** monitoring, **CC5** control activities, **CC6** logical/physical access (authn/authz/RLS/MFA/reviews), **CC7** system operations/incident (SIEM/IR), **CC8** change management (CI/CD gates, IaC, code review), **CC9** risk mitigation/vendors (sub-processors, pen tests).
- ISO 27001: ISMS, risk register, Statement of Applicability, control set — R4+.
- Evidence is **automated** where possible (access reviews, scan results, audit logs, CI gates) so audits are continuous, not fire drills.

## 11. Security program & ownership
- Security ownership from day one (founder/fractional CISO → dedicated CISO by enterprise entry / Series A).
- Quarterly: access reviews, pen test (pre-enterprise then annual), tabletop IR, key-rotation drills, policy review.
- Vulnerability disclosure + bug bounty (R2). Vendor security reviews for all sub-processors.
- **Bright line:** defer deep financial-data ingestion until SOC 2 + maturity (Phase 1 §10 caveat) — the blast radius doesn't justify the early risk.
