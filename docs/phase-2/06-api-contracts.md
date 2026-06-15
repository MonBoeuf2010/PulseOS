# Phase 2.6 — API Contracts (overview)

The machine-readable contract lives in [`openapi.yaml`](./openapi.yaml). This doc gives the conventions and the surface map; the YAML is authoritative.

## Conventions
- **Base:** `https://api.lifeiq.com/v1`. Versioned in path; breaking changes → `/v2` with overlap window.
- **Auth:** `Authorization: Bearer <access_jwt>` (short-lived, ~15 min). Refresh via `POST /auth/refresh` (rotating refresh token, httpOnly cookie or secure store). Service tokens for internal callers.
- **Tenancy:** active tenant from the JWT `tid` claim; switch via `X-Tenant-Id` (must be a tenant the user is a member of; validated + audited).
- **Content type:** `application/json`; cursor pagination (`?cursor=&limit=`), never offset at scale.
- **Idempotency:** mutating POSTs accept `Idempotency-Key` header (stored 24h) → safe retries.
- **Errors:** RFC 9457 `application/problem+json`:
  ```json
  { "type":"https://lifeiq.com/errors/validation",
    "title":"Validation failed","status":422,
    "detail":"confidence must be in [0,1]","instance":"/v1/briefings/123",
    "trace_id":"...", "errors":[{"field":"confidence","msg":"..."}] }
  ```
- **Rate limits:** per-user + per-tenant + per-endpoint; headers `RateLimit-Limit/Remaining/Reset`. `429` with `Retry-After`.
- **Standard codes:** 200/201/202(async accepted)/204; 400/401/403/404/409/422/429; 500/503.
- **Field naming:** `snake_case`; timestamps RFC3339 UTC; money objects `{amount, currency}`; confidence as `0..1` float.
- **Async pattern:** expensive generations return `202 + {job_id}`; poll `GET /jobs/{id}` or receive a websocket/SSE event.

## Surface map (by service)

### Identity & Access
```
POST   /auth/register                 POST /auth/login           POST /auth/refresh
POST   /auth/logout                   POST /auth/mfa/enroll      POST /auth/mfa/verify
POST   /auth/passkey/register/options POST /auth/passkey/register/verify
POST   /auth/passkey/login/options    POST /auth/passkey/login/verify
GET    /auth/sessions                 DELETE /auth/sessions/{id}
GET    /users/me                      PATCH /users/me            DELETE /users/me   (GDPR erase)
GET    /tenants                       POST /tenants              PATCH /tenants/{id}
GET    /tenants/{id}/members          POST /tenants/{id}/members PATCH /tenants/{id}/members/{uid}
```

### Briefing & Dashboard
```
GET    /dashboard                       -> latest briefing + streams + analytics summary
GET    /briefings?cursor=&limit=        GET /briefings/{id}
POST   /briefings:generate              -> 202 {job_id}  (force regenerate)
GET    /briefings/{id}/items            POST /briefing-items/{id}/feedback
```

### Council (mostly internal; read endpoints user-facing)
```
GET    /council/reports/{id}            -> exec summary, consensus, dissent, agent traces, evidence
POST   /council/analyze                 -> 202 {job_id} (Pro+: ad-hoc analysis of a subject)
```

### Opportunity Engine
```
GET    /opportunities?domain=&status=   GET /opportunities/{id}
POST   /opportunities/{id}:dismiss      POST /opportunities/{id}:act   (records WARU)
```

### Memory
```
GET    /memory                          POST /memory
PATCH  /memory/{id}                     DELETE /memory/{id}            (propagates to embeddings)
```

### Search
```
GET    /search?q=&types=people,reports,companies,communities,meetings,opportunities&cursor=
```

### Community & Network
```
GET    /reports?geo=&domain=            POST /reports
POST   /reports/{id}/confirm            POST /reports/{id}/dispute
GET    /communities                     POST /communities          GET /communities/{slug}
GET    /communities/{slug}/posts        POST /communities/{slug}/posts
POST   /posts/{id}/comments
GET    /moderation/queue (admin)        POST /moderation/{id}/appeal   POST /moderation/{id}/decide (admin)
GET    /reputation/{user_id}
GET    /follows                         POST /follows               DELETE /follows/{id}
```

### Corporate & Meetings
```
GET    /companies/{slug}                POST /companies            POST /companies/{id}:verify (admin)
GET    /companies/{id}/broadcasts       POST /companies/{id}/broadcasts  -> fan-out
POST   /meetings                        POST /meetings/{id}/recording  (upload/stream)
GET    /meetings/{id}                   GET /meetings/{id}/intelligence
GET    /meetings/search?q=              (semantic, tenant-scoped)
```

### Billing & Analytics
```
GET    /billing/subscription            POST /billing/checkout      POST /billing/portal
POST   /billing/webhook  (Stripe)       GET /analytics/me           GET /analytics/weekly-report
```

### Notifications, Admin, Privacy
```
GET    /notifications                   PATCH /notifications/prefs   POST /notifications/{id}:read
GET    /admin/...  (RBAC: admin)        GET /admin/audit?actor=&from=&to=
POST   /privacy/export   -> 202         POST /privacy/delete -> 202   GET /privacy/requests/{id}
```

## Webhooks (outbound, for enterprise integrations)
Signed (HMAC-SHA256, `X-LifeIQ-Signature`), retried with backoff, idempotent: `briefing.generated`, `opportunity.detected`, `council.completed`, `broadcast.published`, `meeting.analyzed`.

## Versioning & deprecation
- Additive changes are non-breaking and shipped continuously.
- Breaking changes: new path version, `Sunset` header on the old, ≥6-month overlap, changelog + migration guide.
- The OpenAPI file is the contract; clients are generated from it; contract tests run in CI on both sides.
