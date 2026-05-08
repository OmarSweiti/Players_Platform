# Players Platform - Comprehensive Development Guide

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Development Workflow](#development-workflow)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)
- [Useful Tips](#useful-tips)

---

## 🛠️ Prerequisites

Before starting, ensure you have the following installed:

### Required Software
- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **PostgreSQL** (v14 or higher) - [Download](https://www.postgresql.org/download/)
- **Redis** (v6 or higher) - [Download](https://redis.io/download/)
- **Git** - [Download](https://git-scm.com/)

### Verify Installation
```bash
node --version    # Should be v18+
npm --version     # Should be 9+
psql --version    # Should be v14+
redis-cli --version  # Should be v6+
```

---

## 📁 Project Structure

```
Players_Platform/
├── backend/                 # NestJS Backend API
│   ├── src/
│   │   ├── modules/        # Feature modules (auth, players, scouting, etc.)
│   │   ├── common/         # Shared utilities, guards, decorators
│   │   ├── config/         # Configuration files
│   │   ├── database/       # Database seed scripts
│   │   └── main.ts         # Application entry point
│   ├── prisma/
│   │   ├── schema.prisma   # Database schema
│   │   └── migrations/     # Database migrations
│   ├── .env                # Environment variables
│   └── package.json
│
├── frontend/               # Next.js Frontend Application
│   ├── app/               # Next.js App Router pages
│   │   ├── (auth)/        # Authentication routes (login, register)
│   │   └── (dashboard)/   # Protected dashboard routes
│   ├── src/
│   │   ├── features/      # Feature modules
│   │   ├── shared/        # Reusable components and utilities
│   │   └── components/    # Layout and provider components
│   ├── .env.local         # Environment variables
│   └── package.json
│
└── IMPLEMENTATION_CHECKLIST.md
```

---

## ⚙️ Environment Setup

### 1. Backend Environment Configuration

Navigate to the backend directory:
```bash
cd backend
```

The `.env` file should already exist with default values. Review and adjust if needed:

```env
# Server Configuration
PORT=3000
NODE_ENV=development

# Database Configuration
DATABASE_URL="postgresql://postgres:your_password@localhost:5432/players_platform?schema=public"

# JWT Configuration (MUST be at least 32 characters)
JWT_SECRET=dev-jwt-secret-key-must-be-at-least-32-characters-long!!!
JWT_EXPIRES_IN=15m
JWT_REFRESH_SECRET=dev-refresh-secret-key-must-be-at-least-32-characters-long!
JWT_REFRESH_EXPIRES_IN=7d

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Storage Configuration
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./uploads

# CORS Configuration
CORS_ORIGIN=http://localhost:3001

# Email Configuration
MAIL_FROM=noreply@example.com
```

**⚠️ Important:** Update `DATABASE_URL` with your actual PostgreSQL credentials.

### 2. Frontend Environment Configuration

Navigate to the frontend directory:
```bash
cd frontend
```

The `.env.local` file should exist:

```env
NEXT_PUBLIC_API_URL=http://localhost:3000/api
NEXT_PUBLIC_APP_NAME=Players Platform
```

This is usually fine as-is for local development.

---

## 🗄️ Database Setup

### Step 1: Create PostgreSQL Database

Connect to PostgreSQL and create the database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Inside psql, run:
CREATE DATABASE players_platform;
\q
```

Or use a single command:
```bash
createdb -U postgres players_platform
```

### Step 2: Install Backend Dependencies

```bash
cd backend
npm install
```

### Step 3: Generate Prisma Client

After installing dependencies, generate the Prisma client:

```bash
npx prisma generate
```

This creates TypeScript types based on your schema.

### Step 4: Run Database Migrations

Apply all migrations to create the database schema:

```bash
npx prisma migrate deploy
```

For development with reset capability:
```bash
npx prisma migrate dev
```

### Step 5: Seed the Database (Optional)

Populate the database with initial data:

```bash
npm run seed
```

This creates:
- Default tenant
- Admin user
- Sample roles and permissions

**Default Admin Credentials:**
- Email: `admin@platform.com`
- Password: `Admin@123`

---

## 🚀 Running the Application

### Option 1: Run Backend Only

```bash
cd backend

# Development mode with auto-reload
npm run start:dev

# Production mode (after building)
npm run build
npm run start:prod

# Debug mode
npm run start:debug
```

**Backend will be available at:** `http://localhost:3000`

**API Documentation (Swagger):** `http://localhost:3000/api/docs`

### Option 2: Run Frontend Only

```bash
cd frontend

# Delete corrupted cache first (if experiencing crashes)
Remove-Item -Recurse -Force .next

# Development mode with hot-reload (stable webpack bundler)
npm run dev

# Production mode (after building)
npm run build
npm run start
```

**Frontend will be available at:** `http://localhost:3001`

**⚠️ Important Notes:**
- **Turbopack Issues:** Next.js 16's Turbopack is experimental and may crash on Windows. If you see "FATAL: An unexpected Turbopack error", delete the `.next` folder and restart.
- **Middleware → Proxy Migration:** In Next.js 16, `middleware.ts` has been renamed to `proxy.ts`, AND the exported function must be named `proxy` (not `middleware`). This project uses the correct convention.
- **Cache Problems:** If you experience strange errors, always try deleting `.next` folder first.

### Option 3: Run Both (Recommended for Development)

Open **two terminal windows**:

**Terminal 1 - Backend:**
```bash
cd backend
npm run start:dev
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Now you can:
- Access frontend: `http://localhost:3001`
- Access backend API: `http://localhost:3000`
- View API docs: `http://localhost:3000/api/docs`

---

## 💻 Development Workflow

### Making Changes to Backend

1. **Edit code** in `backend/src/`
2. **Server auto-reloads** (when using `npm run start:dev`)
3. **Test changes** via Swagger UI or frontend
4. **If you modify Prisma schema:**
   ```bash
   npx prisma generate
   npx prisma migrate dev
   ```

### Making Changes to Frontend

1. **Edit code** in `frontend/app/` or `frontend/src/`
2. **Next.js auto-updates** the browser
3. **View changes** at `http://localhost:3001`
4. **Check console** for any errors

### Full-Stack Development Example

**Scenario:** Adding a new player feature

1. **Backend:**
   ```bash
   cd backend
   npm run start:dev
   ```
   - Create endpoint in `src/modules/players/`
   - Test via Swagger UI

2. **Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   - Create API client in `src/features/players/api/`
   - Create React hooks in `src/features/players/hooks/`
   - Build UI component
   - Test in browser

---

## 📝 Common Commands Reference

### Backend Commands

```bash
# Navigate to backend
cd backend

# Install dependencies
npm install

# Development
npm run start:dev          # Watch mode with auto-reload
npm run start:debug        # Debug mode with breakpoints

# Build & Production
npm run build              # Compile TypeScript
npm run start:prod         # Run production build

# Database
npx prisma generate        # Generate Prisma client
npx prisma migrate dev     # Create and apply migrations
npx prisma migrate deploy  # Apply migrations (production)
npx prisma studio          # Open Prisma Studio (visual DB browser)
npm run seed               # Seed database with initial data

# Testing
npm run test               # Run unit tests
npm run test:watch         # Watch mode for tests
npm run test:cov           # Test coverage report
npm run test:e2e           # End-to-end tests

# Code Quality
npm run lint               # Lint and fix code
npm run format             # Format code with Prettier
```

### Frontend Commands

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Development
npm run dev                # Start dev server with hot-reload

# Build & Production
npm run build              # Build for production
npm run start              # Run production build

# Code Quality
npm run lint               # Lint code
```

### Useful Utilities

```bash
# Check what's running on ports
# Windows (PowerShell):
netstat -ano | findstr :3000
netstat -ano | findstr :3001

# Kill process on port (Windows):
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9
lsof -ti:3001 | xargs kill -9
```

---

## 🔧 Troubleshooting

### Backend Issues

#### Problem: Port 3000 already in use
```bash
# Find the process
netstat -ano | findstr :3000

# Kill it (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in .env
PORT=3002
```

#### Problem: Database connection error
```bash
# Verify PostgreSQL is running
pg_ctl status

# Check DATABASE_URL in .env
# Ensure database exists
psql -U postgres -l | findstr players_platform

# Recreate if needed
dropdb -U postgres players_platform
createdb -U postgres players_platform
npx prisma migrate deploy
```

#### Problem: Prisma client not generating
```bash
# Clean and regenerate
rm -rf node_modules/.prisma
npx prisma generate
```

#### Problem: Redis connection error
```bash
# Start Redis server
redis-server

# Or check if running
redis-cli ping  # Should return "PONG"
```

### Frontend Issues

#### Problem: Turbopack Fatal Errors (Next.js 16)

If you see errors like:
```
FATAL: An unexpected Turbopack error occurred.
```

**Solution:**
```bash
cd frontend

# Delete corrupted cache
Remove-Item -Recurse -Force .next

# Restart dev server
npm run dev
```

**Why this happens:**
- Turbopack is experimental in Next.js 16
- Windows filesystem can cause issues
- Corrupted `.next` cache directory
- Unsupported configuration options

**Prevention:**
- Always use `proxy.ts` instead of `middleware.ts` (Next.js 16 requirement)
- Avoid experimental features in `next.config.ts`
- Keep `.next` folder out of OneDrive/synced folders

#### Problem: Port 3001 already in use
```bash
# Next.js will automatically try 3002, 3003, etc.
# Or specify port:
npm run dev -- -p 3002
```

#### Problem: API requests failing
```bash
# Check backend is running
curl http://localhost:3000/health

# Verify .env.local has correct API URL
cat .env.local
# Should show: NEXT_PUBLIC_API_URL=http://localhost:3000/api

# Clear browser cache and cookies
# Check browser DevTools → Network tab
```

#### Problem: Build fails
```bash
# Clear Next.js cache
rm -rf .next
npm run build

# Check for TypeScript errors
npx tsc --noEmit
```

#### Problem: Authentication not working
```bash
# Verify backend is setting cookies
# Check DevTools → Application → Cookies

# Ensure CORS_ORIGIN in backend .env matches frontend URL
# Backend: CORS_ORIGIN=http://localhost:3001
```

### Common Full-Stack Issues

#### Problem: Changes not reflecting
```bash
# Backend: Restart server
# Press Ctrl+C, then npm run start:dev

# Frontend: Hard refresh browser
# Windows: Ctrl + Shift + R
# Mac: Cmd + Shift + R
```

#### Problem: TypeScript errors after schema changes
```bash
# Regenerate Prisma client
cd backend
npx prisma generate

# Restart TypeScript server in VS Code
# Press Ctrl+Shift+P → "TypeScript: Restart TS Server"
```

---

## 💡 Useful Tips

### 1. Use Prisma Studio for Database Management

Visual database browser:
```bash
cd backend
npx prisma studio
```
Opens at `http://localhost:5555`

### 2. Monitor Logs Effectively

**Backend logs:** Visible in terminal where `npm run start:dev` is running

**Frontend logs:** 
- Browser console (F12 → Console tab)
- Terminal where `npm run dev` is running

### 3. API Testing with Swagger

Access interactive API documentation:
```
http://localhost:3000/api/docs
```

Features:
- Test all endpoints
- See request/response schemas
- Authenticate and test protected routes

### 4. Hot Reload Best Practices

- **Backend:** Saves trigger recompilation (takes 2-5 seconds)
- **Frontend:** Saves trigger instant browser update
- If hot reload fails, restart the dev server

### 5. Environment Variables Management

**Never commit sensitive data!**

- Backend: `.env` is in `.gitignore`
- Frontend: `.env.local` is in `.gitignore`

Create `.env.example` files for team sharing:
```env
# .env.example
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
JWT_SECRET=your-secret-here
```

### 6. Debugging Backend

Add breakpoints in VS Code:
1. Click left of line number to set breakpoint
2. Run: `npm run start:debug`
3. Use VS Code debugger panel

### 7. Debugging Frontend

React Query DevTools:
- Automatically appears in development mode
- Bottom-right corner of browser
- Inspect queries, mutations, cache

### 8. Quick Database Reset (Development Only)

```bash
cd backend
npx prisma migrate reset  # Drops and recreates database
npm run seed              # Reseed with initial data
```

⚠️ **Warning:** This deletes all data!

### 9. Check Dependencies Status

```bash
# Backend
cd backend
npm outdated

# Frontend
cd frontend
npm outdated
```

### 10. Clean Install (When Things Break)

```bash
# Backend
cd backend
rm -rf node_modules package-lock.json
npm install
npx prisma generate

# Frontend
cd frontend
rm -rf node_modules package-lock.json .next
npm install
```

---

## 🎯 First-Time Setup Checklist

Follow these steps for a fresh setup:

- [ ] Install Node.js, PostgreSQL, Redis
- [ ] Clone the repository
- [ ] Create PostgreSQL database: `players_platform`
- [ ] Configure `backend/.env` with your database credentials
- [ ] Install backend dependencies: `cd backend && npm install`
- [ ] Generate Prisma client: `npx prisma generate`
- [ ] Run migrations: `npx prisma migrate deploy`
- [ ] Seed database: `npm run seed`
- [ ] Start backend: `npm run start:dev`
- [ ] Verify backend: Visit `http://localhost:3000/health`
- [ ] Install frontend dependencies: `cd frontend && npm install`
- [ ] Start frontend: `npm run dev`
- [ ] Verify frontend: Visit `http://localhost:3001`
- [ ] Login with admin credentials
- [ ] Set Tenant ID in localStorage: `localStorage.setItem('tenantId', 'dev-tenant-001')`

---

## 📚 Additional Resources

### Documentation Files
- `backend/BACKEND_IMPLEMENTATION_STANDARDS.md` - Backend coding standards
- `frontend/FRONTEND_IMPLEMENTATION.md` - Frontend architecture guide
- `frontend/QUICK_START.md` - Frontend quick start guide
- `frontend/FEATURE_IMPLEMENTATION_TEMPLATE.md` - How to add new features

### External Resources
- [NestJS Documentation](https://docs.nestjs.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [React Query Documentation](https://tanstack.com/query/latest)

---

## 🆘 Getting Help

If you encounter issues:

1. **Check this guide's troubleshooting section**
2. **Review error messages carefully** - they often contain the solution
3. **Check backend/frontend logs** for detailed error information
4. **Verify all services are running** (PostgreSQL, Redis, backend, frontend)
5. **Clear caches** and restart services
6. **Search the implementation docs** for specific guidance

---

## 🎉 You're Ready!

You now have everything you need to work effectively with the Players Platform project. Happy coding! 🚀

**Quick Start Summary:**
```bash
# Terminal 1 - Backend
cd backend
npm run start:dev

# Terminal 2 - Frontend  
cd frontend
npm run dev

# Open browser
# Frontend: http://localhost:3001
# Backend API Docs: http://localhost:3000/api/docs
```
