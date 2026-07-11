# UI And UX Rules

## Shared Stack

- Django Templates
- HTMX
- Alpine.js
- Tailwind CSS
- DaisyUI as primitive layer
- Business OS template components
- Lucide icons

## Admin Experience

- Operational screens must be calm, dense enough for repeated work, and not marketing-style.
- Sidebar navigation must be entitlement-aware.
- Tables must support responsive card mode on mobile.
- Forms must include clear labels, help text, error summary, field errors, save/cancel actions, and unsaved-change protection where needed.
- Every page must handle loaded, empty, filtered empty, permission denied, entitlement required, server failure, and success states.

## Public Website Experience

- Websites must not look like raw DaisyUI demos.
- Theme tokens must drive color, fonts, spacing, radius, and button treatment.
- The boutique/fashion template pack must support catalogue browsing first and commerce controls when commerce entitlements are active.
- Checkout must be fast for guests and account-capable for returning customers.

## Accessibility

Target WCAG 2.2 AA:

- Keyboard navigation.
- Visible focus.
- Semantic HTML.
- Accessible dialogs and drawers.
- Error summaries and field-level messages.
- Touch target compliance.
- RTL-ready templates.
- Automated Axe checks and manual keyboard passes before release.

