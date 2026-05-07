# Project: Invoice App

## REQ-001: Create Invoice
The system shall allow users to create invoices with line items.

### AC-001: Invoice contains recipient, date, and line items
### AC-002: Line items have description, quantity, unit price, and total
### AC-003: Invoice auto-calculates subtotal and grand total

## REQ-002: Send Invoice by Email
The system shall send invoices as PDF attachments via email.

### AC-004: Email contains invoice PDF attachment
### AC-005: Email is sent to the recipient email address

## Tasks
- [x] Design database schema for invoices and line items
- [x] Create Invoice model and migration
- [ ] Create InvoiceCreate endpoint
- [ ] Create InvoiceSend email job
- [ ] Create PDF generation service
- [ ] Add email template for invoice

## REQ-003: Invoice Dashboard
The system shall display an invoice list with status filters.

### AC-006: Dashboard shows sent, paid, overdue invoices
### AC-007: Dashboard supports date range filtering

## Tasks (continued)
- [ ] Create invoice dashboard endpoint
- [ ] Create invoice dashboard Vue component

## Out of Scope: Payment processing integration
- [ ] Payment gateway will be added in v2

## MISSING: Invoice approval workflow not yet defined
