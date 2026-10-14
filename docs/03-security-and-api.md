# Security and API contracts

Basis: Hoffman chapters 21-25, 28-36; Madden's API threat/identity/authorization discussions; Google chapters 5, 6, 8, 9 and 13; OWASP REST and ASVS in sources.md.

## Threat model before controls

Map actors, assets, entry points, trust boundaries, admin capabilities and external dependencies. Include abuse cases: another user's ID, cross-tenant queries, forged price/role, replayed webhook, unlimited search/upload, password reset abuse and provider outage. Assess impact and exposure; select applicable ASVS requirements using a versioned identifier. OWASP Top 10 is awareness material, not a complete verification standard.

## Identity and authority

Use a maintained identity implementation. Distinguish authentication from authorization. Deny by default and authorize every resource/action, including nested resources, export, batch operations and background jobs. Tenant/owner scope must come from trusted identity, not a request-supplied field. An opaque identifier is not an authorization check.

For cookie sessions configure Secure, HttpOnly and appropriate SameSite; rotate identifiers on privilege changes and provide expiry/revocation. Decide CSRF protection from ambient credentials and request behavior; use validated tokens/origin controls as appropriate and never use GET for mutation. CORS controls browser response access; it is not authentication or a CSRF substitute.

If JWTs are used, validate signature with an algorithm allowlist, issuer, audience and expiry, and define revocation behavior. ID tokens and access tokens are not interchangeable. Use current provider/library guidance for OAuth/OIDC instead of copying historical sample flows. Avoid custom cryptography. Passwords require a maintained password-hashing implementation and current OWASP parameters, not a fast general hash.

## Inputs, outputs and resource controls

- Validate request shape, types, bounds, allowed fields, content type and payload size on the server. Reject forbidden role/price/tenant fields; calculate authoritative values yourself.
- Use parameterized queries, safe command APIs and contextual output encoding. Sanitize permitted rich HTML with a maintained allowlist; CSP is an additional layer, not a replacement.
- Uploads need size/type checks, content inspection as appropriate, randomized storage names, controlled access and storage outside executable public paths. Add malware/quarantine processing according to risk.
- If fetching user-supplied URLs, restrict schemes/destinations and redirects, block internal/metadata targets and control outbound network access. Validate again after DNS/redirect resolution; a URL regex alone is insufficient SSRF protection.
- Rate-limit expensive/abusable endpoints by suitable principals; limit query complexity, concurrency and time. Distributed deployment may need shared enforcement. Avoid penalizing all users behind one shared network without consideration.

## API behavior

Define schemas, ownership, status codes and error contracts. A possible envelope is `{code, message, requestId, fieldErrors}`; never leak stack traces or secrets. Return actual operation outcomes with appropriate HTTP semantics. Paginate and bound list endpoints; version incompatible contracts intentionally.

Set end-to-end deadlines and smaller dependency timeouts. Retry only retryable failures within a bounded budget using backoff and jitter. A timeout may mean the effect succeeded; reconcile rather than blindly creating again. Idempotency keys need scoped storage, payload fingerprint, atomic claim, replay response, expiry and concurrent-request behavior. Stripe's semantics are provider-specific, not universal defaults.

Webhooks require provider-specific signature validation over the correct raw payload, timestamp/replay handling and unique event processing. The UI redirect from checkout is not proof of payment. Keep audit events for important actions without passwords, tokens or excessive personal data.

## Supply chain and environment

Keep secrets in server-side configuration/secret management; verify public bundles, repository history and logs. Rotate an exposed credential, do not merely delete its line. Pin dependencies through the ecosystem's lockfile, review security advisories and package provenance, and document remediation ownership. Separate deployment identity from runtime identity and restrict both to necessary authority.

## Required negative evidence

Test unauthenticated access, user A accessing user B, tenant A accessing tenant B, ordinary user attempting admin behavior, tampered sensitive fields, invalid/oversized input, duplicate and concurrent mutation, expiry/revocation and dependency failure. Exercise direct API calls; hidden buttons do not prove enforcement. Automated scanning complements manual threat and business-logic review.
