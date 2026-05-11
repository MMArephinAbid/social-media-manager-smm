# 🚀 AIOSOL - AI-Powered Facebook Comment Auto-Reply Platform

<div align="center">

![AIOSOL Logo](https://via.placeholder.com/150x150?text=AIOSOL)

**Automatically respond to your Facebook comments with intelligent, diplomatic AI-powered replies.**

[![Backend CI](https://github.com/your-org/aiosol/workflows/Backend%20CI/badge.svg)](https://github.com/your-org/aiosol/actions)
[![Frontend CI](https://github.com/your-org/aiosol/workflows/Frontend%20CI/badge.svg)](https://github.com/your-org/aiosol/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

---

## ✨ Features

- 🤖 **AI-Powered Replies** - GPT-4/Claude generates intelligent, context-aware responses
- 💬 **Diplomatic Tone** - Professional, brand-aligned communication
- 📊 **Analytics Dashboard** - Track engagement and reply performance
- 🔧 **Customizable Prompts** - Tailor AI behavior to your brand voice
- 📋 **Reply Rules** - Automate handling based on keywords, sentiment, intent
- 🏢 **Multi-tenant** - Support for 1000+ organizations
- 💳 **Billing Integration** - Razorpay & Stripe support
- 🔒 **Enterprise Security** - JWT auth, RBAC, encrypted tokens

---

## 🏗️ Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0
- **Queue:** Redis + Celery
- **Auth:** JWT with RBAC

### Frontend
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **State:** Zustand + React Query

### DevOps
- **Container:** Docker + Docker Compose
- **Proxy:** Nginx
- **CI/CD:** GitHub Actions

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/aiosol.git
cd aiosol

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your values

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 📁 Project Structure

```
aiosol/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core utilities
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── workers/      # Celery tasks
│   ├── alembic/          # Database migrations
│   └── tests/            # Backend tests
│
├── frontend/             # React Frontend
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   ├── stores/       # Zustand stores
│   │   └── types/        # TypeScript types
│   └── public/
│
├── docker/               # Docker configs
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

---

## 🔑 Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aiosol

# JWT
JWT_SECRET_KEY=your-secret-key

# Facebook
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret

# OpenAI
OPENAI_API_KEY=sk-your-key

# Razorpay
RAZORPAY_KEY_ID=rzp_test_xxx
RAZORPAY_KEY_SECRET=xxx
```

---

## 👥 Development Team

| Name | Role | Responsibility |
|------|------|----------------|
| 🧠 Rafiq | Architect | System design, Architecture |
| ⚙️ Sadia | Backend Lead | FastAPI, Database, APIs |
| 🎨 Karim | Frontend Lead | React, UI/UX |
| 🚀 Nila | DevOps | Docker, CI/CD, Deployment |
| 🤖 Tanvir | AI Engineer | OpenAI/Claude, Prompts |
| 🧪 Priya | QA Lead | Testing, Security |

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ by the AIOSOL Team**

[Documentation](docs/) • [Report Bug](issues/) • [Request Feature](issues/)

</div>
