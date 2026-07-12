# Business And Platform Login Session Completion

Date: 2026-07-12

## Scope

This note records the completed Business Admin and Platform Admin login/session slice for master-spec sections 16, 25, 26, 35, and 40.

This is complete for the declared scope: privileged Business Admin and Platform Admin browser login. Customer account login and MFA are separate future product features because they require separate customer actor and sensitive-action policy work.

## Decision

Business OS uses one Django authentication system, but authenticated browser sessions must be scoped to the portal where the login happened.

- Business Admin sessions use the `business_admin` portal scope.
- Platform sessions use the `platform_admin` portal scope.
- Future customer account sessions have a reserved `customer` portal scope.
- A valid Django auth session is not enough to cross from one portal into another.
- If a privileged session appears on a public website host, the server clears it and treats the request as anonymous.
- Customer login remains unavailable until the customer actor model exists.
- Login failures are rate-limited.
- Login, logout, denied access, failed credentials, rate limits, and rejected cross-portal sessions are audited.
- Password reset is available on privileged app/platform hosts and blocked on public website hosts.

## Implementation

Changed code:

- `business_os/apps/accounts/services.py`
- `business_os/apps/accounts/views.py`
- `business_os/apps/core/middleware.py`
- `business_os/apps/websites/domain_services.py`
- `business_os/config/settings/base.py`
- `business_os/config/urls.py`
- `business_os/templates/accounts/portal_login.html`
- `business_os/templates/admin_portal/base.html`
- `business_os/templates/platform_portal/base.html`
- `business_os/templates/registration/password_reset_form.html`
- `business_os/templates/registration/password_reset_done.html`
- `business_os/templates/registration/password_reset_email.html`
- `business_os/templates/registration/password_reset_subject.txt`
- `business_os/templates/registration/password_reset_confirm.html`
- `business_os/templates/registration/password_reset_complete.html`
- `docker-compose.yml`

Tests:

- `tests/integration/test_portal_session_isolation.py`
- Existing domain/support tests were updated to mark forced logins with an explicit portal scope.

## Routes

Canonical routes:

- `GET /login/`
- `POST /login/`
- `POST /logout/`
- `GET /password-reset/`
- `POST /password-reset/`
- `GET /password-reset/done/`
- `GET /password-reset/<uidb64>/<token>/`
- `POST /password-reset/<uidb64>/<token>/`
- `GET /password-reset/complete/`

Legacy local/developer compatibility routes:

- `GET /app/login/`
- `POST /app/login/`
- `POST /app/logout/`
- `GET /platform/login/`
- `POST /platform/login/`
- `POST /platform/logout/`

## Cookie And CSRF Policy

- `SESSION_COOKIE_DOMAIN` defaults to `None`, so browser cookies are host-only by default.
- `CSRF_COOKIE_DOMAIN` defaults to `None`, so CSRF cookies are host-only by default.
- Default CSRF trusted origins are explicit canonical app, platform, and API hosts.
- Docker Compose now includes explicit canonical local CSRF origins for `businessos.local` and `localhost` subdomains.
- Logout is POST-only.
- Password reset routes are not exposed on generated/custom public website hosts.
- Login `next` redirects are constrained to safe, portal-appropriate local paths.
- Login failures are rate-limited by portal, username, and IP address for the configured window.

## Verification

Recorded in `08-verification-log.md`.

Relevant tests:

- Business login marks a `business_admin` session and redirects to the organization dashboard.
- Platform login marks a `platform_admin` session and rejects external `next` redirects.
- Business sessions cannot be reused on the platform host.
- Platform sessions cannot be reused on the business admin host.
- Leaked privileged sessions are cleared on public website hosts.
- Cookie domains remain host-scoped and CSRF trusted origins are explicit.
- Failed login is audited and rate-limited.
- Logout is POST-only, audited, and clears the portal session.
- Password reset sends email without revealing account existence.
- Password reset is blocked on public website hosts.

## Separate Future Features

- Customer actor model and customer account login.
- MFA for sensitive platform/support access.
- Approval workflow for controlled-write support access.
- Rate limiting for support and API endpoints.
- Security headers/CSP hardening.
- Private file access and virus-scan hook.
- Secrets management through Key Vault or equivalent.
- Full privacy workflows for export, deletion, anonymization, retention, and legal hold.
