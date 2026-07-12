# Actor, Portal, And Support Access Foundation

Date: 2026-07-12

## Scope

This note records the first production-grade foundation for master-spec sections 16, 25, 26, 35, 36, and 40.

Business OS remains a modular all-in-one Django monolith. This work is not ecommerce-specific.

## Decision

Platform authority is modeled separately from organization tenant membership.

- `is_platform_staff` remains an eligibility flag on the user account.
- `PlatformRole` and `PlatformRoleAssignment` grant explicit platform permissions.
- Organization admin access is membership-only and no longer treats platform staff as implicit tenant members.
- Support access uses `SupportSession`, not impersonation and not tenant membership.
- Support mode is read-only in this foundation. Controlled-write support access stays blocked until MFA, approval, and policy controls are implemented.

## Implementation

Changed code:

- `business_os/apps/core/models.py`
- `business_os/apps/core/services.py`
- `business_os/apps/core/middleware.py`
- `business_os/apps/core/admin.py`
- `business_os/portals/views.py`
- `business_os/portals/platform_urls.py`
- `business_os/config/urls.py`
- `business_os/templates/platform_portal/organizations.html`
- `business_os/templates/platform_portal/organization_workspace.html`

Migration:

- `business_os/apps/core/migrations/0002_platformrole_supportsession_and_more.py`

The migration creates platform role/support-session tables, links audit events to support sessions, and backfills existing `is_platform_staff=True` users into the system `platform-administrator` role.

## Routes

Canonical platform-host routes:

- `GET /organizations/`
- `GET /organizations/<organization_slug>/`
- `POST /organizations/<organization_slug>/support/start/`
- `POST /organizations/<organization_slug>/support/end/`

Legacy `/platform/...` routes remain available for local/developer compatibility.

## Forms And Inputs

No broad platform UI build was added.

The support start endpoint accepts:

- `reason`
- `ticket_reference`
- `duration_minutes`

The implementation always creates read-only support sessions.

## Entitlements

No tenant entitlement changes were made. Platform role assignments are independent from organization subscriptions and tenant roles.

## Verification

Recorded in `08-verification-log.md`.

Relevant test coverage:

- Business member can access only their own organization admin.
- Platform staff with explicit role can access platform portal.
- Non-platform users cannot access platform portal.
- Support session grants scoped organization workspace access.
- Expired support session fails.
- Support access writes audit events.
- Support access does not grant business-admin tenant access or create tenant membership.

## Remaining Gaps

- Customer portal session isolation and host-scoped cookie policy.
- Full customer actor model.
- Facility-aware role dimensions.
- Platform role management UI.
- MFA/approval workflow for sensitive support access.
- Controlled-write support policy.
- Customer-facing support visibility rules beyond the current platform banner.
- Immutable audit retention, export/delete privacy workflows, and legal hold rules.
