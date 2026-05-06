# Product Requirements Document

## Document metadata

- Product: EcommOS
- Internal codename: eos-beta
- Version: 2.2
- Date: 2026-04-09
- Status: Current-state PRD
- Audience: Product, engineering, operations, design, leadership

## 1. Executive summary

EcommOS is a multi-tenant, Nigeria-native pay-on-delivery order operations system. It is intentionally CRM-shaped in the interface, but operationally it behaves like an order, fulfillment, and remittance console for businesses that sell through landing pages and work orders through human teams.

The product is now broader than a lead queue. It currently includes:

- organization and membership setup
- email/password auth and invite-based staff onboarding
- product and form management
- package options with inventory component definitions
- public order intake
- order queue management with workflow gating
- in-app notifications
- inventory partner, stock, transfer, and movement workflows
- accounting accounts, categories, manual entries, remittance-linked revenue, and overview reporting
- a unified drawer/sheet interaction system across orders, staff, inventory, and accounting

This document is written to reflect the current live product state first. Intended work that is not yet shipped is called out only in the "Known gaps" section.

## 2. Product definition

EcommOS helps POD commerce teams move an order from marketing intake to confirmed, dispatched, delivered, and remitted, while keeping inventory and accounting tied to the real operational workflow.

The system is built around a few core truths:

- Orders are the center of the product.
- Contacts are intentionally lightweight, not full CRM records.
- Staff accountability matters more than opaque automation.
- Multi-tenancy is strict.
- Revenue is recognized on remittance, not just on delivery.
- Inventory should move based on fulfillment reality, not on assumptions.

## 3. Product goals

- Capture structured orders directly from public product forms.
- Route new orders to the right staff fairly and quickly.
- Give teams one queue to work lead, delivery, and remittance stages.
- Tie fulfillment decisions to real partner locations and stock balances.
- Tie remittance updates to accounting records.
- Keep the system simple enough for operational teams to adopt quickly.

## 4. Primary users

### Owners

- Set up organizations
- create products, forms, staff, inventory partners, and accounting structures
- monitor operations across all queues and modules

### Managers

- supervise queue agents
- assign and reassign orders
- manage staff scopes
- oversee inventory movement and accounting entries

### Staff / queue agents

- work assigned orders
- contact customers
- update lead, delivery, and remittance states

### Finance / operations admins

- review and manage accounting entries
- maintain accounts and categories
- reconcile remittances with revenue records

### Fulfillment / logistics admins

- create partner networks and locations
- receive HQ stock
- dispatch stock to partner locations
- confirm receipts and review stock movements

### External users

- customers submitting public forms
- invited staff joining an org through an invite link

## 5. Product principles

- Every tenant-facing record is organization-scoped.
- Orders move through explicit transitions, not arbitrary field edits.
- Delivery cannot skip lead confirmation.
- Remittance cannot skip delivery.
- Inventory and accounting should follow operational truth.
- The app should remain understandable to human operators on desktop and mobile.

## 6. Current product surface

### App navigation

The current authenticated app surface includes:

- Orders
- Products
- Staff
- Inventory
- Accounting
- Notifications

### Public routes

- sign in / sign up
- forgot password / reset password
- organization onboarding
- staff invite acceptance
- hosted public product forms

### Interaction architecture

- Desktop queue workflows use right-side drawers for in-place detail and transitions.
- Mobile queue workflows use bottom sheets for filters, control panels, and create/edit flows.
- Shared sheet primitives now include nested-overlay safety so nested selects/popovers do not dismiss parent sheets by mistake.
- Orders, Staff, Inventory, and Accounting use a common mobile control pattern:
  - compact section titles
  - stronger field labels in two-column rows
  - clear/apply action footers

## 7. Functional requirements by domain

## 7.1 Authentication, organizations, and tenancy

### Goal

Allow a user to authenticate once and operate inside one active organization at a time.

### Current capabilities

- Users can sign up and sign in with email/password.
- Users can request a password reset email.
- Users can reset their password via tokenized reset links.
- Authenticated API requests use Bearer tokens.
- Tenant-aware requests require `X-Org-Id`.
- A user can belong to multiple orgs.
- Users without an org are routed through organization creation.
- `/me` returns the authenticated user plus memberships and role scopes.
- Organization creation automatically creates an `OWNER` role and membership.

### Requirements

- Missing auth returns a standard error envelope.
- Missing or invalid org context is rejected.
- All tenant queries must be scoped by org.
- Password reset links must be safe to use without an existing session.

## 7.2 Roles, membership, and staff

### Goal

Represent the actual people who work orders and control access.

### Current capabilities

- Core roles include `OWNER`, `MANAGER`, and `STAFF`.
- Role scopes exist and are returned with memberships.
- Staff profiles are operational records and may exist before linked user accounts.
- Admins can create staff members with status and role.
- Admins can activate/deactivate staff.
- Admins can assign product scopes to staff.
- Staff can be invited via email and linked to accounts later.
- Invite flows support:
  - existing signed-in user acceptance
  - new account creation during acceptance

### Requirements

- Privileged access is required for staff management.
- Staff email must be unique per org.
- Staff cannot be linked to multiple staff records in the same org.
- Invite acceptance must enforce invited-email matching.

## 7.3 Products

### Goal

Represent sellable operational products and the intake channels that create orders for them.

### Current capabilities

- Products can be created and listed.
- Each product has a name, short code, and default price.
- Product short code is unique per org.
- Products store the last assigned staff member for round-robin assignment continuity.

## 7.4 Product forms

### Goal

Give each product one or more structured order intake endpoints.

### Current capabilities

- A product can have multiple forms.
- Each form has:
  - public key
  - name
  - status
  - schema version
  - form schema payload
- Hosted public form URLs are generated.
- API submit URLs are generated.
- Product detail UI exposes a copyable embed snippet.

### Product stance

Forms are not optional extras. They are the canonical intake surface for most new orders.

## 7.5 Package options

### Goal

Model commercial offers and the inventory they consume.

### Current capabilities

- Each form supports multiple package options.
- Package options include:
  - label
  - amount
  - default quantity
  - currency
  - sort order
  - active/inactive state
- Package options can be created, listed, and updated.
- Package options now support inventory components.
- Each package option can be mapped to one or more component products with quantities.
- The UI exposes an "Inventory components" editor for package options.

### Operational meaning

The commercial package shown to the customer can differ from the underlying inventory products that are decremented on delivery.

## 7.6 Public order intake

### Goal

Convert landing page traffic into operational orders with no manual re-entry.

### Current capabilities

- Public hosted forms are accessible without auth.
- Internal staff can now create manual orders from the orders page using the same package-selection model as form-submitted orders.
- Customers submit:
  - full name
  - phone
  - optional WhatsApp phone
  - state
  - address
  - package option
- Phone numbers are normalized.
- Contacts are upserted by org + normalized phone.
- Orders are created from submissions.
- Order items are created for the selected package option.
- Order events are written on creation.
- The order gets a sequential number per product.
- A WhatsApp-friendly copy text representation is generated and stored.
- Round-robin assignment runs at creation time if eligible staff exist.
- In-app notifications are created for assigned staff users.
- Outbox events are created for assignment notifications.

### Current limitation

- Public submission throttling is still not implemented.

## 7.7 Order queue and queue management

### Goal

Provide a single operational workspace for the team.

### Current capabilities

- Orders page is the primary console.
- Orders page supports manual order entry in addition to list management.
- Orders page includes mobile control sheets for:
  - filters
  - queue scope
  - product scope
  - manual order creation
- Queue supports:
  - search by customer name, phone, or order number
  - product filtering
  - lead status filtering
  - delivery status filtering
  - remittance status filtering
  - created date range filtering
  - assignment filtering
  - workflow views
- Workflow views currently include:
  - new
  - follow-up
  - confirmed
  - dispatched
  - delivered
  - remitted
- Non-privileged users default to "my orders".
- Privileged users can view all, unassigned, or targeted staff queues.
- The UI includes quick dial and WhatsApp affordances.
- Queue rows can expose copy-ready order text for communication workflows.

## 7.8 Order details and order context

### Goal

Allow operators to fully understand and work an order without leaving the queue.

### Current capabilities

- Order detail drawer shows:
  - order identifiers and timestamps
  - contact snapshot
  - delivery address
  - item list
  - assignment
  - fulfillment partner and partner location
  - statuses and transition controls
  - order event timeline
- The detail interaction is responsive:
  - desktop opens as a right-side drawer
  - mobile opens as a bottom sheet with the same operational controls
- Order events can be queried separately.
- The drawer is integrated with:
  - staff reassignment
  - delivery partner selection
  - linked accounting context

## 7.9 Order workflow gating

### Goal

Enforce the real operational sequence of a POD order.

### Current status model

- Lead: `UNATTENDED`, `UNREACHABLE`, `RESCHEDULED`, `CANCELLED`, `CONFIRMED`
- Delivery: `DISPATCHED`, `RESCHEDULED`, `CANCELLED`, `DELIVERED`
- Remittance: `PENDING`, `REMITTED`

### Current rules

- Orders start with `lead_status = UNATTENDED`.
- Delivery transitions require `lead_status = CONFIRMED`.
- Remittance transitions require `delivery_status = DELIVERED`.
- Rescheduled transitions require a timestamp.
- Moving lead away from `CONFIRMED` clears later-stage data.
- Moving delivery away from `DELIVERED` clears remittance data.
- Status changes are handled through transition endpoints.
- Transition events are recorded with actor and request metadata.

## 7.10 Assignment and reassignment

### Goal

Balance work fairly while keeping product specialization intact.

### Current capabilities

- New public-form orders use round-robin assignment by product scope.
- Only active staff scoped to the product are eligible.
- Managers/owners/privileged users can reassign or unassign.
- Reassignment records `order.assigned`, `order.reassigned`, or `order.unassigned` events.

### Requirements

- Staff without product access cannot be assigned.
- Inactive staff cannot be assigned.

## 7.11 Fulfillment partner selection on dispatch

### Goal

Tie dispatch and delivery to real external fulfillment capacity.

### Current capabilities

- Dispatching an order now requires:
  - fulfillment partner
  - fulfillment partner location
- Dispatch validation checks partner/location selection and stock sufficiency.
- The selected fulfillment partner and location are stored on the order.
- The order detail UI lets privileged users select eligible partner locations before dispatch.

## 7.12 Inventory

### Goal

Track stock across HQ and external partner locations and connect inventory to fulfillment.

### Current capabilities

#### Partner network

- Create inventory partners.
- Archive/deactivate partners.
- Create partner locations by country and admin area.
- Edit partner locations and display names.
- Query eligible partner locations.

#### Stock operations

- Receive stock into HQ.
- Adjust stock up or down at HQ or partner locations.
- Create stock transfers between HQ and partner locations.
- Confirm transfer receipt.
- Cancel transfers.
- View stock balances by:
  - product
  - location type
  - partner
  - country
  - admin area
- View inventory movements.
- View partner-specific stock and movement perspectives.
- Build partner stock reports in the UI layer.

#### Order integration

- Delivering an order applies inventory decrement at the selected fulfillment location.
- Delivery decrements are stored as inventory movements.
- Order-linked inventory movement records include the related order.

### Supported movement types

- `RECEIVE_HQ`
- `DISPATCH_OUT`
- `RECEIPT_CONFIRM`
- `ORDER_DELIVERED_DECREMENT`
- `ADJUSTMENT_INCREASE`
- `ADJUSTMENT_DECREASE`

### Current product meaning

Inventory is no longer a placeholder module. It is an active system of record for stock position and dispatch flow.

## 7.13 Accounting

### Goal

Track cash reality, not just operational status.

### Current capabilities

#### Setup

- Default accounts are provisioned on first use.
- Default categories are provisioned on first use.
- Users can create and edit accounts.
- Users can create and edit categories.
- Accounts and categories support active/inactive state.

#### Entries

- Users can create manual revenue and expense entries.
- Entries support:
  - account
  - category
  - amount
  - currency
  - entry date
  - notes
  - related order
  - related partner
  - related partner location
- Entries can be filtered by:
  - entry type
  - account
  - category
  - source type
  - date range
  - related order
- Entries can be edited after creation.

#### Overview

- Accounting overview returns:
  - revenue total
  - expense total
  - net total

#### Order integration

- Marking an order as remitted creates an accounting revenue entry for that order if one does not already exist.
- Later remittance transitions do not duplicate the remittance-linked accounting entry.
- Accounting entry creation from remittance is also logged back into order events.
- Remittance-linked accounting entries can be edited without mutating the operational `remittedAmount` on the order.

### Current product meaning

Accounting is not a future concept anymore. It is an active financial tracking surface, even if it is still intentionally lightweight compared to a full ERP.

## 7.14 Notifications

### Goal

Notify staff about assigned work and give them an activity inbox.

### Current capabilities

- In-app notifications are stored and listed.
- Users can:
  - list notifications
  - filter unread
  - mark a single notification read
  - mark all notifications read
- Notifications deep-link back into order workflows.
- Assignment events create outbox records for async processing.

### Current limitation

- Push token registration still exists as an endpoint seam but is not implemented.
- The worker currently processes assignment outbox events, but device push delivery is not yet complete.

## 7.15 Worker and async processing

### Goal

Handle background event processing reliably.

### Current capabilities

- Event outbox table is active.
- Worker claims pending events with concurrency-safe locking.
- Processing states include pending, processing, processed, and failed.
- A stale-processing reaper resets stuck jobs.
- `notification.order_assigned` is actively processed.

## 7.16 Contacts

### Goal

Store enough customer identity to support fulfillment and communication.

### Current capabilities

- Contacts are deduplicated by org and normalized phone.
- Optional WhatsApp phone and display name are stored.
- Orders store contact snapshots at order creation time.

### Product stance

The system remains intentionally light on CRM depth. Contacts support operations first.

## 7.17 Developer and internal tools

### Goal

Help the team validate the full intake loop quickly in development.

### Current capabilities

- A dev-only test submit page allows internal users to:
  - choose a product
  - choose a form
  - choose a package option
  - submit a real public-order payload into the tenant system

## 7.18 UI system and operational ergonomics

### Goal

Keep high-volume operational tasks fast and consistent across modules and breakpoints.

### Current capabilities

- Shared sheet/drawer primitives are used across Orders, Staff, Inventory, Accounting, and Product detail.
- Mobile control sheets follow a common structure:
  - section overlines
  - compact label/control rows
  - consistent clear/apply footers
  - quick date presets where relevant
- Selection-heavy control sheets use consistent active-row treatment and checkmark affordances.
- Inventory and Accounting now follow the same mobile filter/edit sheet rhythm as Orders.
- Staff management now has dedicated mobile controls sheets with matching detail-drawer behavior.

## 8. Core business rules

- All tenant data is org-scoped.
- Orders have sequential numbers per product.
- Public forms are the primary path for order creation.
- Delivery cannot proceed before confirmation.
- Remittance cannot proceed before delivery.
- Dispatch requires partner and partner location.
- Delivered orders can decrement real inventory.
- Remitted orders can create real accounting revenue.
- Staff eligibility depends on active status plus product scope.
- Privileged access is required for staff, inventory, and accounting administration.

## 9. End-to-end workflows

### 9.1 Business setup

1. User signs up or signs in.
2. User can recover access through forgot/reset password flows if needed.
3. User creates an organization if needed.
4. Owner creates products.
5. Owner creates forms and package options.
6. Owner defines package option inventory components.
7. Owner creates staff and product scopes.
8. Owner creates inventory partners and partner locations.
9. Owner begins working orders through the queue.

### 9.2 Public lead to assigned order

1. Customer opens a hosted form.
2. Customer submits order details.
3. System normalizes phone and upserts contact.
4. System creates order and order item.
5. System assigns eligible staff via round-robin when possible.
6. System stores notification and outbox records.
7. Staff sees the order in queue and/or notifications.

### 9.3 Manual order entry

1. Internal staff opens the orders page.
2. Staff launches the manual order flow.
3. Staff selects a product and package option.
4. Staff enters customer and shipping details.
5. System creates the order using the same downstream lifecycle model as a form-submitted order.
6. The order enters the normal queue and detail workflow.

### 9.4 Confirm to dispatch to delivery

1. Staff confirms the lead.
2. Privileged user dispatches the order and selects partner + location.
3. Delivery is later marked delivered.
4. Delivery writes decrement inventory movements tied to the order.

### 9.5 Delivery to remittance to accounting

1. Staff marks the order delivered.
2. Staff records remittance amount.
3. System updates operational remittance fields.
4. System creates or reuses a remittance-linked accounting revenue entry.
5. Order event timeline records both status and accounting-entry creation.

## 10. Current information architecture

### Public

- `/public/forms/[publicKey]`
- `/sign-in`
- `/sign-up`
- `/forgot-password`
- `/reset-password`
- `/invite/[token]`
- `/onboarding/org`

### Authenticated app

- `/orders`
- `/products`
- `/staff`
- `/inventory`
- `/accounting`
- `/notifications`
- `/tools/test-submit` in non-production development flows

## 11. Current success criteria

The product is successful in its current state if teams can:

- stand up a tenant and onboard staff quickly
- receive structured public orders without manual re-entry
- work queues by assignee and stage
- dispatch through known partner locations
- see stock position and stock history
- record revenue/expense entries and remittance-linked revenue
- complete key filter/scope/edit actions on mobile using bottom-sheet controls
- keep all of the above isolated by organization

## 12. Known gaps and non-shipped seams

These are still not fully implemented as of 2026-04-09:

### 12.1 Reconciliation

- remittance reconciliation views
- partner settlement checks
- accounting vs operations mismatch surfaces
- clearer "what changed and why" audit trails beyond basic event logs

### 12.2 Reversals and corrections

- safe reverse-delivered workflow for operator mistakes
- safe reverse-remittance / accounting correction flow
- receipt reversal and compensating inventory moves
- explicit admin-only correction paths

### 12.3 Search and filtering maturity

- global search across orders, partners, transfers, and accounting records
- saved filter views for repeated operational workflows
- stronger source/channel filter model in orders

### 12.4 Reporting and export

- export orders
- export stock by partner/location
- export accounting transactions
- copy/share-ready operational reports

### 12.5 Settings and defaults

- org-wide defaults
- operational preferences
- messaging templates
- workflow defaults

### 12.6 Invite and admin polish

- resend/reissue invite
- revoke invite
- clearer invite lifecycle/status handling for admins

### 12.7 Permissions hardening

- more granular role model
- explicit authority controls for stock adjustments
- explicit authority controls for accounting edits
- explicit authority controls for transfer cancellation

### 12.8 Public form and commercial polish

- better hosted form UX
- better embed UX/tooling
- broader form-management maturity

### 12.9 Existing technical seams still open

- safe non-status order editing
- push token registration / end-user push delivery
- centralized audit service beyond current order events
- public-form rate limiting
- combo explosion into child `order_items` at save time

### 12.10 Suggested sequence (post-dashboard)

1. Reconciliation
2. Reversals and corrections
3. Reporting and export
4. Permissions hardening
5. Invite and admin polish

These are meaningful gaps, but they no longer define the product as "mostly planned." The core order, inventory, and accounting workflows are already active.

## 13. Non-goals for the current product

- Full CRM with deep customer lifecycle features
- Generic e-commerce storefront management
- Full ERP-grade accounting
- Cookie-session-first API architecture
- Free-form order state editing

## 14. Product positioning

EcommOS should currently be positioned as:

- a POD order operations system
- a lightweight operations CRM
- an inventory-aware fulfillment console
- a remittance-aware accounting console for operator-led commerce teams

## 15. Source basis

This PRD reflects the current product state derived from:

- web app routes and UI flows
- API routes
- core business logic
- database schema
- worker/outbox behavior
- explicit remaining `NotImplemented` seams
