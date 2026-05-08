# Quick Fix Reference - Common Issues

## 🚨 Turbopack Crashes (Next.js 16)

### Symptoms
```
FATAL: An unexpected Turbopack error occurred.
A panic log has been written to C:\Users\...\next-panic-....log
```

### Quick Fix
```powershell
cd frontend
Remove-Item -Recurse -Force .next
npm run dev
```

### Why It Happens
- Turbopack is **experimental** in Next.js 16
- Windows filesystem compatibility issues
- Corrupted `.next` cache
- Invalid configuration options

### Prevention
✅ Use `proxy.ts` instead of `middleware.ts`  
✅ Keep `.next` folder local (not in OneDrive/cloud sync)  
✅ Avoid experimental features in `next.config.ts`  
✅ Clear cache regularly if crashes occur  

---

## 🔧 Middleware → Proxy Migration (Next.js 16)

### What Changed
- **Old:** `middleware.ts` with `export function middleware()`
- **New:** `proxy.ts` with `export function proxy()`

### Changes Required
When migrating from middleware to proxy in Next.js 16:

1. **Rename file:** `middleware.ts` → `proxy.ts`
2. **Rename function:** `export function middleware()` → `export function proxy()`
3. **Config stays the same:** `export const config` remains unchanged

### Already Done ✓
This project has been updated to use `proxy.ts` with the correct `proxy` function export.

### Example Migration
```typescript
// OLD (middleware.ts) - DON'T USE
export function middleware(request: NextRequest) {
  // ... logic
}

// NEW (proxy.ts) - CORRECT
export function proxy(request: NextRequest) {
  // ... same logic
}
```

---

## 🗑️ Cache Reset Commands

### Frontend Cache Reset
```powershell
cd frontend

# Delete .next folder (safe, regenerates on next run)
Remove-Item -Recurse -Force .next

# Optional: Full reset if problems persist
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Backend Cache Reset
```powershell
cd backend

# Regenerate Prisma client
npx prisma generate

# Restart TypeScript server in VS Code
# Ctrl+Shift+P → "TypeScript: Restart TS Server"
```

---

## 📁 Project Structure Reminder

```
frontend/
├── proxy.ts              ← Route protection (was middleware.ts)
├── app/                  ← Next.js pages
├── src/
│   ├── features/         ← Feature modules
│   ├── shared/           ← Shared utilities
│   └── components/       ← Layout components
├── .next/                ← Build cache (DELETE IF CRASHING)
└── .env.local            ← Environment variables

backend/
├── src/
│   ├── modules/          ← Feature modules
│   ├── common/           ← Shared guards, decorators
│   └── main.ts           ← Entry point
├── prisma/
│   └── schema.prisma     ← Database schema
└── .env                  ← Environment variables
```

---

## 🎯 Standard Startup Sequence

### Terminal 1 - Backend
```powershell
cd backend
npm run start:dev
# Wait for: "Application is running on: http://localhost:3000"
```

### Terminal 2 - Frontend
```powershell
cd frontend

# If first time or after crashes:
Remove-Item -Recurse -Force .next

npm run dev
# Wait for: "Ready in X.Xs"
```

### Verify
- Frontend: http://localhost:3001
- Backend API: http://localhost:3000
- API Docs: http://localhost:3000/api/docs

---

## ⚡ Common Error Solutions

### Error: "middleware file convention is deprecated"
**Fix:** Already resolved - renamed to `proxy.ts`

### Error: "Turbopack panic" / "FATAL error"
**Fix:** Delete `.next` folder and restart

### Error: "Port 3000/3001 already in use"
**Fix:** 
```powershell
# Find process
netstat -ano | findstr :3000

# Kill it
taskkill /PID <PID> /F
```

### Error: "GET /api/auth/me 404"
**Cause:** Frontend trying to access non-existent route  
**Fix:** This is expected if backend isn't running or auth endpoint doesn't exist yet

### Error: "Slow filesystem detected"
**Cause:** Project on slow drive or synced folder  
**Impact:** Slower compilation, not fatal  
**Fix:** Move project to local SSD, exclude from OneDrive

---

## 💡 Pro Tips

1. **Always delete `.next` when:**
   - Seeing Turbopack crashes
   - After major dependency updates
   - When behavior seems inconsistent

2. **Backend TypeScript errors?**
   ```powershell
   cd backend
   npx prisma generate
   # Restart dev server
   ```

3. **Frontend acting weird?**
   ```powershell
   cd frontend
   Remove-Item -Recurse -Force .next
   npm run dev
   ```

4. **Want clean slate?**
   ```powershell
   # Both backend and frontend
   cd backend && Remove-Item -Recurse -Force node_modules,package-lock.json,dist
   cd ../frontend && Remove-Item -Recurse -Force node_modules,package-lock.json,.next
   
   # Reinstall
   cd backend && npm install
   cd ../frontend && npm install
   ```

---

## 📞 Emergency Checklist

If everything is broken:

1. ✅ Stop all dev servers (Ctrl+C)
2. ✅ Delete `frontend/.next`
3. ✅ Regenerate Prisma: `cd backend && npx prisma generate`
4. ✅ Start backend: `cd backend && npm run start:dev`
5. ✅ Wait for backend to be ready
6. ✅ Start frontend: `cd frontend && npm run dev`
7. ✅ Check browser console for errors
8. ✅ Check terminal logs for both services

---

## 🔗 Useful Links

- [Next.js 16 Documentation](https://nextjs.org/docs)
- [Turbopack Status](https://nextjs.org/docs/architecture/turbopack)
- [Middleware → Proxy Migration](https://nextjs.org/docs/messages/middleware-to-proxy)
- [Project Development Guide](./DEVELOPMENT_GUIDE.md)

---

**Last Updated:** Based on Next.js 16.2.4 with Turbopack (experimental)
