
## 1. Target user & use-case

1. **Who is this for right now?**
    - 1 team with Mid-size ops (20–100 staff)
        
2. **Primary daily action**
    - Order intake: Support is required for Manual input. They currently take in orders via a webhook link attached to form on their Landing pages forms. I'm supposed to support Manual order input and I would prefer that this app provides HTML snippets for embedding forms on landing pages. That way we can ensure that the data shape is defined in the app rather than a situation where we can't be sure what shape of data is coming in via webhook. Manual order input must still be supported
        
    - Order fulfillment: Orders have status which the staff can update.
      - `Lead status` being the first status the staff attends to. Examples of lead status are: "Cancelled, Confirmed (ready to receive delivery), Rescheduled (opens a date picker to choose rescheduled date), Unreachable (to reach again)"
      - Confirmed orders are eligible to have a `Delivery status` field where staff can edit the `delivery status` to any of: "Dispatched, Delivered, Cancelled, Rescheduled (rescheduled date)"
      - Delivered orders are eligible to have a `Remittance status` field where staff can edit the `remittance status` to any of: "Remitted, pending". A remitted order would have a value field that is prefilled with the value of a unit of the product, but the field can be edited in case the staff had to give a discount to the customer.
     
    - Customer follow-ups: See Order fulfillment above to understand the status of followups. Note that they would call the customer's phone numbers and/or WhatsApp them. 
        
    - Inventory tracking: See Order Fulfilment for `delivery status` For orders where `delivery status` is "Delivered", there should be a decrement of stock. INventory. tracking
        
    - Analytics / oversight: analytics should center on order volume and delivery rate
      
      (ADDED SECTION: ORDERS)
- Order ID should be sequential and generated on save. e.g. Order #007 (is the seventh order in the system). 
- A copy button that captures a neatly formatted text representation of the order should be available so that the staff can post the order on the whatsapp group where logistics partners receive it for action.
        
3. **Is this closer to:**
    - Shopify admin replacement?
    - WhatsApp-commerce back office?
    - Internal ops dashboard for brands?
I'm not familiar with any of the three solutions above. But this market is unique in that it's not one where much automation in in use amongst the market. And so there's a mix of manual inputs and automation. So internal ops I guess as it spans orders+products, acconutings + finance, staff, and inventory

---

## 2. Order sources (very important)

4. **How do orders enter the system initially?**
    
    - Manual entry by staff: make this available 
    - Landing page / checkout form: yes and primary
    - WhatsApp import (copy/paste or API later): copy/paste. how would API work? I'm interested
    - Instagram DM: yes
    - CSV upload: yes
        
5. **Do orders always belong to a customer?**
    THis app is not a modern CRM in the sense of being customer-centric. We do not save customer profiles at all. Especially because the customers are random people buying from seeing ads
        
6. **Do you expect order drafts?**
    - Yes, save order drafts to resume editing.



---

## 3. Customer model depth

7. **What makes a “customer” valuable to you?**    
    - Contactability (WhatsApp / phone)      
See 2.5; a customer is not valuable in the traditional sense. We only need their contact details as seen on an order. Beyond that, we may need to send SMS or Ad campaigns to customers that have certain criteria. So in that sense yes they're valuable
        
8. **Do you want:**
    
    - One customer can have multiple numbers. The order forms typically have phone number and WhatsApp number fields 
        
9. **Will staff add internal notes about customers?**
    
    - Yes
        

---

## 4. Products & inventory

10. **Inventory tracking**
I've created an inventory management app fro this business before and htis is what I implemented:
	#### Core Features
- Authentication with email/password and Google OAuth, plus password reset.
- Tenant-aware access with role-based permissions and membership management.
- Team onboarding with invites and member role control.
- Product catalog management
- Locations and partner locations for routing, availability, and service coverage.
- Stock operations for receiving, dispatching, and confirming deliveries.
- Sales tracking to tie stock movement to revenue and reconcile inventory.
- Dashboard endpoints for operational overview and quick visibility.

#### Dispatch and Receipt Flows
ECT Inventory treats stock movement as a two-step operational flow, ensuring every outbound transfer is traceable and every inbound delivery is confirmed before stock is credited.
##### Dispatch Flow
- Dispatch starts from a source location for a specific product and quantity.
- The system records an outbound movement to establish a clear audit trail.
- Dispatch is routed to a partner location, keeping the originating location’s balance accurate.
- Dispatch entries remain pending until confirmation is received from the destination.
##### Confirm Receipt Flow
- Receipt confirmation is submitted against a pending dispatch.
- The destination partner location’s stock is credited only after confirmation.
- The original dispatch record is updated to a received/confirmed state.
- This flow prevents double-counting and ensures inventory integrity across locations.
#### Partner Coverage and Distribution
- Partners can serve multiple states and regions, enabling wide distribution without duplicating partners per territory.
- Partner locations represent the physical drop-off or pickup points tied to a partner.
- A single partner can manage multiple partner locations across different states, with stock movements tracked per location.
    

11. **Pricing**
- Fixed price but manual value override per order item
    
12. **Is SKU important or optional?**
    SKUs are not needed for this usecase. Rather the products have unique names which can then have short codes. but we won't support non-human friendly paradigms like SKUs

(ADDED SECTION: PRODUCT MANAGEMENT)
- Multiple products can be sold by same org. So need to be able to create  products
- Also  they sell "combos" which are combinations of products into a package. Imagine they have Herbal Oil and Slim Tea. They can create a product combo like this: 
	- 1 S-OIL (1 Herbal Oil & 1 Slim tea) - NGN 10,000
	- 1 S-OIL (1 Herbal Oil & 2 Slim tea) - NGN 25,000
- This means that in the order form the staff works with, they should be able to edit the number of products in the combo that actually got ordered. this is because during the call between the staff and the customer, the customer might opt for 2 "herbal oils" and discard the "slim tea"
- This dynamism should reflect in inventory management as well. when this order is marked "delivered" it should be the overriden value that gets posted to the inventory records.
---

## 5. Team & permissions (future pain point)

13. **Roles you already know you need**
    

- Owner
- Manager: 
- Staff
- Custom roles (plan for this): sensitive parts of the app like Accounting should be scoped to finance manager. That is managers can yet be given scopes. Accounting manager should not be able to edit/add staff for instance.
    

14. **Should staff see all orders or only assigned ones?**
    Only assigned ones. The system auto assigns to the staff in a round-robin fashion .
15. **Do actions need accountability?**  

- Yes (activity log is critical)

(ADDED SECTION: STAFF MANAGEMENT)
- Owner and staff managers should be able to invite staff to the organisation. See the staff's analytics, like confirmed/delivery rates, volume processed over filterable time
- Staff can be removed from this dashboard as well
- Staff analytics, very important (Staff's Total Order, staff's Total Confirmed Orders, Staff's Total Delivered Orders, Staff's Delivery Rate, Number of Upsells for staff)
- Basic HR: Salary amount per staff, probation status, etc. 

---

## 6. Payments & fulfillment (now vs later)

16. **Payments**
  Answer: payments are manually updated by the accounting staff. They first have the `remittance status` field which they can toggle to "Remitted" based on the team's communication with the logistics partners who are the ones that remit the earnings to the business. Remember that the main model is pay-on-delivery

17. **Delivery**
- Simple status only (pending / delivered)
- Rider assignment later
- No delivery logic at all
    See my extensive notes in "Order fulfilment" for this. Note that the interaction with the logistics partner is offline and the staff of the org would, based on feedback from the logistics partner, update the delivery status of the order

(ADDED SECTION: ACCOUNTING)
- App needs revenue and accounting management. Confirmed Remittances should reflect as revenue.
- Expenses can be logged per expense category. Categories can be created dynamically.
- Virtual accounts (e.g. capital reserve, operations account, procurement account) can be created with their own income/expense history.
- For every order that the logistics partner delivers, the accountant would get an informal report from the logistics partner stating what the delivery fee was for "Order #234" for example. Accountant can select from delivery agent and state of delivery when logging this delivery related expense.

---

## 7. Multi-business & scale

18. **One user managing multiple businesses?**
- Yes it should be possible for a user to create another entirely separate org

18. **Is this Nigeria-first?**
- Yes (WhatsApp-first, NGN, Paystack assumptions)
    This is Nigeria first, yes.

18. **Data isolation requirement**
- Strict (no cross-org leakage ever)

---

## 8. Product philosophy (guides API design)

21. **Is this:**
- Opinionated (your way of doing commerce)
   Highly opinionated and tailored to the pay-on-delivery, ecommerce model that's dominant in Nigeria. Where the staff aren't also as tech-savvy. 

22. **Do you prefer:**

- Fewer powerful primitives
- Many explicit features
 A mix honestly
    

23. **Do you want this to become a platform (integrations, webhooks)?**
- Later

## 9. Tech preferences (so I don’t fight you)

24. Backend stack preference?
- Node. What do you think about using NextJS server actions and deploying on Vercel? 

25. Database?
- Postgres with Drizzle
    

26. Auth expectations?
- Email + password
- Magic link

## 10. Notifications
- We need to notify staff of orders as they come in assigned to them.