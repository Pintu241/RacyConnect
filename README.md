# RecyConnect – Connecting Collectors, Empowering Recycling

> *"Connecting Collectors. Empowering Recycling. Building a Greener Future."*

**RecyConnect** is an enterprise-grade, responsive Django web application designed to organize the informal scrap collection sector, simplify doorstep scrap scheduling for households and commercial businesses, introduce transparent digital weighing and price indices, and bridge community collectors directly with industrial recycling corporations.

---

## 🌟 Key Platform Features

### 1. Multi-Role Ecosystem & Custom Authentication
- **Customer (Household / Business):**
  - Instant Scrap Value Estimator with live pricing.
  - Doorstep scrap collection booking with estimated weight, date/time slot, and photo upload.
  - Real-time status tracking timeline (Pending &rarr; Assigned &rarr; Out for Pickup &rarr; Completed & Paid).
  - Ability to cancel requests before pickup dispatch.
  - Digital weighing receipts with environmental diversion impact.
- **Scrap Collector:**
  - Verified collector profile with service areas, vehicle types (Electric Loader, Rickshaw, Mini Truck), and ID verification.
  - Open Pickup Marketplace: Browse nearby unassigned leads and accept them with 1 click.
  - "Out for Pickup" transit status updates.
  - Digital Weighing & Settlement: Records verified actual scrap weight and agreed price per kilogram, automatically calculating `Total Amount = actual_weight * agreed_rate_per_kg`.
  - Transaction generation with cash or instant UPI settlement.
- **Recycling Company (Industrial Recycler):**
  - Aggregated Recyclables Marketplace: Live inventory tracking of collected scrap volumes ready for bulk processing.
  - Bulk Purchase Order placement with custom procurement rates, moisture thresholds, and facility unloading addresses.
  - Extended Producer Responsibility (EPR) traceability documentation.
- **Platform Administrator:**
  - Executive KPI analytics: total recycled volume (kg), turnover, active users, collector count.
  - **Chart.js** visualizations: Category breakdown doughnut chart and monthly recycled volume/turnover trends.
  - Collector Verification Queue: Inspect collector IDs and verify collectors with 1 click.
  - System-wide pickup monitoring and dispute/complaint investigation desk.
  - Scrap category and live indicative price CRUD management.

---

## 🛠 Technology Stack

- **Backend:** Python 3 & Django 6 (Server-rendered MVC)
- **Frontend:** Django Templates, HTML5, CSS3, JavaScript (ES6)
- **UI Framework:** Bootstrap 5.3 + Bootstrap Icons
- **Data Visualizations:** Chart.js 4.4
- **Database:** SQLite (default development configuration; seamlessly configurable to PostgreSQL via Django settings)
- **Authentication:** Django Built-in Authentication with custom User model (`accounts.User`) and role decorators
- **Image Processing:** Pillow

---

## 📂 Project Architecture
