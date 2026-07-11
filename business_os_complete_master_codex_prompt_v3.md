# BUSINESS OS — MASTER CODEX IMPLEMENTATION PROMPT

## 0. ROLE AND EXPECTATION

You are Codex acting as a senior product architect, Django engineer, database architect, SaaS engineer, UI/UX engineer, security engineer, and technical writer.

Build a production-grade, modular, multi-tenant SaaS platform called **Business OS**.

Business OS allows a business to:

- Create a free public website.
- Manage its business from one admin portal.
- Purchase only the modules and capabilities it needs.
- Activate discounted bundles.
- Automatically change both the admin portal and public website based on active entitlements.
- Add e-commerce, appointments, reservations, inventory, POS, CRM, staff, payments, communication, marketing, projects, assets, automation, analytics, AI, and industry extensions without rebuilding the website.
- Use one codebase, one deployment, and one entitlement engine.
- Pay through one consolidated subscription and invoice even when multiple modules or add-ons are active.

Do not create separate applications per customer. Do not physically install or uninstall Django apps per tenant. All modules stay deployed, and entitlements determine what each organization can access.

Build the platform as a **modular Django monolith** first. Keep module boundaries strong enough for future service extraction, but do not introduce microservices, Kubernetes, Kafka, GraphQL, or separate frontend applications during the MVP unless explicitly required.

---

# 1. PRODUCT PRINCIPLES

## 1.1 Core product promise

> Start with a free business website. Add only the business capabilities you need. Your admin portal and website update automatically.

## 1.2 Commercial model

The commercial model is:

```text
Free Business OS Core
+ Optional paid modules
+ Optional feature add-ons
+ Optional connectors
+ Discounted bundles
+ Usage-based external services
```

There are no rigid Starter, Business, and Pro tiers.

Each organization has one subscription with multiple items.

Example:

```text
Organization Subscription
├── Website Pro
├── Catalogue Advanced
├── Appointment Booking
├── WhatsApp Business Connector
└── Automation Lite

Discount:
Salon Bundle

One invoice
One renewal date
One payment
```

## 1.3 Entitlement levels

Entitlements must support three levels:

1. **Module entitlement**
2. **Feature or capability entitlement**
3. **Usage limit or quota**

Examples:

```text
website.enabled
website.custom_domain
catalogue.variants
commerce.cart
commerce.checkout
appointments.waitlist
communication.whatsapp
automation.reminders
analytics.advanced
```

Usage examples:

```text
website.custom_domains.max = 1
catalogue.products.max = 100
staff.users.max = 5
storage.gb = 5
messages.whatsapp.monthly = 1000
```

## 1.4 Ethical UX principles

The system must feel:

- Clean
- Calm
- Trustworthy
- Professional
- Simple by default
- Powerful when needed
- Mobile-friendly
- Transparent
- Accessible
- Fast

Do not use dark patterns.

Do not use:

- Fake urgency
- Hidden charges
- Hard-to-find cancellation
- Misleading discounts
- Manipulative countdowns
- Artificial scarcity
- Confusing pricing
- Preselected paid add-ons without explicit consent

Use progressive disclosure.

Always show:

- What is active
- What is included
- What will change after activation
- Exact monthly or annual price
- Usage charges
- Renewal date
- Cancellation effect
- Data retention behavior

---

# 2. RECOMMENDED TECH STACK

## 2.1 Backend

- Python 3.13
- Django 5.2 LTS
- PostgreSQL 17
- Django ORM
- Django migrations
- Django admin for internal superadmin support only
- Django Ninja for mobile and external APIs
- Celery for background jobs
- Redis for caching, task broker, rate limits, temporary locks, and short-lived availability holds
- Wagtail for content-oriented website editing, publishing, revisions, previews, and media where useful
- django-allauth for authentication flows
- django-storages for Azure Blob or S3-compatible storage
- pytest and pytest-django
- Ruff
- mypy where practical
- OpenTelemetry
- Sentry
- Azure Application Insights

## 2.2 Frontend

For Business Admin and Superadmin:

- Django Templates
- HTMX
- Alpine.js
- Tailwind CSS
- DaisyUI as the primary component primitive layer
- Business OS Component Library
- TailAdmin Free HTML only as an initial visual reference, not as a dependency for generated customer websites
- Lucide icons
- Accessible reusable template components
- FullCalendar free edition for normal calendars
- Custom resource and schedule views where required

For generated public websites:

- Django Templates
- Wagtail or structured page models
- Tailwind CSS
- Minimal Alpine.js
- HTMX only where dynamic server interactions are useful
- Responsive images
- Server-side rendering
- Minimal JavaScript
- Template packs
- Structured website sections
- Theme tokens
- Approved font catalogue
- Lucide icons plus official brand SVGs

## 2.3 Fonts

Admin UI:

- Inter or Geist
- Noto Sans Arabic
- Noto Sans Devanagari
- Noto Sans Malayalam

Generated websites:

- Curated, self-hosted open-source fonts only
- Heading and body fonts configurable by theme
- LTR and RTL support

## 2.4 Hosting

Initial Azure setup:

- Azure Front Door
- Azure Container Apps
- Azure Database for PostgreSQL Flexible Server
- Azure Managed Redis
- Azure Blob Storage
- Azure Key Vault
- GitHub Actions or Azure DevOps
- Docker
- Terraform later

---

# 3. HIGH-LEVEL ARCHITECTURE

```text
                         BUSINESS OS
                              │
                 ┌────────────┴────────────┐
                 │                         │
          Business Admin            Public Website
                 │                         │
                 └────────────┬────────────┘
                              │
                       Django Platform
                              │
              ┌───────────────┼────────────────┐
              │               │                │
       Entitlement Engine   Module Registry   Website Composer
              │               │                │
              └───────────────┼────────────────┘
                              │
                  Shared Domain Services
                              │
       PostgreSQL + Redis + Celery + Blob Storage
```

Every business-facing request must resolve:

```text
request.user
request.organization
request.facility
request.permissions
request.entitlements
request.locale
request.currency
request.timezone
```

---

# 4. FINAL GENERALIZED MODULE ARCHITECTURE

There are 17 generalized architectural modules.

## 4.1 Business Core

Includes:

- Organizations
- Branches
- Facilities
- Business profiles
- Users
- Authentication
- Roles
- Permissions
- Localization
- Currencies
- Tax regions
- Media library
- Custom fields
- Custom objects
- Imports
- Exports
- Audit logs
- Marketplace
- Subscription and entitlement engine
- Feature flags
- Usage limits
- Billing account
- Platform settings
- Retention rules
- Notification preferences
- Tenant-aware storage
- Tenant-aware background jobs

## 4.2 Website & Content

Includes:

- Free basic website
- Website Pro
- Template packs
- Theme packs
- Pages
- Sections
- Navigation
- Header and footer builder
- Hero sections
- Gallery
- Blog
- News
- Testimonials
- FAQ
- Forms
- Landing pages
- SEO
- Sitemap
- robots.txt
- Canonical links
- Open Graph
- Schema.org structured data
- Custom domains
- SSL status
- Domain verification
- Preview tokens
- Drafts
- Publish
- Rollback
- Scheduled publishing
- Multilingual content
- RTL rendering
- Version history
- Media library
- Website analytics
- Cookie and consent banner
- Privacy and terms pages

## 4.3 Catalogue & Offerings

Supports:

- Products
- Services
- Rooms
- Courses
- Memberships
- Rentals
- Menu items
- Tickets
- Packages
- Listings
- Add-ons
- Bundles
- Categories
- Collections
- Tags
- Attributes
- Variants
- Options
- Price
- Sale price
- Images
- Documents
- Availability metadata
- SEO
- Visibility
- Status
- Related offerings
- Cross-sells
- Upsells
- Custom fields

## 4.4 Commerce, Orders & POS

Includes:

- Cart
- Guest cart
- Customer cart
- Checkout
- Orders
- Order items
- Quotations
- Estimates
- Online sales
- Manual sales
- POS
- Sales channels
- Discounts
- Coupons
- Gift cards
- Wishlist
- Returns
- Refund requests
- Exchanges
- Receipts
- Order history
- Order status
- Order notes
- Fulfilment status
- Payment status
- Taxes
- Pricing rules
- In-store and online synchronization

## 4.5 Scheduling, Appointments & Reservations

Generalized for:

- Appointments
- Staff bookings
- Courts
- Tables
- Vehicles
- Equipment
- Rooms
- Tee times
- Hotel stays
- Restaurant reservations
- Classes
- Tours
- Group bookings

Includes:

- Calendars
- Availability
- Schedules
- Shifts
- Time slots
- Date ranges
- Capacity
- Buffers
- Blackout dates
- Maintenance blocks
- Temporary holds
- Waitlists
- Booking windows
- Advance notice
- Conflict detection
- Recurrence
- Rescheduling
- Cancellation
- Check-in
- Check-out
- No-show
- Deposits
- Multi-resource booking
- Group capacity
- Overbooking policy
- Manual override with audit

## 4.6 Inventory, Procurement & Warehouse

Includes:

- Stock levels
- SKUs
- Variant stock
- Safety stock
- Reserved stock
- Available stock
- Warehouses
- Stock locations
- Bins
- Transfers
- Adjustments
- Receiving
- Picking
- Packing
- Dispatch
- Stock counts
- Suppliers
- Purchase orders
- Goods received
- Purchase returns
- Reorder points
- Batches
- Lots
- Serial numbers
- Expiry
- Cost
- Stock movement ledger
- Stock reservation
- Stock release
- Inventory reports

## 4.7 Customers, CRM & Relationships

Generalized party model:

```text
Party
├── Person
└── Organization
```

Party roles:

- Customer
- Lead
- Guest
- Member
- Patient
- Student
- Tenant
- Supplier
- Agent
- Guardian
- Donor
- Vendor
- Partner

Includes:

- Profiles
- Contacts
- Addresses
- Tags
- Groups
- Segments
- Notes
- Timeline
- Lead pipeline
- Status
- Preferences
- Consent
- Communication history
- Orders
- Appointments
- Payments
- Documents
- Relationships
- Portal access
- Custom fields

## 4.8 Workforce, Partners & Access

Includes:

- Employees
- Staff
- Contractors
- Agents
- Vendors
- Drivers
- Teachers
- Doctors
- Technicians
- Volunteers
- Profiles
- Roles
- Permissions
- Skills
- Certifications
- Documents
- Availability
- Shifts
- Leave
- Attendance
- Assignments
- Commissions
- Performance
- Work locations
- Access control
- Staff portal

## 4.9 Payments, Billing & Finance

Includes:

- Payment providers
- Payment intents
- Transactions
- Cash
- Card
- Bank transfer
- Payment links
- Deposits
- Partial payments
- Refunds
- Settlements
- Payouts
- Invoices
- Receipts
- Credit notes
- Expenses
- Taxes
- VAT
- GST
- Customer balances
- Supplier payments
- Recurring billing
- Subscription billing
- Invoice numbering
- Financial reports
- Payment webhooks
- Idempotency
- Reconciliation

## 4.10 Communication & Notifications

Channels:

- In-app
- Basic system email
- Gmail
- Microsoft 365
- WhatsApp Business API
- SMS
- Push
- Custom SMTP
- SendGrid
- Resend
- Azure Communication Services

Includes:

- Connectors
- OAuth
- Message templates
- Transactional notifications
- Scheduled reminders
- Delivery logs
- Failed delivery
- Retry
- Unified inbox
- Customer replies
- Communication history
- Sender identity
- Consent
- Opt-in
- Opt-out

Important rule:

- A simple direct WhatsApp link is a Website or Catalogue feature.
- WhatsApp Business API is a paid communication connector.

## 4.11 Marketing, Loyalty & Reputation

Includes:

- Campaigns
- Segments
- Promotions
- Coupons
- Abandoned cart
- Re-engagement
- Loyalty points
- Rewards
- Referrals
- Membership benefits
- Reviews
- Testimonials
- Review requests
- Reputation dashboard
- Campaign analytics
- Marketing consent

## 4.12 Work, Projects & Service Operations

Includes:

- Projects
- Tasks
- Milestones
- Dependencies
- Boards
- Timelines
- Work orders
- Field jobs
- Support tickets
- Cases
- Maintenance requests
- Assignments
- Statuses
- Priorities
- SLA
- Checklists
- Time tracking
- Materials used
- Expenses
- Photos
- Attachments
- Comments
- Customer approval
- Completion proof
- Internal notes
- Service history

## 4.13 Assets, Facilities & Fleet

Supports:

- Properties
- Buildings
- Floors
- Units
- Rooms
- Equipment
- Machines
- Vehicles
- Courts
- Tables
- Desks
- Rental assets

Includes:

- Asset hierarchy
- Location
- Owner
- Status
- Availability
- Serial number
- Warranty
- Documents
- Meter readings
- Maintenance
- Inspections
- Downtime
- Utilization
- QR codes
- Check-in
- Check-out
- History

## 4.14 Documents, Forms & Compliance

Includes:

- Form builder
- Multi-step forms
- Conditional forms
- Public forms
- Internal forms
- File uploads
- Signatures
- Calculated fields
- Document templates
- PDF generation
- Contracts
- Agreements
- E-signatures
- Digital acceptance
- Checklists
- Inspections
- Licences
- Permits
- Risk register
- Incidents
- Safety
- Quality checks
- Corrective actions
- Approvals
- Evidence
- Expiry reminders
- Audit history
- Consent records

## 4.15 Automation, Rules & Integrations

Includes:

- Triggers
- Conditions
- Actions
- Delays
- Schedules
- Approvals
- Escalations
- Retries
- Workflow logs
- Pricing rules
- Eligibility rules
- Cancellation rules
- Availability rules
- Tax rules
- Webhooks
- API keys
- OAuth
- External integrations
- Google
- Microsoft
- Accounting
- Courier
- Payment providers
- Calendar sync
- Data synchronization

## 4.16 Analytics, Reporting & AI

Includes:

- Dashboards
- Widgets
- KPIs
- Reports
- Scheduled reports
- Exports
- Revenue analytics
- Website analytics
- Product analytics
- Booking analytics
- Inventory analytics
- Staff analytics
- Customer analytics
- Operational analytics
- AI summaries
- Natural-language reporting
- Forecasting
- Recommendations
- Content generation
- Product descriptions
- Anomaly detection
- AI usage tracking
- AI provider abstraction

## 4.17 Industry Extensions

Examples:

- Restaurant kitchen display
- Hotel housekeeping and night audit
- Healthcare clinical records
- Manufacturing BOM and production orders
- Education academic years and grades
- Construction BOQ and progress claims
- Agriculture crop and livestock records
- Pharmacy controlled stock
- Laboratory samples and results

Industry packs combine generalized modules with minimal specialized extensions.

---

# 5. MODULE REGISTRY

Every Django app must register metadata in a central module registry.

Required metadata:

```python
MODULE_CONFIG = {
    "code": "catalogue",
    "name": "Catalogue & Offerings",
    "description": "...",
    "category": "sell",
    "icon": "package",
    "dependencies": [],
    "recommended_with": ["website", "commerce"],
    "capabilities": [],
    "navigation": [],
    "website_contributions": [],
    "dashboard_widgets": [],
    "events": [],
    "usage_metrics": [],
}
```

The registry must support:

- Module code
- Display name
- Category
- Marketplace description
- Benefits
- Screenshots
- Pricing options
- Trial
- Dependencies
- Recommended modules
- Capabilities
- Limits
- Admin navigation
- Website contributions
- Customer portal contributions
- Background jobs
- Events
- Analytics
- Release status
- Visibility
- Supported countries
- Supported industries
- Beta organizations

Lifecycle:

```text
Draft
Internal
Private Beta
Public
Deprecated
Retired
```

---

# 6. SUBSCRIPTION, MARKETPLACE, AND ENTITLEMENT ENGINE

## 6.1 Marketplace for business users

Business Admin must include:

```text
Marketplace
├── Recommended Bundles
├── All Modules
├── My Modules
├── Connectors
├── Usage
├── Billing
└── Invoices
```

Each module card must show:

- Name
- Icon
- Short description
- Monthly price
- Annual price
- Trial
- Usage charges
- Dependencies
- Admin additions
- Website additions
- Customer portal additions
- Limits
- Add-ons
- Screenshots
- Recommended industries
- Setup time
- Activate
- Trial
- Compare
- Customize

## 6.2 Module customization

Users must be able to select only needed capabilities.

Example:

```text
Communication & Notifications

Included:
✓ In-app notifications
✓ Basic system email

Optional:
☐ WhatsApp Business
☐ Gmail Connect
☐ Microsoft 365
☐ SMS
☐ Push
☐ Unified Inbox
☐ Automated Reminders
```

Price updates dynamically.

## 6.3 Bundles

Bundles are discounted combinations.

Example:

```text
Salon Essentials
Website Pro
Appointments
Staff
CRM
WhatsApp Business

Normal price: AED 90
Bundle price: AED 69
```

Bundle purchase must activate the same capabilities as individual purchases.

No feature difference between individual module and bundle purchase.

## 6.4 Superadmin subscription configuration

Superadmin needs:

```text
Platform Admin
├── Organizations
├── Modules
├── Features
├── Capabilities
├── Prices
├── Packages
├── Bundles
├── Dependencies
├── Limits
├── Trials
├── Coupons
├── Promotions
├── Subscriptions
├── Subscription Items
├── Invoices
├── Payments
├── Refunds
├── Usage
├── Revenue Reports
└── Audit Logs
```

## 6.5 Pricing types

Support:

- Fixed recurring
- Annual recurring
- One-time
- Per user
- Per location
- Per transaction
- Usage-based
- Tiered usage
- Setup fee
- Included allowance
- Overage fee
- Manual enterprise price

## 6.6 Subscription statuses

- Draft
- Trialing
- Active
- Past due
- Suspended
- Cancel at period end
- Cancelled
- Expired

## 6.7 Activation flow

```text
Payment confirmed
→ Subscription item active
→ Entitlements generated
→ Limits initialized
→ Admin navigation refreshed
→ Website capabilities unlocked
→ Default pages/sections provisioned
→ Background setup jobs triggered
→ Customer notified
```

## 6.8 Cancellation flow

```text
Cancel at period end
→ Feature remains active until renewal date
→ At end date module becomes read-only
→ New transactions blocked
→ Public feature hidden
→ Existing data retained
→ Export available
→ Reactivation restores access
→ Permanent deletion only after retention period
```

---

# 7. BUSINESS ADMIN UI/UX

## 7.1 Global layout

Desktop:

```text
Top Bar
├── Business switcher
├── Branch selector
├── Global search
├── Help
├── Notifications
└── User menu

Left Sidebar
├── Dashboard
├── Active module navigation
├── Marketplace
└── Settings
```

Mobile:

- Bottom navigation for key actions
- Collapsible menu
- Sticky primary actions
- Cards instead of wide tables
- Large touch targets
- Camera upload support

## 7.2 Dynamic navigation

Navigation must be generated from active entitlements.

Do not hard-code scattered `{% if module %}` checks.

Use:

```python
navigation = module_registry.get_navigation(
    organization=request.organization,
    user=request.user,
)
```

## 7.3 Dashboard

Dashboard must answer:

1. What happened?
2. What needs attention?
3. What should I do next?

Sections:

- Greeting
- Today summary
- Needs attention
- Quick actions
- Active module widgets
- Recent activity
- Setup progress
- Business performance
- Marketplace recommendations

Example:

```text
Good morning, Mithun

Today
12 appointments
8 new orders
AED 4,280 revenue

Needs attention
• 2 pending confirmations
• 3 low-stock items
• 1 failed payment
```

## 7.4 Empty states

Every empty state must include:

- What the feature does
- Why it matters
- Primary action
- Example or guide

## 7.5 Form patterns

Every form must support:

- Clear labels
- Help text
- Required markers
- Field-level errors
- Form-level summary
- Save
- Save and continue
- Cancel
- Autosave only where safe
- Unsaved changes warning
- Draft support where applicable
- Keyboard access
- Mobile responsiveness

## 7.6 Tables

Tables must support where relevant:

- Search
- Filters
- Saved views
- Sort
- Pagination
- Bulk actions
- Column visibility
- Export
- Row actions
- Mobile card mode
- Empty state
- Loading state
- Error state

## 7.7 Status system

Consistent statuses across modules:

- Draft
- Active
- Pending
- Confirmed
- Completed
- Cancelled
- Failed
- Refunded
- Suspended
- Expired
- Blocked
- Archived

Use consistent badge styles throughout the platform.

---

# 8. PUBLIC WEBSITE ENGINE

## 8.1 Website composition

```text
Business Data
→ Website Configuration
→ Active Entitlements
→ Selected Template Pack
→ Theme Tokens
→ Page Sections
→ Rendered Website
```

## 8.2 Website behavior by modules

Free website:

- Home
- About
- Gallery
- Contact
- Opening hours
- Location
- Social links
- Direct WhatsApp link
- Basic SEO
- Business OS subdomain
- Powered by Business OS branding

Catalogue entitlement adds:

- Shop or Catalogue
- Categories
- Collections
- Offering detail
- Search
- Filters
- Product inquiry

Commerce entitlement adds:

- Cart
- Checkout
- Account
- Order history
- Payments
- Order tracking

Appointments entitlement adds:

- Services
- Staff
- Calendar
- Slot selection
- Booking confirmation

Reservations entitlement adds:

- Availability search
- Date range
- Guest count
- Capacity
- Reservation confirmation

## 8.3 Structured sections

Supported section families:

- Hero
- About
- Features
- Services
- Products
- Collections
- Categories
- Staff
- Booking CTA
- Reservation form
- Product grid
- Gallery
- Testimonials
- Reviews
- Pricing
- FAQ
- Contact
- Location
- Opening hours
- Newsletter
- Offers
- Blog posts
- Social proof
- Footer

Each section supports controlled variants.

Example:

```json
{
  "type": "product_grid",
  "variant": "cards_with_badges",
  "title": "New Arrivals",
  "columns": 4,
  "show_price": true,
  "show_whatsapp": true
}
```

## 8.4 Website editor

Tabs:

```text
Pages
Sections
Theme
Navigation
SEO
Domains
Languages
Publishing
Analytics
```

Users can:

- Add section
- Remove section
- Reorder section
- Change layout variant
- Edit content
- Select colours
- Select fonts
- Adjust spacing
- Preview desktop
- Preview tablet
- Preview mobile
- Save draft
- Publish
- Roll back

Avoid unrestricted HTML editing in MVP.

## 8.5 Theme tokens

- Primary color
- Secondary color
- Accent color
- Background
- Surface
- Text
- Muted text
- Heading font
- Body font
- Container width
- Section spacing
- Radius
- Button style
- Card style
- Input style
- Header style
- Footer style

## 8.6 Domains

Support:

- Default subdomain
- Custom domain
- DNS verification
- Domain status
- SSL status
- Redirects
- Canonical domain
- www/non-www
- Failure diagnostics

## 8.7 Website publishing

Models:

- Website
- WebsiteVersion
- Page
- PageVersion
- Section
- Theme
- Domain
- PublishLog
- PreviewToken

Flow:

```text
Draft
→ Preview
→ Publish
→ Published version
→ New draft
→ Republish
→ Rollback
```

---

# 9. SUPERADMIN UI

Superadmin must configure the entire platform.

Main sections:

```text
Overview
Organizations
Users
Modules
Capabilities
Pricing
Bundles
Marketplace
Subscriptions
Invoices
Payments
Usage
Coupons
Trials
Feature Flags
Website Templates
Theme Packs
Industry Packs
Integrations
Background Jobs
System Health
Audit Logs
Support Tools
Platform Settings
```

Superadmin controls:

- Module metadata
- Capability grants
- Pricing
- Limits
- Dependencies
- Visibility
- Trials
- Countries
- Industries
- Beta access
- Templates
- Website section availability
- Admin navigation registration
- Manual entitlements
- Enterprise overrides
- Suspension
- Refunds
- Trial extension
- Retention override
- Feature rollouts
- Usage corrections
- Support impersonation with audit

---

# 10. DATABASE DESIGN

Use UUID primary keys where reasonable.

Every tenant-owned model must include:

- organization_id
- facility_id where applicable
- created_at
- updated_at
- created_by
- updated_by
- status
- soft-delete or archival behavior where needed

## 10.1 Core tables

- organizations
- organization_profiles
- facilities
- facility_hours
- users
- memberships
- roles
- permissions
- role_permissions
- user_roles
- media_assets
- custom_field_definitions
- custom_field_values
- audit_events
- imports
- exports
- localization_settings
- currency_settings
- tax_settings

## 10.2 Marketplace and subscription tables

- modules
- capabilities
- module_capabilities
- module_dependencies
- module_prices
- module_limits
- module_navigation_items
- module_website_contributions
- bundles
- bundle_modules
- bundle_prices
- organization_subscriptions
- subscription_items
- organization_entitlements
- organization_limit_overrides
- usage_records
- trials
- coupons
- promotions
- invoices
- invoice_items
- payments
- refunds

## 10.3 Website tables

- websites
- website_versions
- pages
- page_versions
- sections
- section_versions
- themes
- theme_tokens
- template_packs
- domains
- publish_logs
- preview_tokens
- redirects
- seo_metadata

## 10.4 Catalogue tables

- offerings
- offering_types
- offering_categories
- categories
- collections
- collection_items
- option_definitions
- option_values
- offering_variants
- variant_option_values
- offering_images
- offering_documents
- offering_prices
- offering_relations
- offering_addons

## 10.5 Commerce tables

- carts
- cart_items
- orders
- order_items
- order_status_history
- quotations
- quotation_items
- discounts
- coupons
- gift_cards
- wishlists
- wishlist_items
- returns
- return_items
- exchanges
- sales_channels
- pos_sessions
- pos_transactions

## 10.6 Booking tables

- resources
- resource_groups
- resource_schedules
- availability_rules
- availability_blocks
- booking_holds
- bookings
- booking_resources
- booking_participants
- booking_status_history
- waitlist_entries
- capacity_allocations
- cancellation_policies
- booking_rules

## 10.7 Inventory tables

- inventory_items
- inventory_levels
- stock_locations
- warehouses
- bins
- inventory_reservations
- stock_movements
- stock_adjustments
- stock_transfers
- suppliers
- purchase_orders
- purchase_order_items
- goods_receipts
- goods_receipt_items
- batches
- serial_numbers

## 10.8 CRM tables

- parties
- party_people
- party_organizations
- party_roles
- contacts
- addresses
- party_tags
- party_notes
- party_relationships
- leads
- lead_stages
- lead_activities
- consents
- communication_preferences
- customer_portal_accounts

## 10.9 Workforce tables

- workers
- worker_skills
- worker_certifications
- worker_documents
- worker_schedules
- shifts
- leave_requests
- attendance_records
- assignments
- commissions
- access_rules

## 10.10 Payments and finance tables

- payment_providers
- payment_intents
- payment_transactions
- payment_webhook_events
- invoices
- invoice_lines
- receipts
- credit_notes
- expenses
- refunds
- payouts
- settlements
- tax_rates
- tax_rules

## 10.11 Communication tables

- communication_channels
- provider_connections
- message_templates
- messages
- message_recipients
- delivery_attempts
- conversation_threads
- conversation_messages
- notification_preferences
- sender_identities

## 10.12 Marketing tables

- campaigns
- campaign_segments
- campaign_messages
- loyalty_accounts
- loyalty_transactions
- rewards
- referrals
- reviews
- review_requests
- reputation_sources

## 10.13 Work and operations tables

- projects
- project_members
- milestones
- work_items
- work_item_dependencies
- work_item_assignments
- work_logs
- checklists
- checklist_items
- support_tickets
- service_jobs
- work_orders
- approvals
- customer_signoffs

## 10.14 Assets tables

- assets
- asset_types
- asset_locations
- asset_documents
- asset_warranties
- meter_readings
- maintenance_plans
- maintenance_events
- asset_inspections
- asset_downtime
- asset_usage

## 10.15 Documents and compliance tables

- forms
- form_versions
- form_fields
- form_submissions
- documents
- document_templates
- document_versions
- agreements
- signatures
- inspections
- inspection_templates
- compliance_requirements
- licences
- permits
- risks
- incidents
- corrective_actions
- evidence_files

## 10.16 Automation tables

- automation_workflows
- automation_versions
- triggers
- conditions
- actions
- workflow_runs
- workflow_steps
- workflow_logs
- integration_connections
- webhooks
- webhook_deliveries
- api_keys
- sync_jobs

## 10.17 Analytics tables

- analytics_events
- daily_metrics
- monthly_metrics
- dashboard_definitions
- dashboard_widgets
- report_definitions
- report_runs
- ai_requests
- ai_usage
- ai_feedback

---

# 11. FORMS AND CONTROLS

## 11.1 Organization onboarding form

Fields:

- Business name
- Legal name
- Business type
- Industry
- Country
- Currency
- Timezone
- Default language
- Additional languages
- Address
- Phone
- Email
- Website
- WhatsApp number
- Logo
- Short description
- Opening hours
- Tax registration
- Business registration number
- Preferred modules
- Theme preference
- Domain preference

Controls:

- Stepper
- Back
- Continue
- Save draft
- Preview
- Skip optional
- Progress percentage
- Validation
- Country-aware defaults

## 11.2 Facility form

- Facility name
- Code
- Address
- Contact
- Timezone
- Currency override
- Operating hours
- Holiday calendar
- Status
- Available modules
- Default warehouse
- Default payment provider
- Public visibility

## 11.3 User and role forms

User:

- Name
- Email
- Phone
- Role
- Organization
- Facility
- Status
- Language
- Timezone
- MFA status
- Invite
- Resend invite
- Suspend
- Reset access

Role:

- Name
- Scope
- Capabilities
- Facilities
- Data visibility
- Create
- View
- Edit
- Delete
- Approve
- Export
- Billing access
- Marketplace access

## 11.4 Website page form

- Page title
- Slug
- Page type
- Status
- Navigation visibility
- Parent page
- Sections
- SEO title
- Meta description
- Canonical URL
- Open Graph image
- Structured data type
- Language
- Publish schedule

## 11.5 Theme form

- Primary color
- Secondary color
- Accent color
- Background
- Text color
- Heading font
- Body font
- Button radius
- Card radius
- Section spacing
- Container width
- Header style
- Footer style
- Dark mode
- RTL preview

## 11.6 Product or offering form

Basic:

- Name
- Slug
- Type
- Description
- Short description
- Price
- Sale price
- Currency
- Category
- Collection
- Images
- Visibility
- Status

Advanced:

- Options
- Variants
- SKU
- Barcode
- Tax class
- Weight
- Dimensions
- Availability
- Inventory tracking
- Booking duration
- Capacity
- Related offerings
- Add-ons
- SEO
- Custom fields

## 11.7 Booking configuration form

- Booking mode
- Duration
- Time interval
- Resource type
- Staff required
- Capacity
- Minimum notice
- Maximum advance window
- Buffer before
- Buffer after
- Cancellation policy
- Deposit
- Full payment required
- Waitlist
- Recurrence
- Group booking
- Check-in
- No-show rules
- Confirmation mode
- Overbooking policy

## 11.8 Inventory form

- SKU
- Variant
- Warehouse
- Location
- On-hand
- Reserved
- Safety stock
- Reorder point
- Reorder quantity
- Batch tracking
- Serial tracking
- Expiry tracking
- Cost
- Supplier
- Status

## 11.9 Customer form

- Name
- Type
- Email
- Phone
- Addresses
- Tags
- Segment
- Notes
- Preferences
- Marketing consent
- WhatsApp consent
- Tax number
- Portal access
- Custom fields

## 11.10 Payment provider form

- Provider type
- Display name
- Public key
- Secret reference
- Webhook secret
- Environment
- Supported currencies
- Supported methods
- Default
- Facility scope
- Status
- Test connection

## 11.11 Communication connector form

- Channel
- Provider
- OAuth connect
- Sender identity
- Phone number
- Email
- Template sync
- Default channel
- Transactional enabled
- Marketing enabled
- Consent required
- Usage limit
- Test message
- Disconnect

## 11.12 Automation form

- Name
- Status
- Trigger
- Conditions
- Actions
- Delay
- Schedule
- Channel
- Template
- Recipients
- Retry policy
- Escalation
- Test run
- Activate
- Pause
- Version history

---

# 12. AVAILABILITY, OVERBOOKING, STOCK, AND RESERVATION ENGINE

## 12.1 Availability types

Support:

- Quantity-based stock
- Time-slot appointments
- Capacity-based classes
- Date-range reservations
- Resource bookings
- Multi-resource bookings
- Variant availability
- Maintenance blocks
- Blackout dates
- External calendar blocks

## 12.2 Stock formula

```text
Sellable Stock
=
On Hand
− Reserved
− Safety Stock
```

## 12.3 Booking capacity formula

```text
Available Capacity
=
Maximum Capacity
− Confirmed Capacity
− Held Capacity
```

## 12.4 Overlap rule

```text
existing.start < requested.end
AND
existing.end > requested.start
```

## 12.5 Hold lifecycle

```text
AVAILABLE
→ HELD
→ CONFIRMED

or

AVAILABLE
→ HELD
→ EXPIRED
→ AVAILABLE
```

## 12.6 Required records

- AvailabilityRule
- AvailabilityBlock
- BookingHold
- Booking
- BookingResource
- InventoryReservation
- CapacityAllocation
- ResourceSchedule

## 12.7 Product reservation flow

```text
Customer chooses variant
→ Availability check
→ Inventory row lock
→ Inventory reservation
→ Start checkout
→ Payment success
→ Convert reservation to allocation
→ Reduce stock
→ Confirm order
```

On failure:

```text
Payment failed or hold expired
→ Release reservation
→ Restore available quantity
```

## 12.8 Appointment flow

```text
Select service
→ Select staff/resource
→ Show available slots
→ Create temporary hold
→ Collect deposit if required
→ Confirm booking
→ Send notification
```

## 12.9 Multi-resource booking

Example:

```text
Doctor
+ Room
+ Equipment
```

All resources must be held in one transaction.

If any hold fails, roll back all holds.

## 12.10 Database protection

Use:

- `select_for_update`
- unique constraints
- exclusion constraints where appropriate
- idempotency keys
- transaction.atomic
- source-of-truth PostgreSQL
- Redis only for short-lived acceleration and countdowns

---

# 13. EVENTS AND WORKFLOWS

Use internal domain events and a transactional outbox.

Examples:

- organization.created
- module.activated
- module.cancelled
- website.published
- product.created
- stock.low
- cart.abandoned
- order.created
- order.paid
- order.shipped
- booking.held
- booking.confirmed
- booking.cancelled
- payment.failed
- invoice.created
- customer.created
- review.submitted

Outbox flow:

```text
Database transaction
├── Save business record
└── Save outbox event

Background publisher
└── Dispatch event to handlers
```

Example:

```text
booking.confirmed
├── Send email
├── Send WhatsApp
├── Update analytics
├── Create invoice
├── Add loyalty points
└── Trigger automation
```

---

# 14. SEARCH

Global search must support:

- Customers
- Products
- Services
- Orders
- Bookings
- Staff
- Assets
- Projects
- Documents
- Website pages

Use PostgreSQL full-text and pg_trgm first.

Do not introduce OpenSearch in MVP.

---

# 15. FILES AND MEDIA

Support:

- Logos
- Product images
- Gallery images
- Staff photos
- Documents
- Invoices
- Contracts
- Attachments
- Evidence files

Requirements:

- Signed uploads
- Tenant-aware paths
- File metadata
- Access rules
- Image resizing
- Responsive variants
- WebP or AVIF
- Virus scanning hook
- CDN delivery
- Retention
- Delete
- Archive
- Audit

---

# 16. SECURITY AND MULTI-TENANCY

Mandatory:

- Organization-scoped querysets
- Facility-scoped permissions
- Tenant-aware cache keys
- Tenant-aware Celery tasks
- Tenant-aware file paths
- Audit logs
- CSRF protection
- XSS protection
- Secure cookies
- Session security
- Rate limiting
- MFA readiness
- Password reset
- Email verification
- Idempotency
- Secret storage in Key Vault
- No secrets in database plaintext
- No cross-tenant object access
- Object-level authorization
- Data export
- Data deletion
- Retention policies
- Consent history

---

# 17. API DESIGN

Use Django Ninja.

Namespaces:

```text
/api/v1/auth
/api/v1/organizations
/api/v1/facilities
/api/v1/marketplace
/api/v1/subscriptions
/api/v1/websites
/api/v1/catalogue
/api/v1/commerce
/api/v1/bookings
/api/v1/inventory
/api/v1/customers
/api/v1/staff
/api/v1/payments
/api/v1/communications
/api/v1/marketing
/api/v1/projects
/api/v1/assets
/api/v1/documents
/api/v1/automation
/api/v1/analytics
```

Requirements:

- Versioning
- Pagination
- Filtering
- Sorting
- Idempotency
- Rate limits
- Request IDs
- Tenant context
- Permission checks
- OpenAPI
- Error schema
- Audit

---

# 18. TESTING

Required:

- Unit tests
- Service tests
- Permission tests
- Entitlement tests
- Multi-tenant isolation tests
- Billing tests
- Website rendering tests
- Booking conflict tests
- Stock reservation tests
- Payment webhook tests
- Workflow tests
- Celery task tests
- Accessibility tests
- Playwright end-to-end tests
- k6 load tests later

Critical E2E scenarios:

1. Free website onboarding
2. Activate catalogue
3. Website gains catalogue pages
4. Activate commerce
5. Website gains cart and checkout
6. Buy appointment module
7. Website gains booking
8. Disable module
9. Website hides feature
10. Data retained
11. Reactivate module
12. Data restored
13. Two users attempt last stock item
14. Two users attempt same appointment slot
15. Payment webhook duplicate
16. Subscription payment failure
17. Trial expiry
18. Bundle activation
19. Feature-level add-on activation

---

# 19. PHASED IMPLEMENTATION ROADMAP

## Phase 1 — Platform Foundation

- Django project
- Organization tenancy
- Facilities
- Authentication
- Roles
- Permissions
- Audit
- Module registry
- Entitlements
- Marketplace foundation
- Subscription foundation
- Basic website
- Template system
- Theme tokens
- Publish flow
- Basic analytics
- Free subdomain

## Phase 2 — Catalogue and First Customer

For the dress website:

- Business Core
- Website Pro
- Catalogue
- Products
- Categories
- Collections
- Sizes
- Colours
- Variants
- Images
- Price
- Direct WhatsApp inquiry
- SEO
- Basic analytics
- Admin forms
- Responsive public website

No cart or payment yet.

## Phase 3 — Commerce Upgrade

- Cart
- Checkout
- Orders
- Inventory
- Payment provider
- Customer portal
- Shipping rules
- Transactional email
- Returns
- Refund requests

## Phase 4 — Appointments

- Services
- Staff
- Availability
- Slots
- Holds
- Booking
- Calendar
- Reminders
- Rescheduling
- Cancellation
- Deposits

## Phase 5 — Communication and Automation

- Gmail
- WhatsApp Business
- SMS
- Templates
- Reminders
- Delivery logs
- Automation rules

## Phase 6 — POS, CRM, Loyalty, Projects, Assets

Build only after customer demand.

---

# 20. CURRENT DRESS CUSTOMER CONFIGURATION

Active now:

```text
Business Core
Website Pro
Catalogue & Offerings
Basic Analytics
Direct WhatsApp Inquiry
```

Public website:

- Home
- Shop
- Collections
- Product Details
- About
- Contact
- Size Guide
- Shipping Information
- Return Policy
- Privacy Policy
- Terms

Admin:

```text
Dashboard
Website
Products
Categories
Collections
Sizes
Colours
Media
Analytics
Marketplace
Settings
```

Direct WhatsApp message:

```text
Hi, I’m interested in:

{{ product.name }}
Product code: {{ product.code }}
Size: {{ selected_size }}
Colour: {{ selected_colour }}
Price: {{ product.price }}

Product:
{{ product_url }}

Please confirm availability.
```

Later activation:

```text
Commerce
Inventory
Payments
Shipping
Customer Portal
```

Then the same website automatically gains:

- Add to Cart
- Buy Now
- Cart
- Checkout
- Online payment
- Customer account
- Order tracking

---

# 21. PROJECT STRUCTURE

```text
business_os/
├── config/
│   ├── settings/
│   ├── urls.py
│   ├── celery.py
│   └── asgi.py
├── apps/
│   ├── core/
│   ├── accounts/
│   ├── organizations/
│   ├── facilities/
│   ├── permissions/
│   ├── marketplace/
│   ├── subscriptions/
│   ├── entitlements/
│   ├── websites/
│   ├── catalogue/
│   ├── commerce/
│   ├── bookings/
│   ├── inventory/
│   ├── crm/
│   ├── workforce/
│   ├── payments/
│   ├── communications/
│   ├── marketing/
│   ├── operations/
│   ├── assets/
│   ├── documents/
│   ├── automation/
│   ├── analytics/
│   ├── integrations/
│   └── industry_extensions/
├── templates/
│   ├── admin/
│   ├── superadmin/
│   ├── components/
│   ├── websites/
│   └── emails/
├── static/
├── tests/
├── docker/
├── scripts/
└── docs/
```

Each app should contain:

```text
models.py
services.py
selectors.py
forms.py
views.py
urls.py
api.py
tasks.py
events.py
permissions.py
entitlements.py
navigation.py
website.py
admin.py
tests/
templates/
```

Keep business logic out of views, templates, signals, serializers, and models where practical.

Use service classes and explicit domain operations.

---

# 22. CODING RULES

- Use explicit types.
- Use service functions for business actions.
- Use selectors for complex reads.
- Use transactions for all critical writes.
- Use outbox events.
- Avoid hidden signal-based business logic.
- Avoid god models.
- Avoid giant generic JSON blobs for core business data.
- Use JSON only for flexible configuration.
- Use extension models for specialized industry data.
- Keep migrations clean.
- Write tests with every feature.
- Create reusable template components.
- Keep UI strings translatable.
- Support RTL.
- Make mobile behavior explicit.
- Document all public APIs.
- Record audit events for security-sensitive and billing-sensitive actions.

---

# 23. ACCEPTANCE CRITERIA

The implementation is acceptable only if:

1. One tenant cannot access another tenant’s data.
2. Admin navigation changes automatically based on entitlements.
3. Public website changes automatically based on entitlements.
4. Module activation provisions required pages and settings.
5. Module cancellation hides public features without deleting data.
6. Direct WhatsApp inquiry works without WhatsApp Business API.
7. Commerce activation reuses existing catalogue data.
8. Stock overselling is prevented.
9. Booking overbooking is prevented.
10. Payment webhook retries are idempotent.
11. Superadmin can configure prices, features, bundles, trials, limits, and visibility.
12. Business users can customize modules and pay only for selected features.
13. One organization receives one consolidated invoice.
14. Website editor supports draft, preview, publish, and rollback.
15. Admin and public websites are responsive, accessible, multilingual, and RTL-ready.
16. Empty states, errors, loading, success, cancellation, and recovery flows are implemented.
17. The first dress customer can go live with catalogue and WhatsApp inquiry before commerce is built.
18. Later commerce activation does not require rebuilding the website or re-entering products.

---

# 24. FINAL IMPLEMENTATION INSTRUCTION

Start by creating:

1. Architecture documentation
2. Django project scaffold
3. Core tenancy
4. Module registry
5. Entitlement engine
6. Marketplace data model
7. Website engine
8. Catalogue module
9. Dress customer template pack
10. Direct WhatsApp inquiry
11. Basic analytics
12. Tests
13. Seed data
14. Docker setup
15. Local development instructions

Do not attempt to build every module in one pass.

Build the platform foundation and the dress catalogue customer first, while keeping interfaces and extension points ready for the later modules described in this specification.


# BUSINESS OS MASTER SPECIFICATION — VERSION 2 COMPLETION ADDENDUM

> This section is normative. Where it conflicts with an earlier section, this section takes precedence. Codex must treat the entire document as a product specification, not as permission to build every feature in one pass.

# 25. CANONICAL DOMAIN AND ROUTING ARCHITECTURE

Assume the platform root domain is configurable through `PLATFORM_ROOT_DOMAIN`. Examples below use `businessos.com`.

## 25.1 Domain map

| Surface | Canonical host | Audience |
|---|---|---|
| Marketing site | `businessos.com` | Prospects and public |
| Business admin | `app.businessos.com` | Owners, managers, staff |
| Platform superadmin | `platform.businessos.com` | Business OS team only |
| Public API | `api.businessos.com` | Apps and integrations |
| Documentation | `docs.businessos.com` | Developers and customers |
| Status | `status.businessos.com` | Public service health |
| Generated sites | `{site_slug}.businessos.com` | Business customers |
| Custom sites | Customer-owned domain | Business customers |
| Preview | `{token}.preview.businessos.com` | Authorized preview users |

For organization Nova:

```text
Public generated website:
https://nova.businessos.com

Optional custom website:
https://www.novafashion.com

Business admin:
https://app.businessos.com/o/nova/dashboard

Customer portal:
https://nova.businessos.com/account
or
https://www.novafashion.com/account

Platform organization workspace:
https://platform.businessos.com/organizations/nova
```

The slug is navigational, not a security boundary. Resolve organization UUID and enforce tenant scope on every request.

## 25.2 Host isolation

- Public website hosts expose no business-admin or platform-admin routes.
- `app` accepts business users only.
- `platform` accepts authorized platform staff only.
- Platform roles and tenant roles are separate.
- Cookies are host-scoped by default.
- Do not share privileged cookies across wildcard subdomains.
- CSRF trusted origins are explicit.
- Redirect destinations are allow-listed.
- Custom domains never expose platform administration.
- Customer portal sessions are isolated from business-admin sessions.
- Platform support access uses a separate audited support session.

## 25.3 Domain lifecycle

States:

```text
REQUESTED
DNS_PENDING
VERIFYING
VERIFIED
SSL_PENDING
ACTIVE
FAILED
SUSPENDED
REMOVED
```

Domain form:

- Domain name
- Primary-domain toggle
- Redirect generated subdomain toggle
- Redirect www/non-www selection
- Verification method
- DNS records
- Verification status
- Last checked
- SSL status
- Canonical status
- Retry verification
- Remove domain

Flow:

```text
Add domain
→ Validate syntax
→ Check domain is not assigned elsewhere
→ Generate DNS instructions
→ Verify ownership
→ Provision TLS
→ Mark active
→ Select canonical host
→ Configure redirects
→ Purge CDN
```

# 26. ACTOR, PORTAL, AND PERMISSION MODEL

## 26.1 Actors

- Anonymous website visitor
- Registered customer
- Business owner
- Business administrator
- Facility manager
- Department manager
- Staff member
- Cashier
- Website editor
- Catalogue manager
- Inventory manager
- Booking manager
- Finance manager
- Marketing manager
- Support agent
- Platform owner
- Platform administrator
- Platform billing administrator
- Platform support administrator
- Platform support read-only
- Marketplace manager
- Template manager
- Operations engineer
- Security auditor
- Finance viewer

## 26.2 Permission dimensions

Permissions include:

```text
resource
action
organization scope
facility scope
department scope
ownership scope
field visibility
approval limit
financial limit
export permission
sensitive-data permission
```

Actions:

```text
view
create
edit
delete
archive
restore
approve
reject
cancel
refund
export
import
publish
configure
assign
override
impersonate
```

## 26.3 Customer portal

Navigation is entitlement-aware:

```text
Overview
Profile
Addresses
Orders
Returns
Appointments
Reservations
Memberships
Loyalty
Payments
Invoices
Documents
Reviews
Notifications
Communication Preferences
Privacy & Data
Security
```

Customer flows:

- Register
- Verify email
- Sign in
- Social sign-in where enabled
- Password reset
- Claim guest order
- Manage addresses
- View order
- Request cancellation
- Request return
- Download invoice
- Reschedule booking
- Cancel booking
- Manage membership
- View points
- Manage consent
- Export data
- Request account deletion

# 27. FACILITY MODEL AND FACILITY-AWARE ADAPTATION

## 27.1 Facility concept

A facility is an operational location or unit belonging to an organization.

Examples:

- Retail store
- Online-only store
- Salon
- Clinic
- Restaurant
- Hotel
- Resort
- Warehouse
- Office
- School
- Training center
- Gym
- Sports club
- Golf club
- Court venue
- Co-working location
- Rental branch
- Workshop
- Factory
- Construction site
- Property
- Farm
- Event venue
- Professional office
- Service area

A facility has:

- Name
- Code
- Facility type
- Address
- Coordinates
- Timezone
- Currency
- Languages
- Contact details
- Operating hours
- Holiday calendar
- Tax registration
- Active modules
- Capability overrides
- Default warehouse
- Default price list
- Default payment provider
- Default notification sender
- Public visibility
- Website association
- Status

## 27.2 Facility profile schema

```text
Facility Type
→ Terminology Pack
→ Default Modules
→ Recommended Modules
→ Default Forms
→ Default Navigation
→ Default Website Sections
→ Default Dashboard Widgets
→ Default Workflows
→ Default Reports
```

## 27.3 Terminology packs

UI labels must be configurable without changing domain models.

Examples:

| Generic | Salon | Clinic | Hotel | Restaurant | Education |
|---|---|---|---|---|---|
| Customer | Client | Patient | Guest | Guest | Student |
| Offering | Service | Treatment | Room/Service | Menu Item | Course |
| Booking | Appointment | Appointment | Reservation | Reservation | Enrollment |
| Resource | Staff/Chair | Practitioner/Room | Room | Table | Trainer/Room |
| Order | Sale | Invoice | Folio | Order | Enrollment Invoice |

Never change database table names based on terminology.

## 27.4 Facility-aware forms

Form schema resolution:

```text
Base module form
+ facility-type field rules
+ organization custom fields
+ entitlement visibility
+ user permission visibility
+ country rules
= rendered form
```

Every field schema supports:

- key
- label
- help text
- placeholder
- input type
- required
- visible
- editable
- default
- validation
- choices
- section
- order
- entitlement
- permission
- facility types
- countries
- conditional rules

# 28. MARKETPLACE, MODULE, SUBMODULE, CAPABILITY, CONNECTOR, AND BUNDLE MODEL

## 28.1 Commercial hierarchy

```text
Module
├── Included capabilities
├── Optional submodules
├── Optional premium capabilities
├── Optional connectors
├── Limits
└── Usage meters

Bundle
└── Discounted combination of the above
```

Definitions:

- Module: broad product domain.
- Submodule: coherent optional feature set inside a module.
- Capability: smallest entitlement-controlled behavior.
- Connector: integration with an external provider.
- Limit: quota.
- Usage meter: billable consumption.
- Bundle: discounted selection; not a separate implementation.

## 28.2 Purchase rules

Customers may:

- Buy a complete module.
- Buy a base module plus selected submodules.
- Add an individual capability if dependencies are satisfied.
- Select one connector without selecting unrelated connectors.
- Buy a bundle.
- Upgrade or downgrade.
- Change quantity.
- Start a trial.
- Schedule cancellation.

Do not charge for tiny usability necessities. Base module must remain functional.

## 28.3 Capability examples

```text
website.basic
website.custom_domain
website.blog
website.multilingual
website.advanced_seo

catalogue.basic
catalogue.variants
catalogue.advanced_filters
catalogue.whatsapp_inquiry

commerce.cart
commerce.checkout
commerce.coupons
commerce.gift_cards
commerce.returns
commerce.wishlist

booking.appointments
booking.resources
booking.date_range
booking.waitlist
booking.group_capacity

communication.whatsapp_business
communication.gmail
communication.microsoft365
communication.sms
communication.push
communication.unified_inbox
```

## 28.4 Dependency types

- Required
- Optional
- Recommended
- Conflicting
- Replaced by
- Minimum version
- Country restricted
- Facility restricted
- Industry restricted

## 28.5 Marketplace checkout

Steps:

```text
Select
→ Customize
→ Resolve dependencies
→ Show additions to admin and website
→ Show limits and usage fees
→ Show subtotal
→ Apply bundle discount
→ Apply coupon
→ Calculate tax
→ Show renewal date
→ Confirm
→ Pay
→ Activate
```

# 29. MODULE CATALOGUE: SUBMODULES, FORMS, UI, WEBSITE CONTRIBUTIONS, AND PURCHASE UNITS

## 29.1 Business Core

Included:

- Organization
- One facility
- Owner user
- Basic roles
- Settings
- Audit foundation
- Marketplace
- Basic website
- Basic analytics

Optional purchase units:

- Additional facilities
- Additional staff seats
- Advanced permissions
- Custom fields
- Advanced import/export
- Increased storage
- White labeling

Admin navigation:

```text
Dashboard
Marketplace
Settings
```

Core forms:

- Organization
- Facility
- User
- Role
- Permission
- Business hours
- Holiday
- Tax profile
- Localization
- Branding
- Data retention

## 29.2 Website & Content

Submodules:

- Basic Website
- Website Pro
- Blog
- Advanced SEO
- Multilingual
- Custom Domain
- Premium Template
- Landing Pages
- Forms
- White Label

Admin:

```text
Website
├── Overview
├── Pages
├── Sections
├── Navigation
├── Theme
├── Media
├── Blog
├── Forms
├── SEO
├── Domains
├── Languages
├── Publishing
└── Analytics
```

Website contributions:

- Pages
- Header
- Footer
- Hero
- About
- Gallery
- Contact
- Opening hours
- Location
- Social links
- WhatsApp contact action

Forms:

Page, section, navigation, theme, SEO, domain, language, redirect, publish.

## 29.3 Catalogue & Offerings

Submodules:

- Basic Catalogue
- Variants
- Advanced Attributes
- Collections
- Advanced Search and Filters
- Packages and Bundles
- Add-ons
- Digital Downloads
- Catalogue PDF
- WhatsApp Inquiry

Admin:

```text
Catalogue
├── Offerings
├── Categories
├── Collections
├── Attributes
├── Options
├── Variants
├── Add-ons
├── Price Lists
├── Media
└── Settings
```

Facility adaptations:

- Retail: Product, SKU, size, color.
- Salon: Service, duration, eligible staff.
- Clinic: Treatment, practitioner type.
- Hotel: Room type, occupancy, amenities.
- Restaurant: Menu item, modifiers.
- Education: Course, trainer, duration.
- Rental: Rental item, deposit.
- Events: Ticket type, capacity.

## 29.4 Commerce, Orders & POS

Submodules:

- Online Store
- Checkout
- Discounts
- Coupons
- Wishlist
- Gift Cards
- Returns
- Exchanges
- Subscriptions
- POS
- Shipping
- Cash on Delivery

Admin:

```text
Sales
├── Orders
├── Quotes
├── Carts
├── Returns
├── Refunds
├── Discounts
├── Coupons
├── Gift Cards
├── Fulfilment
├── POS
└── Settings
```

State machines:

```text
DRAFT
PENDING_PAYMENT
PAID
CONFIRMED
PROCESSING
PARTIALLY_FULFILLED
FULFILLED
DELIVERED
CANCELLED
RETURNED
PARTIALLY_REFUNDED
REFUNDED
DISPUTED
```

Forms:

Cart, checkout, address, order, quote, discount, coupon, gift card, return, exchange, fulfilment, shipment, POS session.

## 29.5 Scheduling, Appointments & Reservations

Purchasable submodules:

- Appointments
- Resource Booking
- Date-range Reservations
- Classes and Capacity
- Waitlist
- Recurring Booking
- Group Booking
- Deposits
- Check-in
- External Calendar Sync

Admin:

```text
Bookings
├── Calendar
├── Appointments
├── Reservations
├── Resources
├── Availability
├── Schedules
├── Blocks
├── Waitlist
├── Check-in
└── Settings
```

Facility behavior:

- Salon: service + staff + chair.
- Clinic: treatment + practitioner + room.
- Hotel: room + date range + guests.
- Restaurant: table + time + party size.
- Sports: court + slot.
- Golf: tee time + player capacity.
- Rental: asset + date range.
- Class: instructor + room + seat capacity.

Forms:

Booking type, service availability, resource, schedule, block, cancellation policy, deposit rule, capacity, hold, booking, participant, check-in.

## 29.6 Inventory, Procurement & Warehouse

Submodules:

- Basic Inventory
- Multi-location
- Procurement
- Warehouse
- Batch/Lot
- Serial Tracking
- Expiry Tracking
- Barcode
- Advanced Replenishment

Admin:

```text
Inventory
├── Overview
├── Stock
├── Movements
├── Reservations
├── Adjustments
├── Transfers
├── Warehouses
├── Suppliers
├── Purchase Orders
├── Receiving
├── Counts
└── Settings
```

Forms:

Inventory item, level, warehouse, bin, supplier, PO, goods receipt, transfer, adjustment, count, batch, serial.

## 29.7 Customers, CRM & Relationships

Submodules:

- Customer Directory
- Leads
- Pipeline
- Segmentation
- Customer Portal
- Advanced Consent
- Relationship Mapping

Admin:

```text
Customers
├── All
├── Leads
├── Pipeline
├── Segments
├── Groups
├── Activities
├── Portal
└── Settings
```

Forms:

Person, organization, role, address, contact, note, tag, segment, lead, activity, consent, portal invitation.

## 29.8 Workforce, Partners & Access

Submodules:

- Staff Directory
- Scheduling
- Attendance
- Leave
- Skills
- Certifications
- Commission
- Partner/Vendor Portal
- Advanced Access

Admin:

```text
Team
├── Staff
├── Schedules
├── Shifts
├── Attendance
├── Leave
├── Skills
├── Certifications
├── Assignments
├── Commissions
└── Access
```

## 29.9 Payments, Billing & Finance

Submodules:

- Payment Gateway
- Payment Links
- Invoices
- Expenses
- Recurring Billing
- Payouts
- Reconciliation
- Accounting Connector

Admin:

```text
Finance
├── Overview
├── Payments
├── Invoices
├── Receipts
├── Refunds
├── Expenses
├── Credit Notes
├── Payouts
├── Reconciliation
├── Taxes
└── Settings
```

Never store raw card data. Use hosted/tokenized provider flows.

## 29.10 Communication & Notifications

Purchasable independently:

- WhatsApp Business
- Gmail
- Microsoft 365
- Custom SMTP
- Transactional Email Provider
- SMS
- Push
- Unified Inbox
- Advanced Templates
- Automated Reminders

Admin:

```text
Communications
├── Inbox
├── Messages
├── Templates
├── Scheduled
├── Delivery
├── Channels
├── Senders
├── Consent
└── Settings
```

A direct WhatsApp link remains a website/catalogue capability, not this module.

## 29.11 Marketing, Loyalty & Reputation

Submodules:

- Campaigns
- Promotions
- Loyalty
- Rewards
- Referrals
- Reviews
- Reputation
- Abandoned Cart
- Advanced Segmentation

Admin:

```text
Marketing
├── Campaigns
├── Audiences
├── Promotions
├── Loyalty
├── Rewards
├── Referrals
├── Reviews
├── Reputation
└── Analytics
```

## 29.12 Work, Projects & Service Operations

Submodules:

- Projects
- Tasks
- Time Tracking
- Field Service
- Work Orders
- Helpdesk
- SLA
- Customer Approval

Admin:

```text
Work
├── Projects
├── Boards
├── Tasks
├── Jobs
├── Work Orders
├── Tickets
├── Calendar
├── Time
├── Approvals
└── Reports
```

## 29.13 Assets, Facilities & Fleet

Submodules:

- Asset Register
- Preventive Maintenance
- Inspections
- Facility Management
- Property Units
- Fleet
- Metering
- QR Labels

Admin:

```text
Assets
├── Register
├── Locations
├── Maintenance
├── Inspections
├── Downtime
├── Meters
├── Fleet
├── Documents
└── Reports
```

## 29.14 Documents, Forms & Compliance

Submodules:

- Form Builder
- Document Generation
- Agreements
- E-signature
- Checklists
- Inspections
- Compliance
- Risk
- Safety
- Quality

Admin:

```text
Documents & Compliance
├── Forms
├── Submissions
├── Documents
├── Templates
├── Agreements
├── Signatures
├── Checklists
├── Inspections
├── Compliance
├── Risks
├── Incidents
└── Corrective Actions
```

## 29.15 Automation, Rules & Integrations

Submodules:

- Automation Lite
- Advanced Workflow
- Approval Workflow
- Pricing Rules
- Availability Rules
- Webhooks
- API Access
- Google Connector
- Microsoft Connector
- Accounting Connector
- Courier Connector

Admin:

```text
Automation
├── Workflows
├── Templates
├── Runs
├── Approvals
├── Rules
├── Connections
├── Webhooks
├── API Keys
└── Logs
```

## 29.16 Analytics, Reporting & AI

Submodules:

- Basic Analytics
- Advanced Dashboards
- Custom Reports
- Scheduled Reports
- Data Export
- AI Assistant
- Forecasting
- Recommendations
- Content Generation

Admin:

```text
Analytics
├── Overview
├── Dashboards
├── Reports
├── Scheduled
├── Exports
├── AI Assistant
├── Usage
└── Settings
```

## 29.17 Industry Extensions

Each industry pack declares:

- Required modules
- Recommended modules
- Specialized models
- Terminology
- Forms
- Navigation
- Website sections
- Workflows
- Reports
- Permissions
- Compliance warnings

Initial packs:

- Fashion and Retail
- Salon and Beauty
- Clinic
- Restaurant
- Hotel
- Sports Facility
- Golf
- Gym and Fitness
- Education
- Rental
- Professional Services
- Field Services
- Property
- Construction
- Manufacturing
- Events
- Agriculture

# 30. DETAILED STATE MACHINES

## 30.1 Product

```text
DRAFT
→ REVIEW
→ SCHEDULED
→ ACTIVE
→ HIDDEN
→ ARCHIVED
```

## 30.2 Booking

```text
DRAFT
→ HELD
→ PENDING_PAYMENT
→ CONFIRMED
→ CHECKED_IN
→ COMPLETED

Alternatives:
WAITLISTED
CANCELLED
NO_SHOW
EXPIRED
REFUNDED
```

## 30.3 Subscription

```text
DRAFT
→ TRIALING
→ ACTIVE
→ PAST_DUE
→ GRACE_PERIOD
→ SUSPENDED
→ CANCELLED
→ EXPIRED
```

## 30.4 Invoice

```text
DRAFT
→ ISSUED
→ PARTIALLY_PAID
→ PAID

Alternatives:
VOID
OVERDUE
REFUNDED
PARTIALLY_REFUNDED
```

## 30.5 Website

```text
DRAFT
→ PREVIEW
→ SCHEDULED
→ PUBLISHED
→ UNPUBLISHED
→ ARCHIVED
```

# 31. BILLING EDGE CASES

Support:

- Upgrade now with proration
- Upgrade next renewal
- Downgrade next renewal
- Quantity changes
- Monthly to annual
- Annual to monthly at renewal
- Trial conversion
- Trial expiry
- Failed payment retries
- Grace period
- Dunning
- Card expiry
- Account credit
- Refund
- Partial refund
- Chargeback
- Price grandfathering
- Future price changes
- Offline enterprise billing
- Purchase-order billing
- Tax-inclusive/exclusive pricing
- Bundle item removal
- Bundle discount recalculation

Every price calculation creates an immutable calculation snapshot.

# 32. SHIPPING, TAX, AND FULFILMENT

Shipping:

- Zones
- Countries
- Regions
- Postal codes
- Flat rate
- Weight based
- Price based
- Free threshold
- Local delivery
- Store pickup
- Delivery windows
- Courier
- Labels
- Tracking
- Split shipment
- Failed delivery
- Return shipping
- Proof of delivery

Tax:

- Jurisdiction
- Registration
- Category
- Rate
- Inclusive/exclusive
- Zero-rated
- Exempt
- Shipping tax
- Discount treatment
- Rounding
- Immutable transaction snapshot

# 33. IMPORT, EXPORT, AND MIGRATION

Import flow:

```text
Upload
→ Map fields
→ Validate
→ Preview
→ Detect duplicates
→ Dry run
→ Confirm
→ Background import
→ Result summary
→ Download error file
→ Rollback when supported
```

Support:

- Customers
- Products
- Variants
- Inventory
- Suppliers
- Bookings
- Orders
- Staff
- Assets

Export:

- Current view
- Full module
- Full tenant
- Personal data
- Scheduled export

# 34. OBSERVABILITY, OPERATIONS, BACKUP, AND DISASTER RECOVERY

Logging:

- JSON
- Timestamp
- Environment
- Service
- Organization ID
- Facility ID
- User ID
- Request ID
- Trace ID
- Job ID
- Event
- Severity
- Sanitized context

Health:

```text
/health/live
/health/ready
/health/database
/health/redis
/health/workers
```

Monitor:

- Error rate
- Latency
- Queue depth
- Failed jobs
- Failed webhooks
- Database connections
- Slow queries
- Payment failures
- Booking conflicts
- Domain failures
- Publish failures

Backup:

- Automated database backup
- Point-in-time recovery
- Blob versioning
- Retention
- Quarterly restore test
- Recovery runbook
- Initial RPO target: 15 minutes
- Initial RTO target: 4 hours

# 35. PRIVACY, SECURITY, LEGAL, AND AUDIT

Privacy:

- Terms versions
- Privacy versions
- Acceptance history
- Cookie categories
- Consent
- Export
- Deletion
- Anonymization
- Retention
- Legal hold
- Data residency configuration
- Subprocessor registry
- Sensitive-field classification
- Field masking

Do not claim formal compliance until verified.

Audit event:

- Actor
- Organization
- Facility
- Action
- Target
- Before
- After
- IP
- User agent
- Request ID
- Reason
- Support mode
- Source
- Timestamp

# 36. SUPPORT MODE AND SUPERADMIN ORGANIZATION WORKSPACE

Organization workspace:

```text
Overview
Business Profile
Facilities
Users
Active Modules
Capabilities
Subscription
Usage
Invoices
Payments
Website
Domains
Integrations
Health
Audit
Support
```

Support mode requires:

- Reason
- Ticket reference
- Read-only or controlled-write
- Duration
- MFA for sensitive access
- Visible banner
- Auto expiry
- Immediate exit
- Full audit

# 37. ACCESSIBILITY, LOCALIZATION, PWA, AND SEARCH

Accessibility target:

- WCAG 2.2 AA
- Keyboard
- Focus
- Screen reader
- Error summary
- Contrast
- Reduced motion
- Accessible calendar
- Accessible drag/drop alternative
- Axe tests

Localization:

- Per-language content
- Fallback
- RTL
- Locale URLs
- Date/time/number/currency formats
- Localized SEO
- Translation status

PWA:

- Manifest
- Installability
- Offline fallback
- Camera upload
- QR/barcode support
- Push readiness
- Low-bandwidth behavior

Search:

- Tenant scoped
- Permission filtered
- Full text
- Trigram typo tolerance
- Suggestions
- Filters
- Synonyms
- Multilingual normalization
- Search analytics

# 38. AI GOVERNANCE

- Provider abstraction
- Organization opt-in
- Model configuration
- Quotas
- Cost tracking
- Prompt templates
- Prompt versions
- Human approval
- Redaction
- Permission-aware retrieval
- No cross-tenant training
- Audit
- Feedback
- Rate limit
- Disable switch
- Failure fallback

# 39. DATABASE GOVERNANCE

Require:

- Explicit foreign-key deletion behavior
- Unique constraints
- Composite indexes
- Partial indexes
- Check constraints
- Soft-delete policy
- Archive policy
- Immutable transaction snapshots
- Optimistic locking where needed
- Cursor pagination for large datasets
- Query budgets
- Partition strategy for analytics/audit later

Separate:

```text
platform_billing_invoices
business_sales_invoices
```

Do not create ambiguous duplicate invoice tables.

# 40. CODEX DELIVERY PROTOCOL

Codex must not implement all modules in one uncontrolled generation.

For every phase:

1. Read this complete specification.
2. Produce an architecture decision record.
3. Produce an implementation plan.
4. List assumptions.
5. List affected modules.
6. List migrations.
7. List forms and routes.
8. List entitlements.
9. List tests.
10. Implement in small reviewable changes.
11. Run tests.
12. Update documentation.
13. Do not remove existing functionality without approval.

No placeholders such as TODO for mandatory business behavior.

Do not silently invent pricing, legal claims, provider credentials, tax rates, domain ownership, or customer data.

# 41. FINAL PRODUCT RULE

Business OS is one configurable platform.

```text
Organization
→ Facilities
→ Modules
→ Submodules
→ Capabilities
→ Connectors
→ Limits
→ Bundles
→ Entitlements
→ Dynamic Admin
→ Dynamic Website
→ Dynamic Customer Portal
```

The same entitlement decision must control:

- Navigation
- Routes
- Forms
- Fields
- APIs
- Website sections
- Customer portal
- Background jobs
- Usage
- Billing
- Reports
- Automation

Never rely only on hiding UI. Enforce access in backend services and queries.


# 42. FINAL UI/UX TECHNOLOGY DECISION — DAISYUI

> This section is normative and supersedes earlier recommendations that use Flowbite as the primary component system.

## 42.1 Final UI stack

Business Admin and Platform Superadmin:

```text
Django 5.2 LTS
+ Django Templates
+ HTMX
+ Alpine.js
+ Tailwind CSS
+ DaisyUI
+ Business OS Component Library
+ Lucide Icons
```

Generated business websites:

```text
Django Templates / Wagtail
+ Tailwind CSS
+ Business OS Website Design System
+ DaisyUI primitives where useful
+ Minimal Alpine.js
+ HTMX for server-driven interactions
```

Do not use Flowbite and DaisyUI as equal primary component systems. Avoid duplicate component systems, inconsistent styles, unnecessary JavaScript, and conflicting behavior.

## 42.2 DaisyUI role

DaisyUI is the low-level UI primitive layer for:

- Buttons
- Inputs
- Selects
- Checkboxes
- Radio controls
- Toggles
- Textareas
- File inputs
- Cards
- Alerts
- Badges
- Tabs
- Menus
- Drawers
- Dropdowns
- Modals
- Tooltips
- Accordions
- Steps
- Stats
- Skeletons
- Loading states
- Pagination
- Breadcrumbs
- Tables
- Timelines
- Toast presentation

DaisyUI is not the Business OS brand and is not the public website identity.

## 42.3 Business OS component library

Create reusable Django template components instead of repeating raw DaisyUI markup.

Required components:

```text
bos_button
bos_icon_button
bos_link_button
bos_input
bos_textarea
bos_select
bos_checkbox
bos_radio
bos_toggle
bos_date_input
bos_datetime_input
bos_money_input
bos_phone_input
bos_address_input
bos_file_upload
bos_search_input
bos_combobox
bos_form_field
bos_form_error
bos_error_summary
bos_card
bos_stat
bos_alert
bos_badge
bos_status_badge
bos_tabs
bos_breadcrumbs
bos_dropdown
bos_modal
bos_drawer
bos_toast
bos_empty_state
bos_skeleton
bos_table
bos_data_grid
bos_filter_bar
bos_pagination
bos_stepper
bos_page_header
bos_section_header
bos_action_menu
bos_confirmation_dialog
bos_permission_guard
bos_entitlement_guard
bos_upgrade_prompt
bos_usage_meter
bos_price
bos_avatar
bos_activity_item
bos_timeline
bos_command_palette
```

Each component must support:

- Accessible labels
- Keyboard navigation
- Disabled state
- Loading state
- Error state
- Help text
- Responsive behavior
- RTL
- Dark mode readiness
- Test selectors
- Analytics hooks where required

## 42.4 Business OS admin visual direction

Use:

- Clean neutral backgrounds
- High-contrast readable text
- One trustworthy primary brand color
- Limited accent colors
- Subtle borders
- Light shadows
- Medium corner radius
- Comfortable spacing
- Clear hierarchy
- Consistent status colors
- Minimal purposeful motion

Avoid:

- Excessive gradients
- Excessive glassmorphism
- Heavy shadows
- Over-rounded cards
- Too many colors
- Decorative animation in operational screens
- Dense forms without sections
- Icon-only actions without labels or tooltips
- Hidden critical actions

## 42.5 Theme architecture

Create a custom DaisyUI theme named `businessos`.

Theme tokens must be configurable centrally:

```text
primary
primary-content
secondary
secondary-content
accent
accent-content
neutral
neutral-content
base-100
base-200
base-300
base-content
info
success
warning
error
radius-selector
radius-field
radius-box
border
depth
noise
```

Do not hard-code brand colors across templates.

## 42.6 Admin density modes

Support:

- Comfortable
- Compact

Comfortable is default.

Density affects:

- Table row height
- Form spacing
- Card padding
- Navigation spacing

Do not reduce touch targets below accessibility requirements.

## 42.7 Responsive admin behavior

Desktop:

- Persistent sidebar
- Top bar
- Multi-column dashboard
- Data tables
- Side panels

Tablet:

- Collapsible sidebar
- Two-column layouts
- Responsive filters

Mobile:

- Drawer navigation
- Sticky primary action
- Card representation for wide tables
- Bottom navigation only for high-frequency actions
- Full-screen modal where appropriate
- Camera upload
- Large touch targets

## 42.8 Required UI states

Every page and component must define:

- Initial
- Loading
- Loaded
- Empty
- Filtered empty
- Validation error
- Permission denied
- Entitlement required
- Usage limit reached
- Offline or network failure
- Server failure
- Partial failure
- Success
- Read-only
- Archived
- Suspended

## 42.9 Marketplace UI

Marketplace module card:

- Icon
- Module name
- Description
- Category
- Recommended badge
- Active badge
- Trial badge
- Starting price
- Billing period
- Included capabilities
- Optional add-ons
- Website changes
- Admin changes
- Dependencies
- Usage charges
- Customize
- Compare
- Start trial
- Activate

Customization drawer:

```text
Module summary
Included features
Optional submodules
Individual capabilities
Connectors
Limits
Usage pricing
Dependencies
Recommended additions
Live price summary
Tax
Discount
Renewal date
Activate button
```

## 42.10 Entitlement-aware UI

The same entitlement decision must control:

- Sidebar item
- Dashboard widget
- Route
- View
- Form
- Field
- Action
- API
- Background job
- Website section
- Customer portal section
- Report
- Export
- Automation action

Never rely only on hidden UI.

Entitlement states:

```text
AVAILABLE
TRIAL_AVAILABLE
TRIALING
ACTIVE
LIMITED
PAST_DUE
READ_ONLY
SUSPENDED
EXPIRED
NOT_PURCHASED
NOT_AVAILABLE
```

## 42.11 Generated website design system

Do not expose raw DaisyUI theme names to business customers.

Customer-facing style choices:

- Minimal
- Modern
- Elegant
- Luxury
- Fashion
- Professional
- Friendly
- Bold
- Wellness
- Hospitality
- Technology
- Editorial

Website component families:

Header:
- Classic
- Centered
- Transparent
- Marketplace
- Minimal
- Sidebar

Hero:
- Minimal
- Split
- Editorial
- Product focused
- Service focused
- Booking focused
- Video
- Full bleed

Product card:
- Minimal
- Fashion
- Luxury
- Retail
- Compact
- Marketplace

Service card:
- Icon
- Image
- Price
- Duration
- Staff
- Booking CTA

Footer:
- Simple
- Multi-column
- Newsletter
- Brand focused
- Contact focused

## 42.12 Website theme tokens

Each website theme supports:

- Primary
- Secondary
- Accent
- Background
- Surface
- Text
- Muted text
- Heading font
- Body font
- Font scale
- Container width
- Section spacing
- Card radius
- Button radius
- Input radius
- Border width
- Shadow level
- Header style
- Footer style
- Image treatment
- Animation level

## 42.13 Website template contracts

Each template pack declares:

```yaml
code: fashion_editorial
version: 1.0.0
supported_modules:
  - website
  - catalogue
  - commerce
required_sections:
  - header
  - footer
supported_languages:
  - en
  - ar
rtl_supported: true
supported_capabilities:
  - catalogue.variants
  - catalogue.whatsapp_inquiry
  - commerce.cart
  - commerce.checkout
```

Support:

- Compatibility validation
- Module activation preview
- Safe template switching
- Missing-section fallback
- Content migration
- Template versioning
- Deprecation
- Upgrade
- Customization preservation

## 42.14 Specialized UI libraries

Use only when required:

```text
FullCalendar
→ Calendar and scheduling views

Apache ECharts
→ Dashboards and analytics

Flatpickr
→ Date and time selection

SortableJS
→ Section ordering and simple drag/drop

TipTap or Editor.js
→ Rich content editing

Leaflet
→ Maps

Cropper.js
→ Image cropping

FilePond or direct-upload component
→ Advanced uploads
```

Wrap external libraries in Business OS components.

## 42.15 Icons

Use Lucide as the primary icon library.

Rules:

- Use one icon style consistently.
- Do not use emoji as operational UI icons.
- Use official brand SVGs for provider logos.
- Include visible labels for unfamiliar actions.
- Add accessible names to icon-only controls.
- Keep icon size consistent.

## 42.16 Fonts

Admin:

- Inter or Geist
- Noto Sans Arabic
- Noto Sans Devanagari
- Noto Sans Malayalam

Generated websites:

- Curated open-source font catalogue
- Self-host where practical
- Per-language fallback
- Font-display optimization
- No arbitrary remote font injection

## 42.17 Accessibility

Target WCAG 2.2 AA.

Mandatory:

- Keyboard access
- Visible focus
- Skip links
- Semantic HTML
- Screen-reader labels
- Error summary
- Field errors
- Contrast validation
- Reduced-motion support
- Accessible dialogs
- Accessible drawers
- Accessible calendars
- Drag/drop alternatives
- Touch-target compliance
- Alt text
- RTL testing
- Automated Axe tests
- Manual keyboard tests

## 42.18 UI acceptance criteria

The UI implementation is accepted only when:

1. Business Admin and Superadmin use the same Business OS component library.
2. Generated websites do not look like raw DaisyUI demos.
3. Theme tokens are centralized.
4. Entitlement checks are enforced in backend and UI.
5. All pages implement required states.
6. Forms are accessible and responsive.
7. Tables have mobile alternatives.
8. RTL works.
9. Customer website templates preserve business identity.
10. DaisyUI can be upgraded without rewriting all templates.
