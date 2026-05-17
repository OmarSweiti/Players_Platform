# Authentication & Authorization Testing Guide

This guide will help you test the complete authentication and authorization flow for all user roles in the Players Platform.

## 📋 Prerequisites

1. **Database Setup**: Ensure PostgreSQL is running
2. **Backend Running**: `cd backend && npm run start:dev`
3. **Frontend Running**: `cd frontend && npm run dev`

---

## 🚀 Step 1: Seed the Database

Run the seed script to create test users and tenants:

```bash
cd backend
npm run seed
```

This will create:
- **SUPER_ADMIN** account with platform-wide access
- **3 sample tenants** (Manchester United, Real Madrid Academy, Barcelona Youth)
- **Admin users** for each tenant

### Default Credentials

After seeding, you'll see output like this:

```
Login Credentials:
------------------
SUPER_ADMIN: admin@players-platform.com / Admin@123456
Tenant ID: <uuid-here>

Sample Tenants:
- Manchester United FC: admin@manchester-united.com / Admin@123456
  Tenant ID: <uuid-here>
- Real Madrid Academy: admin@real-madrid-academy.com / Admin@123456
  Tenant ID: <uuid-here>
- Barcelona Youth Club: admin@barcelona-youth.com / Admin@123456
  Tenant ID: <uuid-here>
```

**Copy these Tenant IDs** - you'll need them for registration!

---

## 🧪 Step 2: Test SUPER_ADMIN Login

### 2.1 Login as SUPER_ADMIN

1. Open browser: `http://localhost:3000/login`
2. Enter credentials:
   - Email: `admin@players-platform.com`
   - Password: `Admin@123456`
3. Click "Sign In"

**Expected Result:**
- ✅ Redirected to dashboard (`/dashboard`)
- ✅ No error messages
- ✅ User menu shows "Platform Administrator"

### 2.2 Verify SUPER_ADMIN Profile

1. Navigate to profile/settings
2. Check user role displays as "SUPER_ADMIN"
3. Verify email is verified

**API Test (Optional):**
```bash
curl -X GET http://localhost:3001/auth/me \
  -H "Cookie: accessToken=<your-token>"
```

---

## 🏢 Step 3: Test Tenant Creation (SUPER_ADMIN Only)

As SUPER_ADMIN, you should be able to create new tenants.

### 3.1 Create a New Tenant

**Note**: If tenant creation UI doesn't exist yet, use the API directly:

```bash
curl -X POST http://localhost:3001/tenants \
  -H "Content-Type: application/json" \
  -H "Cookie: accessToken=<your-token>" \
  -d '{
    "name": "Test Football Club",
    "slug": "test-fc",
    "domain": "testfc.players-platform.com"
  }'
```

**Expected Result:**
- ✅ New tenant created with unique ID
- ✅ Response includes tenant details

### 3.2 List All Tenants

```bash
curl -X GET http://localhost:3001/tenants \
  -H "Cookie: accessToken=<your-token>"
```

**Expected Result:**
- ✅ Returns list of all tenants (platform-admin + 3 samples + new one)
- ✅ Each tenant has: id, name, slug, isActive status

---

## 👥 Step 4: Test Tenant User Registration

Now test how users from different tenants register and login.

### 4.1 Register a New User for Manchester United

1. Get Manchester United's Tenant ID from seed output
2. Go to: `http://localhost:3000/register`
3. Fill in:
   - First Name: `John`
   - Last Name: `Coach`
   - Email: `john.coach@manutd.com`
   - Password: `Coach@123456` (must meet strength requirements)
   - Tenant ID: `<manchester-united-tenant-id>`
4. Click "Create Account"

**Password Strength Indicator Test:**
- Type weak password first (e.g., "password") → See red indicator
- Add uppercase → See improvement
- Add numbers and special chars → See green "Strong" indicator
- Verify all 5 requirements show checkmarks when met

**Expected Result:**
- ✅ Account created successfully
- ✅ Message: "Registration successful. Please check your email to verify your account."
- ⚠️ Email verification link (in development, check console logs or database)

### 4.2 Verify Email (Development Mode)

Since email sending may not be configured, manually verify:

```bash
# Find the user in database
psql -U postgres -d players_platform

# Run query:
SELECT id, email, "emailVerificationToken", "emailVerifiedAt" 
FROM users 
WHERE email = 'john.coach@manutd.com';

# Manually verify:
UPDATE users 
SET "emailVerifiedAt" = NOW() 
WHERE email = 'john.coach@manutd.com';
```

### 4.3 Login as Tenant User

1. Go to: `http://localhost:3000/login`
2. Enter:
   - Email: `john.coach@manutd.com`
   - Password: `Coach@123456`
3. Click "Sign In"

**Expected Result:**
- ✅ Login successful
- ✅ Redirected to dashboard
- ✅ User role shows as default role (likely PLAYER or COACH based on schema)
- ✅ Tenant isolation working (can only see Manchester United data)

---

## 🔐 Step 5: Test Multi-Tenant Isolation

Verify that users from different tenants cannot access each other's data.

### 5.1 Login as Manchester United Admin

1. Email: `admin@manchester-united.com`
2. Password: `Admin@123456`
3. Tenant ID: `<manchester-united-id>`

### 5.2 Attempt to Access Another Tenant's Data

```bash
# Try to get Real Madrid's tenant info (should fail)
curl -X GET http://localhost:3001/tenants/<real-madrid-tenant-id> \
  -H "Cookie: accessToken=<manutd-admin-token>"
```

**Expected Result:**
- ❌ 403 Forbidden or 404 Not Found
- ✅ Cannot access data from other tenants

### 5.3 Verify Data Isolation

Create a player as Manchester United admin:

```bash
curl -X POST http://localhost:3001/players \
  -H "Content-Type: application/json" \
  -H "Cookie: accessToken=<manutd-admin-token>" \
  -d '{
    "fullName": "Marcus Rashford",
    "dateOfBirth": "1997-10-31",
    "position": "LW",
    "nationality": "England"
  }'
```

Then login as Real Madrid admin and try to list players:

```bash
curl -X GET http://localhost:3001/players \
  -H "Cookie: accessToken=<realmadrid-admin-token>"
```

**Expected Result:**
- ✅ Real Madrid admin sees ONLY Real Madrid players
- ✅ Marcus Rashford (Man Utd player) NOT in the list

---

## 🛡️ Step 6: Test Security Features

### 6.1 Password Visibility Toggle

1. Go to login page
2. Type password in password field
3. Click eye icon 👁️

**Expected Result:**
- ✅ Password text becomes visible
- ✅ Icon changes to crossed eye 👁️‍🗨️
- ✅ Clicking again hides password

### 6.2 Remember Me Checkbox

1. On login page, check "Remember me"
2. Login successfully
3. Close browser completely
4. Reopen and navigate to app

**Expected Result:**
- ✅ Still logged in (if cookies persist)
- OR session expires based on token expiry (15 min for access token)

### 6.3 Failed Login Attempts & Account Lockout

1. Login with wrong password 5 times
2. On 6th attempt, try correct password

**Expected Result:**
- ✅ After 5 failures: "Account locked. Try again in 30 minutes"
- ✅ Correct password rejected while locked
- ✅ `lockedUntil` timestamp set in database

Check database:
```sql
SELECT "failedLoginAttempts", "lockedUntil" 
FROM users 
WHERE email = 'admin@players-platform.com';
```

### 6.4 Rate Limiting

Send 6+ login requests within 1 minute:

```bash
for i in {1..6}; do
  curl -X POST http://localhost:3001/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@players-platform.com","password":"wrong"}'
done
```

**Expected Result:**
- ✅ First 5 requests: 401 Unauthorized (wrong password)
- ✅ 6th request: 429 Too Many Requests

---

## 🔑 Step 7: Test Two-Factor Authentication (2FA)

### 7.1 Enable 2FA

1. Login as any user
2. Navigate to: `http://localhost:3000/dashboard/settings/2fa`
3. Click "Enable 2FA"
4. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
5. Enter 6-digit code from app
6. Click "Verify & Enable"

**Expected Result:**
- ✅ QR code displayed
- ✅ Secret key available for manual entry
- ✅ 2FA enabled after verification
- ✅ Backup codes generated (8 codes)
- ✅ Can download/copy backup codes

### 7.2 Test 2FA Login

1. Logout
2. Login with email/password
3. Should prompt for 2FA code (if implemented in login flow)
4. Enter code from authenticator app

**Expected Result:**
- ✅ Login requires 2FA code
- ✅ Invalid code rejected
- ✅ Valid code grants access

### 7.3 Disable 2FA

1. Go back to 2FA settings page
2. Enter current 6-digit code
3. Click "Disable 2FA"

**Expected Result:**
- ✅ 2FA disabled
- ✅ Next login doesn't require 2FA code

---

## 🔄 Step 8: Test Token Refresh & Session Management

### 8.1 Token Auto-Refresh

1. Login successfully
2. Wait 14 minutes (access token expires at 15 min)
3. Make an API request

**Expected Result:**
- ✅ Access token automatically refreshed via refresh token
- ✅ No interruption to user experience
- ✅ New access token issued

### 8.2 Logout from All Devices

1. Login on multiple browsers/devices
2. On one device, go to settings/sessions
3. Click "Logout from all devices"

**Expected Result:**
- ✅ All sessions invalidated
- ✅ Other devices logged out immediately
- ✅ Redirected to login page

### 8.3 Session Revocation (Limited)

1. View active sessions
2. Try to revoke a specific session

**Expected Result:**
- ⚠️ Message: "Session revocation requires token blacklisting implementation"
- ℹ️ This is a known limitation of stateless JWT

---

## 🎭 Step 9: Test Different User Roles

Create users with different roles and verify their permissions.

### 9.1 Role-Based Access Control

For each role, test:
- SUPER_ADMIN: Full platform access
- OWNER: Full tenant access
- ADMIN: Operational admin access
- COACH: Training and player management
- PLAYER: View own data only
- SCOUT: Scouting reports and watchlists
- MEDICAL: Medical records access

**Test Method:**
1. Create user with specific role (via API or admin panel)
2. Login as that user
3. Try to access different endpoints
4. Verify allowed/denied actions match role permissions

Example - Create a COACH user:

```bash
curl -X POST http://localhost:3001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "coach@manchester-united.com",
    "password": "Coach@123456",
    "firstName": "Erik",
    "lastName": "Ten Hag",
    "role": "COACH",
    "tenantId": "<manchester-united-tenant-id>"
  }'
```

Then test accessing protected endpoints:

```bash
# COACH should be able to view players
curl -X GET http://localhost:3001/players \
  -H "Cookie: accessToken=<coach-token>"

# COACH might not be able to delete players (depending on permissions)
curl -X DELETE http://localhost:3001/players/<player-id> \
  -H "Cookie: accessToken=<coach-token>"
```

**Expected Result:**
- ✅ GET /players: 200 OK
- ✅ DELETE /players: 403 Forbidden (if COACH lacks delete permission)

---

## 📊 Step 10: Test Password Management

### 10.1 Forgot Password Flow

1. Go to: `http://localhost:3000/forgot-password`
2. Enter email: `admin@players-platform.com`
3. Click "Send Reset Link"

**Expected Result:**
- ✅ Message: "If an account exists, a reset link has been sent"
- ⚠️ Check email/console for reset token (development mode)

### 10.2 Reset Password

Get reset token from database:

```sql
SELECT "passwordResetToken" 
FROM users 
WHERE email = 'admin@players-platform.com';
```

Then visit: `http://localhost:3000/reset-password?token=<reset-token>`

1. Enter new password: `NewPassword@123`
2. Confirm password
3. Click "Reset Password"

**Expected Result:**
- ✅ Password updated
- ✅ All existing sessions invalidated
- ✅ Redirected to login page
- ✅ Can login with new password

### 10.3 Change Password (Logged-In User)

1. Login with current password
2. Go to settings/profile
3. Change password form:
   - Current password: `NewPassword@123`
   - New password: `Updated@456`
   - Confirm new password
4. Submit

**Expected Result:**
- ✅ Password changed successfully
- ✅ Can login with new password
- ✅ Old password rejected

---

## ✅ Testing Checklist

Use this checklist to ensure all features work correctly:

### Authentication
- [ ] SUPER_ADMIN can login
- [ ] Tenant admins can login
- [ ] Regular users can login
- [ ] Invalid credentials rejected
- [ ] Account lockout after 5 failed attempts
- [ ] Rate limiting on login endpoint
- [ ] Password visibility toggle works
- [ ] Remember me checkbox functional
- [ ] Auto-redirect after login

### Registration
- [ ] New users can register
- [ ] Password strength indicator works
- [ ] Email validation enforced
- [ ] Tenant ID required
- [ ] Duplicate email rejected
- [ ] Email verification flow works

### Multi-Tenancy
- [ ] Users isolated by tenant
- [ ] Cannot access other tenant data
- [ ] Tenant ID automatically added to queries
- [ ] SUPER_ADMIN can manage all tenants

### Security
- [ ] HTTP-only cookies used for tokens
- [ ] Tokens have correct expiry times
- [ ] Token refresh works seamlessly
- [ ] Logout clears tokens
- [ ] Logout all devices invalidates all sessions
- [ ] 2FA can be enabled/disabled
- [ ] 2FA codes verified correctly

### Authorization
- [ ] Role-based access control enforced
- [ ] Protected routes require authentication
- [ ] Public routes accessible without login
- [ ] Permission checks work correctly
- [ ] Different roles have appropriate access

### Password Management
- [ ] Forgot password sends reset email
- [ ] Reset password with token works
- [ ] Change password for logged-in user works
- [ ] Password change invalidates old sessions
- [ ] Password strength validated

### Error Handling
- [ ] 401 errors trigger auto-logout
- [ ] User-friendly error messages shown
- [ ] Loading states display during API calls
- [ ] Network errors handled gracefully

---

## 🐛 Troubleshooting

### Issue: Cannot login after seeding

**Solution:**
1. Verify database was seeded: `SELECT * FROM users WHERE email = 'admin@players-platform.com';`
2. Check backend is running: `curl http://localhost:3001/health`
3. Clear browser cookies and try again
4. Check browser console for errors

### Issue: Tenant ID not found during registration

**Solution:**
1. Get tenant IDs: `SELECT id, name, slug FROM tenants;`
2. Copy the correct UUID
3. Ensure you're pasting the full UUID (no extra spaces)

### Issue: CORS errors

**Solution:**
1. Check backend CORS configuration in `main.ts`
2. Ensure frontend URL is allowed (usually `http://localhost:3000`)
3. Restart backend after config changes

### Issue: Email verification not working

**Solution (Development):**
1. Manually verify in database: `UPDATE users SET "emailVerifiedAt" = NOW() WHERE email = '...';`
2. Or configure MailService with test SMTP server (Mailhog, Ethereal)

### Issue: 2FA QR code not showing

**Solution:**
1. Check if `qrcode.react` is installed: `npm list qrcode.react`
2. Verify backend returns QR code in response
3. Check browser console for JavaScript errors

---

## 📝 Notes

- **All passwords** in seed script: `Admin@123456`
- **Access token expiry**: 15 minutes
- **Refresh token expiry**: 7 days
- **Account lockout duration**: 30 minutes
- **Rate limit**: 5 requests per minute on login

### Known Limitations

1. **Session Revocation**: Individual session revocation requires token blacklisting (Redis/database). Currently returns informational message.
2. **Email Sending**: May not work in development without SMTP configuration. Manual verification recommended for testing.
3. **Role-Based Frontend Guards**: Handled at page level via `useCurrentUser()` hook rather than middleware for performance.

---

## 🎯 Next Steps

After completing authentication testing:

1. **Implement Tenant Management UI** for SUPER_ADMIN
2. **Add User Management** pages (create/edit users with different roles)
3. **Build Dashboard Pages** specific to each role
4. **Implement Domain Modules** (Players, Contracts, Training, etc.)
5. **Add Comprehensive E2E Tests** using Playwright/Cypress

---

**Happy Testing! 🚀**
