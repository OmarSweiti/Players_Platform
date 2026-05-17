# Authentication Implementation - Action Items

**Priority Order:** High → Medium → Low  
**Estimated Time:** 2-3 days for high priority items

---

## 🔴 HIGH PRIORITY (Must Do Before Production)

### 1. Create 2FA Setup Page
**Location:** `frontend/app/(dashboard)/settings/2fa/page.tsx`  
**Time Estimate:** 4-6 hours  
**Dependencies:** Backend API already exists (`POST /auth/2fa/enable`, `POST /auth/2fa/verify`)

#### Requirements:
- [ ] Display QR code from API response
- [ ] Show manual entry key as fallback
- [ ] 6-digit TOTP code input field
- [ ] Verify button to confirm setup
- [ ] Enable/disable toggle switch
- [ ] Instructions for Google Authenticator/Authy
- [ ] Error handling for invalid codes
- [ ] Success confirmation message

#### Implementation Steps:
1. Create page component at `frontend/app/(dashboard)/settings/2fa/page.tsx`
2. Use `useEnable2FA()` hook to get QR code
3. Display QR code using a library like `qrcode.react`
4. Add input field for 6-digit code
5. Use `useVerify2FA()` hook to verify and enable
6. Add disable functionality with `useDisable2FA()` hook
7. Style according to design system

#### Code Example:
```typescript
'use client';

import { useState } from 'react';
import { useEnable2FA, useVerify2FA, useDisable2FA } from '@/features/auth/hooks/use-auth';
import { QRCodeSVG } from 'qrcode.react';
import { Button, Input, Label, Card } from '@/shared/ui';

export default function TwoFactorAuthPage() {
  const [qrCode, setQrCode] = useState<string>('');
  const [secret, setSecret] = useState<string>('');
  const [code, setCode] = useState('');
  
  const enableMutation = useEnable2FA();
  const verifyMutation = useVerify2FA();
  const disableMutation = useDisable2FA();

  const handleEnable = async () => {
    const response = await enableMutation.mutateAsync();
    setQrCode(response.data.qrCode);
    setSecret(response.data.secret);
  };

  const handleVerify = async () => {
    await verifyMutation.mutateAsync({ token: code });
    // Show success message
  };

  // ... render UI
}
```

---

### 2. Implement HTTP-only Cookie Storage
**Time Estimate:** 6-8 hours  
**Impact:** Critical security improvement  
**Files to Modify:** Multiple backend and frontend files

#### Current Issue:
Backend returns tokens in JSON response body. Frontend stores them (likely in localStorage), which is vulnerable to XSS attacks.

#### Solution:
Set tokens as HTTP-only cookies from backend. Browser automatically sends cookies with requests.

#### Backend Changes:

**File:** `backend/src/modules/auth/presentation/auth.controller.ts`

Modify login endpoint to set cookies:
```typescript
import { Res } from '@nestjs/common';
import type { Response } from 'express';

@Post('login')
async login(
  @Body() loginDto: LoginDto, 
  @Req() req: RequestWithUser,
  @Res({ passthrough: true }) res: Response  // Add this
) {
  const tenantId = req.tenantId || 'default-tenant';
  const result = await this.loginUseCase.execute(loginDto, tenantId);
  
  // Set HTTP-only cookies
  res.cookie('accessToken', result.accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production', // HTTPS only in production
    sameSite: 'strict',
    maxAge: 15 * 60 * 1000, // 15 minutes
  });
  
  res.cookie('refreshToken', result.refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  });
  
  // Return user data without tokens
  return {
    user: result.user,
  };
}
```

Apply same pattern to:
- [ ] `/auth/register` endpoint
- [ ] `/auth/refresh` endpoint

**File:** `backend/src/main.ts`

Enable CORS with credentials:
```typescript
app.enableCors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true, // Allow cookies
});
```

#### Frontend Changes:

**File:** `frontend/src/shared/lib/api-client.ts`

Update Axios configuration:
```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api',
  withCredentials: true, // Send cookies automatically
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Remove token storage from:**
- [ ] `frontend/src/features/auth/hooks/use-auth.ts` - Remove any localStorage.setItem calls
- [ ] Any other files that manually store tokens

**Update auth provider:**
- [ ] `frontend/src/components/providers/auth-provider.tsx` - Remove token checking logic, rely on cookie existence

#### Testing:
1. Test login - verify cookies are set in browser DevTools
2. Test API calls - verify cookies are sent automatically
3. Test refresh token rotation
4. Test logout - verify cookies are cleared
5. Test in production environment with HTTPS

---

### 3. Add Auto-logout Interceptor for 401 Responses
**Time Estimate:** 2-3 hours  
**Files to Modify:** `frontend/src/shared/lib/api-client.ts`

#### Implementation:

```typescript
import axios from 'axios';
import { ROUTES } from './constants';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth state
      if (typeof window !== 'undefined') {
        // Clear React Query cache
        window.location.href = ROUTES.LOGIN;
      }
    }
    return Promise.reject(error);
  }
);
```

**Better approach with React Query:**

Create a custom hook or update the query client configuration to handle 401s globally.

---

## 🟡 MEDIUM PRIORITY (Should Do)

### 4. Add Password Strength Indicator UI
**Location:** `frontend/app/(auth)/register/page.tsx`  
**Time Estimate:** 2-3 hours

#### Requirements:
- [ ] Visual indicator showing password strength (weak/medium/strong)
- [ ] Checklist of requirements (8+ chars, uppercase, lowercase, number, special char)
- [ ] Real-time updates as user types
- [ ] Color coding (red/yellow/green)

#### Implementation:
Use a library like `zxcvbn` or implement custom strength checker.

```typescript
const checkPasswordStrength = (password: string) => {
  const checks = [
    { test: password.length >= 8, label: 'At least 8 characters' },
    { test: /[A-Z]/.test(password), label: 'One uppercase letter' },
    { test: /[a-z]/.test(password), label: 'One lowercase letter' },
    { test: /\d/.test(password), label: 'One number' },
    { test: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password), label: 'One special character' },
  ];
  
  const passed = checks.filter(c => c.test).length;
  const strength = passed / checks.length;
  
  return { checks, strength };
};
```

---

### 5. Add "Remember Me" Checkbox
**Location:** `frontend/app/(auth)/login/page.tsx`  
**Time Estimate:** 2 hours

#### Backend Changes:
Modify login endpoint to accept `rememberMe` parameter and adjust refresh token expiry accordingly.

#### Frontend Changes:
Add checkbox to login form and pass to API.

---

### 6. Implement Role-Based Route Guards (Frontend)
**Time Estimate:** 4-6 hours

#### Implementation:
Create a higher-order component or hook to protect routes based on user role.

```typescript
// frontend/src/components/guards/role-guard.tsx
import { useAuth } from '@/features/auth';
import { UserRole } from '@/features/auth/types/auth.types';
import { useRouter } from 'next/navigation';

interface RoleGuardProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
  redirectTo?: string;
}

export function RoleGuard({ allowedRoles, children, redirectTo = '/unauthorized' }: RoleGuardProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!user || !allowedRoles.includes(user.role)) {
    router.push(redirectTo);
    return null;
  }

  return <>{children}</>;
}
```

Usage:
```typescript
<RoleGuard allowedRoles={[UserRole.ADMIN, UserRole.COACH]}>
  <AdminDashboard />
</RoleGuard>
```

---

### 7. Create Permission-Based Component
**Time Estimate:** 3-4 hours

```typescript
// frontend/src/components/guards/permission-guard.tsx
import { useAuth } from '@/features/auth';

interface CanProps {
  permission: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function Can({ permission, children, fallback = null }: CanProps) {
  const { user } = useAuth();
  
  // Check if user has permission (implement logic based on your permission system)
  const hasPermission = checkUserPermission(user, permission);
  
  return hasPermission ? <>{children}</> : <>{fallback}</>;
}
```

Usage:
```typescript
<Can permission="player.create">
  <Button>Create Player</Button>
</Can>
```

---

## 🟢 LOW PRIORITY (Nice to Have)

### 8. Generate Backup Codes for 2FA
**Time Estimate:** 4-5 hours

#### Backend:
- [ ] Generate 10 random backup codes when 2FA is enabled
- [ ] Hash and store in database
- [ ] Return unhashed codes to user (one-time display)
- [ ] Allow backup code usage during login

#### Frontend:
- [ ] Display backup codes in modal after 2FA setup
- [ ] Provide download/print options
- [ ] Warn user to save codes securely

---

### 9. Create Session Tracking Table
**Time Estimate:** 6-8 hours

#### Database:
Add `UserSession` model to schema.prisma:
```prisma
model UserSession {
  id           String   @id @default(uuid())
  userId       String   @db.Uuid
  refreshToken String   @db.VarChar(500)
  ipAddress    String?  @db.VarChar(45)
  userAgent    String?  @db.VarChar(500)
  createdAt    DateTime @default(now())
  expiresAt    DateTime
  revokedAt    DateTime?
  
  @@index([userId])
  @@index([refreshToken])
}
```

#### Backend:
- [ ] Store session on login
- [ ] Validate session on token refresh
- [ ] Revoke session on logout
- [ ] List active sessions endpoint (already exists, needs implementation)
- [ ] Revoke specific session endpoint

---

### 10. Add CAPTCHA to Registration
**Time Estimate:** 3-4 hours

Integrate Google reCAPTCHA v3 or hCaptcha to prevent bot registrations.

---

## 📋 Testing Checklist

After implementing each feature:

### Manual Testing
- [ ] Test happy path (successful flow)
- [ ] Test error cases (invalid input, expired tokens, etc.)
- [ ] Test edge cases (network failures, concurrent requests)
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test on mobile devices

### Security Testing
- [ ] Verify tokens are not accessible via JavaScript (if using HTTP-only cookies)
- [ ] Test rate limiting is working
- [ ] Test account lockout after failed attempts
- [ ] Verify email verification tokens expire correctly
- [ ] Test multi-tenant isolation (user from tenant A can't access tenant B data)

### Performance Testing
- [ ] Measure login response time
- [ ] Test with concurrent users
- [ ] Monitor database query performance
- [ ] Check memory usage

---

## 🎯 Success Criteria

Authentication system is considered complete when:

- [ ] All high-priority items are implemented
- [ ] All auth flows work end-to-end without errors
- [ ] Security audit passes with no critical vulnerabilities
- [ ] Unit tests cover 80%+ of auth logic
- [ ] Integration tests cover all API endpoints
- [ ] E2E tests cover critical user journeys
- [ ] Documentation is up-to-date
- [ ] Performance meets acceptable thresholds (<500ms for login)

---

## 📚 Resources

### Libraries to Install
```bash
# For QR code generation (2FA page)
npm install qrcode.react

# For password strength checking
npm install zxcvbn
npm install @types/zxcvbn

# For CAPTCHA (optional)
npm install react-google-recaptcha
```

### Documentation References
- [NestJS Authentication](https://docs.nestjs.com/security/authentication)
- [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

## 📞 Support

If you encounter issues:
1. Check the detailed audit report: `AUTH_IMPLEMENTATION_AUDIT.md`
2. Review the summary: `AUTH_SUMMARY.md`
3. Consult NestJS and Next.js documentation
4. Search for similar issues in project issues/PRs

---

**Last Updated:** May 10, 2026  
**Estimated Total Time:** 2-3 days for high priority, 1-2 weeks for all items
