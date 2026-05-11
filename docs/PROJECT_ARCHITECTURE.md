# 🚀 AIOSOL - Facebook Auto-Reply SaaS Platform

## Enterprise Architecture Document
**Version:** 1.0.0
**Created:** May 2026
**Team:** AIOSOL Development Team

---

## 📋 Table of Contents
1. [Executive Summary](#executive-summary)
2. [Team Structure](#team-structure)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Database Design](#database-design)
6. [API Architecture](#api-architecture)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)
9. [Pricing & Billing](#pricing--billing)
10. [Development Phases](#development-phases)

---

## 🎯 Executive Summary

### Product Vision
AIOSOL হলো একটি AI-powered Facebook Comment Auto-Reply SaaS platform যা businesses কে তাদের Facebook Page এর comments এ intelligent, diplomatic এবং context-aware responses দিতে সাহায্য করে।

### Key Value Propositions
- ⚡ **Instant Response**: Comments এ seconds এ reply
- 🧠 **AI-Powered**: GPT-4/Claude দিয়ে intelligent replies
- 🎯 **Diplomatic Tone**: Professional, brand-aligned responses
- 📊 **Analytics**: Reply performance tracking
- 🏢 **Multi-tenant**: 1000+ organizations support ready
- 🔒 **Enterprise Security**: SOC2 compliant architecture

### Target Users
- E-commerce businesses
- Digital marketing agencies
- Social media managers
- Small to large enterprises

---

## 👥 Team Structure

### Core Team Agents

| Agent | Role | Expertise |
|-------|------|-----------|
| **🧠 Rafiq** | Project Architect | System design, Scalability, DB architecture |
| **⚙️ Sadia** | Backend Lead | FastAPI, PostgreSQL, Facebook API, Webhooks |
| **🎨 Karim** | Frontend Lead | React 18, TypeScript, Tailwind, Dashboard UI |
| **🚀 Nila** | DevOps Engineer | Docker, Nginx, CI/CD, SSL, Monitoring |
| **🤖 Tanvir** | AI Engineer | OpenAI API, Claude API, Prompt Engineering |
| **🧪 Priya** | QA Lead | Testing, Security Audit, Performance Testing |

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AIOSOL PLATFORM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │   Facebook  │────▶│   Webhook   │────▶│   Queue     │────▶│    AI     │ │
│  │   Graph API │     │   Handler   │     │   (Redis)   │     │   Engine  │ │
│  └─────────────┘     └─────────────┘     └─────────────┘     └───────────┘ │
│         ▲                   │                   │                   │       │
│         │                   ▼                   ▼                   ▼       │
│         │            ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│         └────────────│   FastAPI   │────▶│  PostgreSQL │     │  OpenAI/  │ │
│                      │   Backend   │     │   Database  │     │  Claude   │ │
│                      └─────────────┘     └─────────────┘     └───────────┘ │
│                             ▲                                               │
│                             │                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      React Frontend (Dashboard)                      │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────┐  │   │
│  │  │  Auth   │  │  Pages  │  │ Replies │  │Analytics│  │  Billing  │  │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └───────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User comments on Facebook Page
         ↓
2. Facebook sends webhook to our server
         ↓
3. Webhook handler validates & queues the comment
         ↓
4. Background worker picks up from Redis queue
         ↓
5. AI Engine generates diplomatic reply
         ↓
6. Reply posted back to Facebook via Graph API
         ↓
7. Analytics updated in PostgreSQL
         ↓
8. User sees reply stats in Dashboard
```

---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI Framework |
| TypeScript | 5.x | Type Safety |
| Vite | 5.x | Build Tool |
| Tailwind CSS | 3.x | Styling |
| React Query | 5.x | Data Fetching |
| React Router | 6.x | Routing |
| Zustand | 4.x | State Management |
| React Hook Form | 7.x | Form Handling |
| Recharts | 2.x | Analytics Charts |
| Lucide React | - | Icons |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.110+ | API Framework |
| SQLAlchemy | 2.x | ORM |
| Alembic | 1.x | Migrations |
| PostgreSQL | 15+ | Database |
| Redis | 7.x | Queue & Cache |
| Celery | 5.x | Background Jobs |
| Pydantic | 2.x | Validation |
| python-jose | - | JWT |
| passlib | - | Password Hashing |
| httpx | - | HTTP Client |

### External APIs
| Service | Purpose |
|---------|---------|
| Facebook Graph API | Comments, Pages, Webhooks |
| OpenAI API | GPT-4 for AI replies |
| Claude API | Alternative AI (backup) |
| Razorpay | Payment Gateway (India) |
| Stripe | Payment Gateway (Global) |
| SendGrid/Resend | Email Service |

### DevOps
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Local Development |
| Nginx | Reverse Proxy |
| Ubuntu 22.04 | Server OS |
| Let's Encrypt | SSL Certificates |
| GitHub Actions | CI/CD |
| Sentry | Error Monitoring |
| Prometheus + Grafana | Metrics |

---

## 🗄️ Database Design

### Entity Relationship Diagram

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   organizations  │     │      users       │     │   subscriptions  │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ id (PK)          │◀───┤│ organization_id  │     │ id (PK)          │
│ name             │     │ id (PK)          │     │ organization_id  │──▶
│ slug             │     │ email            │     │ plan_id          │──▶
│ settings (JSON)  │     │ password_hash    │     │ status           │
│ created_at       │     │ role             │     │ current_period   │
│ updated_at       │     │ is_active        │     │ razorpay_sub_id  │
└──────────────────┘     │ created_at       │     │ stripe_sub_id    │
         │               └──────────────────┘     └──────────────────┘
         │                                                 │
         ▼                                                 ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  facebook_pages  │     │    comments      │     │      plans       │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ id (PK)          │     │ id (PK)          │     │ id (PK)          │
│ organization_id  │──▶  │ page_id          │──▶  │ name             │
│ fb_page_id       │     │ fb_comment_id    │     │ price_monthly    │
│ page_name        │     │ fb_post_id       │     │ price_yearly     │
│ access_token     │     │ commenter_name   │     │ max_pages        │
│ is_active        │     │ comment_text     │     │ max_replies      │
│ settings (JSON)  │     │ reply_text       │     │ features (JSON)  │
│ created_at       │     │ reply_status     │     │ is_active        │
└──────────────────┘     │ replied_at       │     └──────────────────┘
                         │ ai_model_used    │
                         │ tokens_used      │
                         │ created_at       │
                         └──────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   reply_rules    │     │   ai_prompts     │     │   usage_logs     │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ id (PK)          │     │ id (PK)          │     │ id (PK)          │
│ organization_id  │──▶  │ organization_id  │──▶  │ organization_id  │──▶
│ page_id          │──▶  │ name             │     │ action_type      │
│ rule_type        │     │ system_prompt    │     │ tokens_used      │
│ keywords         │     │ tone             │     │ cost             │
│ action           │     │ language         │     │ created_at       │
│ reply_template   │     │ is_default       │     └──────────────────┘
│ is_active        │     │ created_at       │
│ priority         │     └──────────────────┘
└──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│  webhook_logs    │     │   audit_logs     │
├──────────────────┤     ├──────────────────┤
│ id (PK)          │     │ id (PK)          │
│ organization_id  │──▶  │ organization_id  │──▶
│ event_type       │     │ user_id          │──▶
│ payload (JSON)   │     │ action           │
│ status           │     │ entity_type      │
│ error_message    │     │ entity_id        │
│ processed_at     │     │ old_values       │
│ created_at       │     │ new_values       │
└──────────────────┘     │ ip_address       │
                         │ created_at       │
                         └──────────────────┘
```

### Key Tables Description

#### 1. organizations (Multi-tenant Core)
```sql
- id: UUID PRIMARY KEY
- name: Organization name
- slug: URL-friendly unique identifier
- settings: JSONB for flexible configuration
  {
    "timezone": "Asia/Kolkata",
    "language": "bn",
    "reply_delay_min": 30,
    "reply_delay_max": 120,
    "working_hours": {"start": "09:00", "end": "21:00"},
    "auto_reply_enabled": true
  }
```

#### 2. facebook_pages (Connected Pages)
```sql
- fb_page_id: Facebook's page ID
- access_token: Encrypted long-lived token
- settings: Page-specific AI settings
  {
    "tone": "professional",
    "language": "bengali",
    "custom_prompt": "...",
    "excluded_keywords": ["spam", "hate"]
  }
```

#### 3. comments (Reply History)
```sql
- reply_status: ENUM('pending', 'processing', 'replied', 'failed', 'skipped')
- ai_model_used: 'gpt-4', 'claude-3', etc.
- tokens_used: For billing calculation
```

---

## 🔌 API Architecture

### API Versioning
All APIs prefixed with `/api/v1/`

### Authentication Endpoints
```
POST   /api/v1/auth/register          # New user registration
POST   /api/v1/auth/login             # Login, returns JWT
POST   /api/v1/auth/refresh           # Refresh access token
POST   /api/v1/auth/logout            # Invalidate token
POST   /api/v1/auth/forgot-password   # Request password reset
POST   /api/v1/auth/reset-password    # Reset with token
GET    /api/v1/auth/me                # Current user profile
```

### Organization Endpoints
```
GET    /api/v1/organizations          # List user's organizations
POST   /api/v1/organizations          # Create organization
GET    /api/v1/organizations/:id      # Get organization details
PATCH  /api/v1/organizations/:id      # Update organization
DELETE /api/v1/organizations/:id      # Delete organization
```

### Facebook Integration Endpoints
```
GET    /api/v1/facebook/auth-url      # Get FB OAuth URL
GET    /api/v1/facebook/callback      # OAuth callback
GET    /api/v1/pages                  # List connected pages
POST   /api/v1/pages/:id/connect      # Connect a page
DELETE /api/v1/pages/:id              # Disconnect page
PATCH  /api/v1/pages/:id/settings     # Update page settings
GET    /api/v1/pages/:id/comments     # List comments
GET    /api/v1/pages/:id/analytics    # Page analytics
```

### AI & Reply Endpoints
```
GET    /api/v1/prompts                # List AI prompts
POST   /api/v1/prompts                # Create custom prompt
PATCH  /api/v1/prompts/:id            # Update prompt
DELETE /api/v1/prompts/:id            # Delete prompt
POST   /api/v1/prompts/test           # Test prompt with sample

GET    /api/v1/rules                  # List reply rules
POST   /api/v1/rules                  # Create rule
PATCH  /api/v1/rules/:id              # Update rule
DELETE /api/v1/rules/:id              # Delete rule
```

### Billing Endpoints
```
GET    /api/v1/plans                  # List available plans
GET    /api/v1/subscription           # Current subscription
POST   /api/v1/subscription/checkout  # Create checkout session
POST   /api/v1/subscription/cancel    # Cancel subscription
GET    /api/v1/invoices               # List invoices
GET    /api/v1/usage                  # Current usage stats
```

### Webhook Endpoints
```
POST   /api/v1/webhooks/facebook      # Facebook webhook receiver
GET    /api/v1/webhooks/facebook      # Webhook verification
POST   /api/v1/webhooks/razorpay      # Razorpay webhook
POST   /api/v1/webhooks/stripe        # Stripe webhook
```

### Admin Endpoints (Super Admin Only)
```
GET    /api/v1/admin/organizations    # All organizations
GET    /api/v1/admin/users            # All users
GET    /api/v1/admin/stats            # Platform stats
GET    /api/v1/admin/revenue          # Revenue dashboard
PATCH  /api/v1/admin/plans/:id        # Modify plans
```

---

## 🔒 Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: HTTPS/TLS 1.3                                     │
│  ├── All traffic encrypted                                  │
│  └── HSTS enabled                                           │
│                                                             │
│  Layer 2: Rate Limiting                                     │
│  ├── 100 requests/minute per IP                             │
│  ├── 1000 requests/hour per user                            │
│  └── Webhook: 10000/minute (Facebook)                       │
│                                                             │
│  Layer 3: JWT Authentication                                │
│  ├── Access Token: 15 minutes                               │
│  ├── Refresh Token: 7 days                                  │
│  └── Token rotation on refresh                              │
│                                                             │
│  Layer 4: Role-Based Access Control (RBAC)                  │
│  ├── super_admin: Full platform access                      │
│  ├── org_owner: Full org access                             │
│  ├── org_admin: Manage org settings                         │
│  ├── org_member: View & reply                               │
│  └── org_viewer: View only                                  │
│                                                             │
│  Layer 5: Multi-tenant Isolation                            │
│  ├── All queries filtered by organization_id                │
│  ├── Row-level security in PostgreSQL                       │
│  └── Tenant context middleware                              │
│                                                             │
│  Layer 6: Data Encryption                                   │
│  ├── Passwords: bcrypt (12 rounds)                          │
│  ├── Tokens: AES-256 encryption at rest                     │
│  └── PII: Encrypted columns                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Security Headers
```python
# All responses include:
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### Input Validation
- All inputs validated with Pydantic
- SQL injection prevention via ORM
- XSS prevention via output encoding
- CSRF tokens for state-changing operations

---

## 🚀 Deployment Architecture

### Production Setup

```
                        ┌─────────────────┐
                        │   CloudFlare    │
                        │   (CDN + WAF)   │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │     Nginx       │
                        │ (Reverse Proxy) │
                        │   Port 443      │
                        └────────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
     ┌────────▼────────┐ ┌──────▼──────┐ ┌────────▼────────┐
     │  Frontend       │ │   Backend   │ │   Webhook       │
     │  (Static)       │ │   FastAPI   │ │   Handler       │
     │  /var/www/html  │ │   :8000     │ │   :8001         │
     └─────────────────┘ └──────┬──────┘ └────────┬────────┘
                                │                  │
                       ┌────────▼──────────────────▼────────┐
                       │              Redis                  │
                       │         (Queue + Cache)             │
                       │            :6379                    │
                       └────────────────┬───────────────────┘
                                        │
                       ┌────────────────▼───────────────────┐
                       │           PostgreSQL               │
                       │              :5432                 │
                       └────────────────────────────────────┘

     ┌─────────────────────────────────────────────────────┐
     │                   Celery Workers                    │
     │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
     │  │Worker 1 │  │Worker 2 │  │Worker 3 │  (Auto-scale)│
     │  └─────────┘  └─────────┘  └─────────┘             │
     └─────────────────────────────────────────────────────┘
```

### Server Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Storage | 50 GB SSD | 100 GB SSD |
| Bandwidth | 1 TB/month | Unlimited |

### Scaling Strategy
```
Phase 1 (0-100 orgs):     Single VPS
Phase 2 (100-500 orgs):   VPS + Managed DB
Phase 3 (500-2000 orgs):  Multiple VPS + Load Balancer
Phase 4 (2000+ orgs):     Kubernetes cluster
```

---

## 💳 Pricing & Billing

### Plans Structure

| Plan | Monthly | Yearly | Pages | Replies/mo | Features |
|------|---------|--------|-------|------------|----------|
| **Free** | ₹0 | ₹0 | 1 | 100 | Basic AI, Email support |
| **Starter** | ₹499 | ₹4,990 | 3 | 1,000 | Custom prompts, Priority support |
| **Pro** | ₹1,499 | ₹14,990 | 10 | 5,000 | Analytics, API access, Rules |
| **Business** | ₹4,999 | ₹49,990 | 25 | 20,000 | White-label, Dedicated support |
| **Enterprise** | Custom | Custom | Unlimited | Unlimited | SLA, Custom AI, On-premise |

### Revenue Projections

```
Year 1 Target:
├── Free users: 1000
├── Starter: 200 × ₹499 = ₹99,800/mo
├── Pro: 50 × ₹1,499 = ₹74,950/mo
├── Business: 10 × ₹4,999 = ₹49,990/mo
└── Total MRR: ₹2,24,740 (~$2,700)
    Total ARR: ₹26,96,880 (~$32,400)
```

---

## 📅 Development Phases

### Phase 1: Foundation (Week 1-2)
**Lead: Rafiq (Architect) + Sadia (Backend)**
```
□ Project setup (monorepo structure)
□ Database schema implementation
□ FastAPI base structure
□ JWT authentication system
□ Multi-tenant middleware
□ Basic CRUD operations
□ Alembic migrations setup
```

### Phase 2: Facebook Integration (Week 3-4)
**Lead: Sadia (Backend) + Tanvir (AI)**
```
□ Facebook App creation guide
□ OAuth implementation
□ Page connection flow
□ Webhook setup
□ Comment fetching
□ Reply posting
□ Token refresh mechanism
```

### Phase 3: AI Engine (Week 4-5)
**Lead: Tanvir (AI Engineer)**
```
□ OpenAI integration
□ Claude integration (backup)
□ Prompt engineering
□ Context-aware replies
□ Sentiment analysis
□ Language detection
□ Reply rules engine
```

### Phase 4: Frontend Dashboard (Week 5-7)
**Lead: Karim (Frontend)**
```
□ React project setup
□ Authentication pages
□ Dashboard layout
□ Page management UI
□ Comment/Reply viewer
□ Analytics charts
□ Settings pages
□ Billing UI
```

### Phase 5: Billing System (Week 7-8)
**Lead: Sadia (Backend)**
```
□ Razorpay integration
□ Stripe integration
□ Subscription management
□ Usage tracking
□ Invoice generation
□ Webhook handlers
```

### Phase 6: DevOps & Launch (Week 8-9)
**Lead: Nila (DevOps)**
```
□ Docker configuration
□ CI/CD pipeline
□ Nginx setup
□ SSL configuration
□ Monitoring setup
□ Backup automation
□ Documentation
```

### Phase 7: Testing & Polish (Week 9-10)
**Lead: Priya (QA)**
```
□ Unit tests
□ Integration tests
□ Security audit
□ Performance testing
□ Load testing
□ Bug fixes
□ Launch preparation
```

---

## 📁 Project Structure

```
aiosol/
├── docs/                          # Documentation
│   ├── PROJECT_ARCHITECTURE.md
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── FACEBOOK_SETUP_GUIDE.md
│
├── backend/                       # FastAPI Backend
│   ├── alembic/                   # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app entry
│   │   ├── config.py             # Settings & config
│   │   ├── database.py           # DB connection
│   │   │
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── organization.py
│   │   │   ├── user.py
│   │   │   ├── facebook_page.py
│   │   │   ├── comment.py
│   │   │   ├── subscription.py
│   │   │   ├── plan.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── schemas/              # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── organization.py
│   │   │   ├── user.py
│   │   │   ├── facebook.py
│   │   │   ├── comment.py
│   │   │   └── billing.py
│   │   │
│   │   ├── api/                  # API routes
│   │   │   ├── __init__.py
│   │   │   ├── deps.py           # Dependencies
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py
│   │   │       ├── auth.py
│   │   │       ├── organizations.py
│   │   │       ├── users.py
│   │   │       ├── pages.py
│   │   │       ├── comments.py
│   │   │       ├── prompts.py
│   │   │       ├── rules.py
│   │   │       ├── billing.py
│   │   │       ├── webhooks.py
│   │   │       └── admin.py
│   │   │
│   │   ├── services/             # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── facebook_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── reply_service.py
│   │   │   ├── billing_service.py
│   │   │   └── analytics_service.py
│   │   │
│   │   ├── core/                 # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py       # JWT, hashing
│   │   │   ├── permissions.py    # RBAC
│   │   │   ├── exceptions.py     # Custom exceptions
│   │   │   └── middleware.py     # Tenant middleware
│   │   │
│   │   └── workers/              # Celery tasks
│   │       ├── __init__.py
│   │       ├── celery_app.py
│   │       ├── comment_processor.py
│   │       └── token_refresher.py
│   │
│   ├── tests/                    # Backend tests
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_facebook.py
│   │   └── test_billing.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                      # React Frontend
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── vite-env.d.ts
│   │   │
│   │   ├── components/           # Reusable components
│   │   │   ├── ui/               # Base UI components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Table.tsx
│   │   │   │   └── index.ts
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── DashboardLayout.tsx
│   │   │   └── shared/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       └── ProtectedRoute.tsx
│   │   │
│   │   ├── pages/                # Page components
│   │   │   ├── auth/
│   │   │   │   ├── Login.tsx
│   │   │   │   ├── Register.tsx
│   │   │   │   └── ForgotPassword.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   └── Analytics.tsx
│   │   │   ├── pages/
│   │   │   │   ├── PagesList.tsx
│   │   │   │   ├── PageSettings.tsx
│   │   │   │   └── ConnectPage.tsx
│   │   │   ├── comments/
│   │   │   │   ├── CommentsList.tsx
│   │   │   │   └── CommentDetail.tsx
│   │   │   ├── settings/
│   │   │   │   ├── Settings.tsx
│   │   │   │   ├── AIPrompts.tsx
│   │   │   │   └── ReplyRules.tsx
│   │   │   ├── billing/
│   │   │   │   ├── Plans.tsx
│   │   │   │   ├── Subscription.tsx
│   │   │   │   └── Invoices.tsx
│   │   │   └── admin/
│   │   │       ├── AdminDashboard.tsx
│   │   │       └── Organizations.tsx
│   │   │
│   │   ├── hooks/                # Custom hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useOrganization.ts
│   │   │   └── useApi.ts
│   │   │
│   │   ├── services/             # API services
│   │   │   ├── api.ts            # Axios instance
│   │   │   ├── auth.service.ts
│   │   │   ├── facebook.service.ts
│   │   │   └── billing.service.ts
│   │   │
│   │   ├── stores/               # Zustand stores
│   │   │   ├── authStore.ts
│   │   │   └── organizationStore.ts
│   │   │
│   │   ├── types/                # TypeScript types
│   │   │   ├── auth.types.ts
│   │   │   ├── organization.types.ts
│   │   │   └── facebook.types.ts
│   │   │
│   │   ├── utils/                # Utilities
│   │   │   ├── constants.ts
│   │   │   ├── helpers.ts
│   │   │   └── validators.ts
│   │   │
│   │   └── styles/
│   │       └── globals.css
│   │
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── .env.example
│
├── docker/                        # Docker configs
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── nginx/
│       └── nginx.conf
│
├── scripts/                       # Utility scripts
│   ├── setup.sh
│   ├── deploy.sh
│   └── backup.sh
│
├── .github/                       # GitHub Actions
│   └── workflows/
│       ├── backend-ci.yml
│       └── frontend-ci.yml
│
├── .gitignore
├── README.md
└── LICENSE
```

---

## ✅ Success Metrics

### Technical KPIs
- API response time < 200ms
- 99.9% uptime
- Webhook processing < 5 seconds
- Zero data breaches

### Business KPIs
- 1000+ organizations in Year 1
- ₹2L+ MRR in 6 months
- < 5% monthly churn
- NPS > 40

---

## 📞 Support & Maintenance

### Support Channels
- Email: support@aiosol.com
- Live Chat: In-app widget
- Documentation: docs.aiosol.com
- Status Page: status.aiosol.com

### Maintenance Windows
- Weekly: Tuesday 2 AM - 4 AM IST
- Monthly: First Sunday 2 AM - 6 AM IST

---

**Document Version:** 1.0.0
**Last Updated:** May 2026
**Next Review:** June 2026

---

*This document is maintained by the AIOSOL Development Team*
