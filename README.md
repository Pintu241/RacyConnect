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

```
recyconnect/
│
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
│
├── config/                  # Django project root settings & router
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                # User registration, profiles, roles, decorators
│   ├── models.py            # User, CollectorProfile, RecyclerProfile
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── decorators.py        # Role-based access control decorators
│
├── scrap/                   # Scrap categories, indicative rates, price history
│   ├── models.py            # ScrapCategory
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── pickups/                 # Pickup scheduling, status lifecycle, assignments
│   ├── models.py            # PickupRequest
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── transactions/            # Verified weights, rates, totals, digital receipts
│   ├── models.py            # Transaction
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── recyclers/               # Recycler bulk marketplace & purchase orders
│   ├── models.py            # PurchaseRequest
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── dashboard/               # Role-specific dashboards & Chart.js analytics
│   ├── views.py             # Customer, Collector, Recycler, Admin views
│   └── urls.py
│
├── core/                    # Homepage, About, How-it-Works, Contact, Complaints
│   ├── models.py            # Complaint, ContactMessage
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── context_processors.py
│   ├── tests.py             # Full workflow integration & unit tests
│   └── management/commands/
│       └── seed_data.py     # Realistic demonstration seed script
│
├── static/
│   ├── css/styles.css       # Custom sustainability theme & responsive layout
│   └── js/main.js           # Live calculators & UI helpers
│
├── templates/               # Django server-rendered templates
│   ├── base.html
│   ├── core/
│   ├── accounts/
│   ├── scrap/
│   ├── pickups/
│   ├── transactions/
│   ├── recyclers/
│   └── dashboard/
│
└── media/                   # Uploaded scrap images & profile documentation
```

---

## ⚡ Quick Start & Installation

### 1. Clone & Setup Virtual Environment
```bash
# Clone the repository
git clone <repository_url>
cd RecyConnect

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Apply Migrations & Seed Demo Data
```bash
# Run database migrations
python manage.py migrate

# Seed realistic scrap categories, users, pickups, and orders
python manage.py seed_data
```

### 3. Run the Development Server
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Demo Accounts & Credentials

The seed script creates ready-to-test accounts for every role. You can also use the **Quick Demo Switcher** in the top navigation bar to switch between roles with 1 click:

| Role | Username | Password | Persona / Details |
|------|----------|----------|-------------------|
| **Platform Administrator** | `admin` | `admin123` | Platform Admin with access to analytics & verification queue |
| **Customer (Household)** | `customer1` | `pass123` | Rahul Sharma (Green Valley Apartments) |
| **Customer (Commercial)** | `business1` | `pass123` | Nexus Tech Hub (Office IT equipment & scrap) |
| **Scrap Collector (Verified)** | `collector1` | `pass123` | Mohan Lal (Electric Loader, 4.9★ rating) |
| **Scrap Collector (Pending)** | `collector2` | `pass123` | Ramesh Kumar (Awaiting admin verification) |
| **Industrial Recycler** | `recycler1` | `pass123` | EcoGreen Reclaim & Smelting Ltd. |

---

## 🧪 Running Automated Tests

Run the comprehensive test suite verifying calculations, permissions, workflows, and endpoints:

```bash
python manage.py test
```

Expected result:
```
Ran 6 tests in ~20s
OK
```

---

## 🔒 Security & Validation Details

- **Calculation Integrity:** Total amounts (`total_amount = actual_weight * agreed_rate_per_kg`) and bulk order values are strictly calculated and validated on the server.
- **CSRF Protection:** Django CSRF tokens on all POST requests.
- **Role-Based Access Control:** Reusable decorators (`@customer_required`, `@collector_required`, `@recycler_required`, `@admin_required`) enforce permission boundaries across views.
- **Ownership Validation:** Customers can only view and cancel their own requests; collectors can only complete pickups assigned to them.
- **Auditability:** Every completed collection automatically generates an unalterable `Transaction` model record linking customer, collector, pickup reference, weighing data, and payment status.
