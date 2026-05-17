# Comprehensive Feature Implementation Prompt Template

**IMPORTANT: Copy and paste this ENTIRE template before EVERY feature request to ensure consistent, high-quality implementations following your established architecture and best practices.**

---

## 🎯 FEATURE REQUEST

**Feature Name**: [e.g., "Player Management - Create & Edit Player Profile"]

**Module**: [Backend/Frontend/Both]

**Priority**: [High/Medium/Low]

**Description**: 
[Provide a clear, concise description of what this feature should accomplish in 2-3 sentences]

**User Stories**:
- As a [user role], I want to [action] so that [benefit/value]
- As a [user role], I want to [action] so that [benefit/value]

**Business Value**:
[Explain why this feature is important and what problem it solves]

---

## 📋 REQUIREMENTS

### Functional Requirements
1. [List specific functionality requirements]
2. [Be explicit about expected behavior]
3. [Include edge cases and constraints]

### Non-Functional Requirements
- **Performance**: [e.g., "Load player list in <500ms with pagination"]
- **Security**: [e.g., "Only COACH and ADMIN roles can edit players"]
- **Accessibility**: [e.g., "Full keyboard navigation support"]
- **Responsive Design**: [e.g., "Mobile-first, works on all screen sizes"]

### Acceptance Criteria
- [ ] [Criterion 1 - measurable and testable]
- [ ] [Criterion 2 - measurable and testable]
- [ ] [Criterion 3 - measurable and testable]

---

## 🔧 TECHNICAL SPECIFICATIONS

### Backend API Endpoints (if applicable)
```
METHOD | Path | Description | Auth Required | Roles
-------|------|-------------|---------------|------
GET    | /api/[endpoint] | [Description] | Yes | [Roles]
POST   | /api/[endpoint] | [Description] | Yes | [Roles]
PUT    | /api/[endpoint]/:id | [Description] | Yes | [Roles]
DELETE | /api/[endpoint]/:id | [Description] | Yes | [Roles]
```

### Database Schema Changes (if applicable)
[Describe new models or modifications to existing models]
- New fields, relations, enums
- Indexes needed
- Migration considerations

### Frontend Routes (if applicable)
- `/dashboard/[feature]` - [Page description]
- `/dashboard/[feature]/:id` - [Page description]
- `/dashboard/[feature]/new` - [Page description]

### Expected Data Flow
[Describe how data flows through the system]
1. User action → API call → Business logic → Database → Response → UI update

---

## ✅ ARCHITECTURE COMPLIANCE CHECKLIST

### Backend Architecture (Clean Architecture + DDD)

#### Layer Structure Compliance
- [ ] **Domain Layer**: Pure business logic, NO external dependencies
  - [ ] Entity classes defined in `domain/entities/`
  - [ ] Repository interfaces in `domain/interfaces/`
  - [ ] No imports from infrastructure/presentation layers
  
- [ ] **Application Layer**: Business orchestration
  - [ ] Use cases in `application/use-cases/` with single `execute()` method
  - [ ] One use case per operation (CreateX, GetX, UpdateX, DeleteX)
  - [ ] Inject repository INTERFACES (not implementations)
  - [ ] Emit domain events for cross-module communication
  
- [ ] **Infrastructure Layer**: Technical implementations
  - [ ] Repository implementations in `infrastructure/repositories/`
  - [ ] Implements domain interfaces
  - [ ] Uses PrismaService (no direct Prisma calls in use cases)
  - [ ] NO manual tenantId in queries (middleware handles it)
  
- [ ] **Presentation Layer**: HTTP/WebSocket endpoints
  - [ ] Controllers are THIN (delegate to use cases only)
  - [ ] DTOs with class-validator decorators
  - [ ] Swagger annotations (@ApiTags, @ApiOperation, @ApiResponse)
  - [ ] Role-based access control (@Roles decorator)

#### Multi-Tenancy (CRITICAL)
- [ ] All database queries automatically scoped by tenantId via middleware
- [ ] NEVER manually add `where: { tenantId }` in Prisma queries
- [ ] Extract tenant from request: `req.tenantId` (set by TenantGuard)
- [ ] All models have `tenantId String @db.Uuid` field
- [ ] Composite unique constraint: `@@unique([id, tenantId])`
- [ ] Proper indexes: `@@index([tenantId])`

#### Security & Authorization
- [ ] Global JWT guard protects ALL routes by default
- [ ] Use `@Public()` ONLY for auth endpoints (login, register, forgot-password)
- [ ] Apply `@Roles(UserRole.ADMIN, UserRole.COACH, ...)` for role-based access
- [ ] Available roles: SUPER_ADMIN, OWNER, ADMIN, SPORTING_DIRECTOR, SCOUT, COACH, ASSISTANT_COACH, GOALKEEPER_COACH, FITNESS_COACH, MEDICAL, PHYSIOTHERAPIST, LEGAL, FINANCE_MANAGER, PERFORMANCE_ANALYST, VIDEO_ANALYST, TRAINING_MANAGER, PLAYER, GUARDIAN
- [ ] Permission-based access using `@RequirePermissions('player.create')` when needed
- [ ] Input validation via DTO decorators (whitelist enabled globally)

#### Error Handling
- [ ] Throw NestJS built-in exceptions:
  - `UnauthorizedException` - Invalid credentials/token
  - `ForbiddenException` - Insufficient permissions
  - `NotFoundException` - Resource not found
  - `ConflictException` - Duplicate resource
  - `BadRequestException` - Invalid input
- [ ] HttpExceptionFilter catches all exceptions automatically
- [ ] TransformInterceptor wraps responses in standard format

#### Response Format (AUTOMATIC)
```json
{
  "statusCode": 201,
  "message": "Success",
  "data": { },
  "timestamp": "2026-05-10T12:00:00.000Z"
}
```
- [ ] NEVER manually format responses in controllers

#### File Naming Conventions
- [ ] Use cases: `<action>-<entity>.usecase.ts` (e.g., `create-player.usecase.ts`)
- [ ] Repositories: `<entity>.repository.ts`
- [ ] Controllers: `<entities>.controller.ts` (plural)
- [ ] DTOs: `<action>-<entity>.dto.ts` (e.g., `create-player.dto.ts`)
- [ ] Entities: `<entity>.entity.ts`
- [ ] Interfaces: `<entity>-repository.interface.ts`

---

### Frontend Architecture (Next.js 16 + React Query + Feature-Sliced)

#### Feature-Sliced Structure
- [ ] Create feature folder: `src/features/[feature-name]/`
- [ ] Standard subfolder structure:
  ```
  [feature-name]/
  ├── api/          # API service layer
  ├── hooks/        # Custom React Query hooks
  ├── types/        # TypeScript interfaces
  ├── components/   # Reusable feature components (optional)
  └── index.ts      # Barrel export
  ```
- [ ] NO cross-feature imports (only import from `@/shared/*`)
- [ ] Barrel export in `index.ts` exports all public APIs

#### Type Safety First
- [ ] Define TypeScript interfaces in `types/[feature].types.ts`
- [ ] Match backend response structures EXACTLY
- [ ] Use existing shared types: `BaseEntity`, `ApiResponse`, `PaginatedResponse`
- [ ] ZERO `any` types allowed - everything must be typed
- [ ] Export types from feature's `index.ts`

#### API Layer Pattern
- [ ] Create API service: `api/[feature].api.ts`
- [ ] Use singleton `apiClient` (NEVER create new axios instances)
- [ ] All methods return `Promise<ApiResponse<T>>`
- [ ] Include JSDoc comments for each method
- [ ] Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- [ ] Handle pagination parameters if listing data
- [ ] Cookie-based authentication (HTTP-only cookies, NOT localStorage)

#### Custom Hooks Pattern (React Query)
- [ ] Create hooks: `hooks/use-[feature].ts`
- [ ] Mark with `'use client'` directive
- [ ] Use React Query for ALL server state (`useQuery`, `useMutation`)
- [ ] Use centralized `queryKeys` from `@/shared/lib/query-keys`
- [ ] Add query keys to `query-keys.ts` if not present
- [ ] Handle cache invalidation on mutations:
  ```typescript
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.[feature].lists() });
  }
  ```
- [ ] Include proper `enabled` conditions for conditional queries
- [ ] Return typed results from hooks

#### Component Architecture
- [ ] Pages are Server Components by default (add `'use client'` ONLY when needed)
- [ ] Pages are THIN - delegate logic to hooks (max 100 lines)
- [ ] Use existing UI components from `@/shared/ui/` (Button, Input, Label, etc.)
- [ ] Create feature-specific components in `components/` folder if reusable
- [ ] Use `cn()` utility for className merging
- [ ] Implement loading states (use `LoadingSpinner` or skeletons)
- [ ] Implement error states (display user-friendly messages)
- [ ] Implement empty states (use `EmptyState` component)
- [ ] Forms use `react-hook-form` + `zod` validation
- [ ] Buttons show loading state during mutations

#### State Management
- [ ] Server state → React Query (data fetching, caching, synchronization)
- [ ] Client state → React local state (`useState`) or form state
- [ ] NO localStorage for sensitive data (tokens handled via HTTP-only cookies)
- [ ] Use `useAuth()` for authentication state
- [ ] Invalidate relevant queries after mutations

#### Routing & Navigation
- [ ] Add route constants to `ROUTES` in `@/shared/lib/constants.ts`
- [ ] Use Next.js App Router file structure: `app/(dashboard)/[feature]/page.tsx`
- [ ] Use `useRouter()` for programmatic navigation
- [ ] Use `<Link>` for declarative navigation
- [ ] Protected routes automatically handled by middleware

#### Error Handling
- [ ] Display mutation errors in UI (user-friendly messages)
- [ ] Handle API errors gracefully (ApiError class from api-client)
- [ ] Form validation errors displayed inline
- [ ] Network errors caught and displayed
- [ ] Auto-logout on 401 (handled by api-client interceptor)

#### Performance Optimization
- [ ] Use appropriate `staleTime` for queries (default: 5 minutes)
- [ ] Implement pagination for large lists (use `PAGINATION.DEFAULT_PAGE_SIZE`)
- [ ] Lazy load heavy components with `next/dynamic` if needed
- [ ] Avoid unnecessary re-renders (proper dependency arrays)
- [ ] Use React Query caching effectively

#### Accessibility & UX
- [ ] Use semantic HTML elements
- [ ] Include ARIA labels where needed
- [ ] Keyboard navigation support
- [ ] Focus management for forms
- [ ] Responsive design (mobile-first approach)
- [ ] Loading indicators for async operations
- [ ] Success/error feedback for user actions (toast notifications)

---

## 🚀 IMPLEMENTATION STEPS

### For Backend Features:

#### Step 1: Database Schema (if needed)
**File**: `backend/prisma/schema.prisma`
- Add model with `tenantId`, timestamps, soft delete
- Add composite unique constraint: `@@unique([id, tenantId])`
- Add indexes: `@@index([tenantId])`, relevant field indexes
- Run: `npx prisma migrate dev --name <description>` then `npx prisma generate`

#### Step 2: Domain Layer
**Files**: 
- `src/modules/[module]/domain/entities/[entity].entity.ts`
- `src/modules/[module]/domain/interfaces/[entity]-repository.interface.ts`

Pure business objects with NO external dependencies.

#### Step 3: Infrastructure Layer
**File**: `src/modules/[module]/infrastructure/repositories/[entity].repository.ts`
- Implement repository interface
- Use PrismaService for database operations
- Map Prisma models to domain entities
- NO manual tenantId filtering (middleware handles it)

#### Step 4: Application Layer
**Files**: `src/modules/[module]/application/use-cases/*.usecase.ts`
- Create use case classes with single `execute()` method
- Inject repository INTERFACES (not implementations)
- Handle business rules, transactions, domain events
- Throw appropriate NestJS exceptions

#### Step 5: Presentation Layer
**Files**:
- `src/modules/[module]/presentation/dto/*.dto.ts`
- `src/modules/[module]/presentation/[entities].controller.ts`

DTOs with class-validator decorators. Controllers delegate to use cases.

#### Step 6: Module Definition
**File**: `src/modules/[module]/[module].module.ts`
- Register providers with dependency injection
- Provide repository interface with implementation
- Export repositories if other modules need them
- Import required modules (PrismaModule, etc.)

#### Step 7: App Module Registration
**File**: `src/app.module.ts`
- Import module in imports array

---

### For Frontend Features:

#### Step 1: Define Types
**File**: `src/features/[feature]/types/[feature].types.ts`
```typescript
import { BaseEntity } from '@/shared/types';

export interface [Entity] extends BaseEntity {
  // fields matching backend response
}

export interface Create[Entity]Payload {
  // creation fields
}

export interface Update[Entity]Payload extends Partial<Create[Entity]Payload> {}

export interface [Entity]Filters {
  // filter fields for list queries
}
```

#### Step 2: Create API Service
**File**: `src/features/[feature]/api/[feature].api.ts`
```typescript
import { apiClient } from '@/shared/lib/api-client';
import type { ApiResponse, PaginatedResponse, ListQueryParams } from '@/shared/types';
import type { [Entity], Create[Entity]Payload, Update[Entity]Payload, [Entity]Filters } from '../types/[feature].types';

export const [feature]Api = {
  getList: (params: ListQueryParams & { filters?: [Entity]Filters }): Promise<ApiResponse<PaginatedResponse<[Entity]>>> => {
    return apiClient.get('/[endpoint]', { params });
  },

  getById: (id: string): Promise<ApiResponse<[Entity]>> => {
    return apiClient.get(`/[endpoint]/${id}`);
  },

  create: (data: Create[Entity]Payload): Promise<ApiResponse<[Entity]>> => {
    return apiClient.post('/[endpoint]', data);
  },

  update: (id: string, data: Update[Entity]Payload): Promise<ApiResponse<[Entity]>> => {
    return apiClient.put(`/[endpoint]/${id}`, data);
  },

  delete: (id: string): Promise<ApiResponse<void>> => {
    return apiClient.delete(`/[endpoint]/${id}`);
  },
};
```

#### Step 3: Update Query Keys
**File**: `src/shared/lib/query-keys.ts`
```typescript
export const queryKeys = {
  // ... existing keys
  
  [feature]: {
    all: ['[feature]'] as const,
    lists: () => [...queryKeys.[feature].all, 'list'] as const,
    list: (filters: Record<string, unknown>) => [...queryKeys.[feature].lists(), filters] as const,
    details: () => [...queryKeys.[feature].all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.[feature].details(), id] as const,
  },
} as const;
```

#### Step 4: Create Custom Hooks
**File**: `src/features/[feature]/hooks/use-[feature].ts`
```typescript
'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { [feature]Api } from '../api/[feature].api';
import { queryKeys } from '@/shared/lib/query-keys';
import type { ListQueryParams, [Entity]Filters } from '@/shared/types';

export function use[Entity]List(params: ListQueryParams & { filters?: [Entity]Filters }) {
  return useQuery({
    queryKey: queryKeys.[feature].list(params),
    queryFn: async () => {
      const response = await [feature]Api.getList(params);
      return response.data;
    },
  });
}

export function use[Entity](id: string) {
  return useQuery({
    queryKey: queryKeys.[feature].detail(id),
    queryFn: async () => {
      const response = await [feature]Api.getById(id);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreate[Entity]() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: [feature]Api.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.[feature].lists() });
    },
  });
}

export function useUpdate[Entity](id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => [feature]Api.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.[feature].detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.[feature].lists() });
    },
  });
}

export function useDelete[Entity]() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: [feature]Api.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.[feature].lists() });
    },
  });
}
```

#### Step 5: Update Barrel Export
**File**: `src/features/[feature]/index.ts`
```typescript
export * from './api/[feature].api';
export * from './hooks/use-[feature]';
export * from './types/[feature].types';
```

#### Step 6: Create Page Component
**File**: `app/(dashboard)/[feature]/page.tsx`
- Server Component by default (add `'use client'` only if needed)
- Thin page - delegate to hooks
- Use existing UI components
- Handle loading, error, empty states
- Implement search/filter if needed
- Pagination for lists

#### Step 7: Add Route Constants (if needed)
**File**: `src/shared/lib/constants.ts`
```typescript
export const ROUTES = {
  // ... existing routes
  
  [FEATURE]: '/dashboard/[feature]',
  [FEATURE]_DETAIL: (id: string) => `/dashboard/[feature]/${id}`,
  [FEATURE]_NEW: '/dashboard/[feature]/new',
} as const;
```

---

## 🔍 PRE-IMPLEMENTATION VERIFICATION

Before starting implementation, answer these questions:

### Backend
1. **Does this feature already exist partially?**
   - Check existing modules in `backend/src/modules/`
   - Reuse existing code if present
   
2. **Are database changes needed?**
   - Review `prisma/schema.prisma` for existing models
   - Plan migrations carefully
   - Consider backward compatibility

3. **What dependencies are needed?**
   - Check `package.json` for available libraries
   - Use existing dependencies (don't add new ones unless necessary)
   - Current stack: NestJS, Prisma, JWT, Passport, class-validator, Swagger

4. **What existing patterns should I follow?**
   - Review `backend/src/modules/auth/` as reference implementation
   - Check similar features for consistency
   - Follow naming conventions exactly

5. **Cross-module communication needed?**
   - Use domain events (EventEmitter2) for decoupled communication
   - Avoid circular dependencies between modules

### Frontend
1. **Does this feature already exist partially?**
   - Check `src/features/` for existing folders
   - Check `app/` for existing pages
   - Reuse existing code if present

2. **Are backend endpoints ready?**
   - Confirm API endpoints exist and are documented
   - Test endpoints with curl/Postman first
   - Verify response structure matches expected types

3. **What dependencies are needed?**
   - Check `package.json` for available libraries
   - Use existing dependencies (don't add new ones unless necessary)
   - Current stack: React Query, Axios, React Hook Form, Zod, Radix UI, Lucide icons

4. **What existing patterns should I follow?**
   - Review `src/features/auth/` as reference implementation
   - Check similar features for consistency
   - Follow naming conventions exactly

5. **What shared utilities can I reuse?**
   - `cn()` for className merging
   - `formatDate()` for date formatting
   - Existing UI components (Button, Input, Label)
   - Shared components (LoadingSpinner, EmptyState)

---

## 🚫 COMMON MISTAKES TO AVOID

### Backend
❌ **DON'T**:
- Put business logic in controllers
- Call Prisma directly in use cases (use repositories)
- Manually add `tenantId` to queries (middleware does it)
- Inject repository implementation (inject interface)
- Skip DTO validation decorators
- Forget `@Roles()` decorator for authorization
- Create circular dependencies between modules (use events instead)
- Hardcode tenantId (always use `req.tenantId`)
- Return custom response format (TransformInterceptor handles it)
- Forget to add module to `app.module.ts` imports
- Use `any` types in TypeScript
- Store passwords in plaintext (use PasswordService with bcrypt/argon2)
- Expose sensitive data in responses (filter in use case/repository)

✅ **DO**:
- Follow Clean Architecture layers strictly
- Use repository pattern for data access
- Let middleware handle tenant isolation
- Inject interfaces, not implementations
- Validate all inputs with class-validator
- Apply role-based access control
- Use domain events for cross-module communication
- Extract tenant from request context
- Let interceptors handle response formatting
- Register modules properly
- Type everything with TypeScript
- Hash passwords securely
- Return only necessary data

### Frontend
❌ **DON'T**:
- Create new axios instances (use `apiClient`)
- Store tokens in localStorage (use HTTP-only cookies)
- Use `any` types (define proper interfaces)
- Put business logic in pages (use hooks)
- Skip error handling
- Forget to invalidate cache after mutations
- Import directly from deep paths (use barrel exports)
- Create duplicate types (reuse shared types)
- Hardcode route strings (use `ROUTES` constant)
- Forget `'use client'` directive for client hooks
- Fetch data in components (use React Query in hooks)
- Mutate state directly (use proper React patterns)
- Ignore accessibility (semantic HTML, ARIA labels)
- Skip loading/error/empty states

✅ **DO**:
- Follow feature-sliced structure exactly
- Use React Query for all server state
- Type everything with TypeScript
- Handle loading, error, and empty states
- Invalidate cache on mutations
- Use existing UI components
- Add JSDoc comments
- Test the feature manually before marking complete
- Update barrel exports
- Follow naming conventions
- Use cookie-based authentication
- Keep pages thin (<100 lines)
- Implement proper error boundaries
- Ensure mobile responsiveness
- Follow accessibility best practices

---

## 📊 QUALITY ASSURANCE CHECKLIST

After implementation, verify ALL items:

### Backend QA
- [ ] TypeScript compilation passes (`npm run build`)
- [ ] No ESLint errors (`npm run lint`)
- [ ] All layers follow dependency rule (Domain → Application → Infrastructure → Presentation)
- [ ] Controllers are thin (only delegate to use cases)
- [ ] Use cases inject repository interfaces
- [ ] All DTOs validated with class-validator
- [ ] Routes protected with @Roles() decorators
- [ ] Swagger annotations present on all endpoints
- [ ] Module registered in app.module.ts
- [ ] No manual tenantId in queries (middleware handles it)
- [ ] Proper error handling (throw NestJS exceptions)
- [ ] Domain events emitted for cross-module communication
- [ ] Response format consistent (TransformInterceptor)
- [ ] Database migrations created and applied
- [ ] Indexes added for performance
- [ ] Soft deletes implemented (deletedAt field)

### Frontend QA
- [ ] TypeScript compilation passes (`npm run build`)
- [ ] No ESLint errors (`npm run lint`)
- [ ] Feature loads without errors
- [ ] All CRUD operations work correctly
- [ ] Error messages are user-friendly
- [ ] Loading states display properly
- [ ] Empty states show when appropriate
- [ ] Mobile responsive design works
- [ ] Cache invalidation works (data updates after mutations)
- [ ] Navigation works correctly
- [ ] Authentication required (if protected route)
- [ ] No console errors or warnings
- [ ] Accessibility basics covered (labels, keyboard nav)
- [ ] Forms validate with Zod schemas
- [ ] No `any` types used
- [ ] Barrel exports updated
- [ ] Route constants added to ROUTES
- [ ] Query keys added to queryKeys

### Integration QA
- [ ] Backend and frontend communicate correctly
- [ ] API response types match frontend expectations
- [ ] Authentication flow works end-to-end
- [ ] Authorization enforced on both backend and frontend
- [ ] Error handling consistent across stack
- [ ] Multi-tenancy isolation working
- [ ] Performance acceptable (load times <500ms for typical operations)
- [ ] No security vulnerabilities (input validation, XSS protection, CSRF protection)

---

## 🎨 UI/UX GUIDELINES (Frontend)

### Styling
- Use Tailwind CSS utility classes exclusively
- Follow existing color scheme (primary, secondary, destructive, muted, etc.)
- Maintain consistent spacing (use Tailwind scale: 1, 2, 3, 4, 6, 8, 12, 16)
- Ensure dark mode compatibility (test with dark theme)
- Use CSS variables for theme colors

### Components
- Use Radix UI primitives for accessibility (Dialog, DropdownMenu, Select, etc.)
- Apply CVA (Class Variance Authority) variants for consistency
- Keep components composable and reusable
- Follow compound component pattern when appropriate

### Forms
- Validate with Zod schemas (client-side)
- Show inline validation errors (below each field)
- Disable submit button during submission
- Show success/error feedback (toast notifications)
- Reset form after successful submission
- Preserve form state on validation errors

### Tables/Lists
- Show loading skeleton while fetching
- Display empty state when no data
- Implement pagination for large datasets (>20 items)
- Provide search/filter functionality
- Sortable columns where applicable
- Row actions (edit, delete) in dropdown menu

### Feedback
- Toast notifications for success/error (use sonner or similar)
- Inline errors for form validation
- Loading spinners for async operations
- Skeleton loaders for content placeholders
- Progress indicators for multi-step processes

---

## 📚 REFERENCE FILES

Study these files as examples of best practices:

### Backend References
- **Auth Module**: `backend/src/modules/auth/` (complete implementation)
  - Use Cases: `application/use-cases/login.usecase.ts`
  - Repository: `infrastructure/repositories/user.repository.ts`
  - Controller: `presentation/auth.controller.ts`
  - DTOs: `presentation/dto/login.dto.ts`
- **Prisma Service**: `backend/src/infrastructure/prisma/prisma.service.ts`
- **Guards**: `backend/src/common/guards/jwt-auth.guard.ts`, `roles.guard.ts`
- **Decorators**: `backend/src/common/decorators/*.decorator.ts`
- **Interceptors**: `backend/src/common/interceptors/transform.interceptor.ts`
- **Module Template**: `backend/src/modules/auth/auth.module.ts`

### Frontend References
- **Auth Feature**: `frontend/src/features/auth/` (complete implementation)
  - API: `api/auth.api.ts`
  - Hooks: `hooks/use-auth.ts`
  - Types: `types/auth.types.ts`
- **API Client**: `frontend/src/shared/lib/api-client.ts` (interceptors, error handling)
- **Query Keys**: `frontend/src/shared/lib/query-keys.ts` (cache management)
- **UI Components**: `frontend/src/shared/ui/button.tsx` (CVA pattern)
- **Login Page**: `frontend/app/(auth)/login/page.tsx` (form pattern)
- **Dashboard Layout**: `frontend/app/(dashboard)/layout.tsx` (layout structure)
- **Constants**: `frontend/src/shared/lib/constants.ts` (routes, config)

---

## 💡 PRO TIPS

### General
1. **Start with types** - Define your data structures first (backend entities, frontend interfaces)
2. **Build bottom-up** - Database → Domain → Application → Presentation (backend); Types → API → Hooks → Components → Page (frontend)
3. **Reuse aggressively** - Don't reinvent existing patterns, check auth module first
4. **Test as you go** - Verify each layer before moving to next
5. **Keep it simple** - Avoid over-engineering, follow KISS principle
6. **Comment complex logic** - Explain WHY, not WHAT
7. **Think about edge cases** - Empty states, errors, loading, race conditions
8. **Consider scalability** - Will this work with 1000+ items? 100+ concurrent users?
9. **Plan for maintenance** - Clear naming, separation of concerns, documentation
10. **Follow the standards** - Consistency is key across the entire codebase

### Backend Specific
1. **Domain-driven design** - Keep business logic in domain layer
2. **Dependency inversion** - Depend on abstractions (interfaces), not concretions
3. **Single responsibility** - One use case per operation
4. **Open/closed principle** - Extend via new use cases, don't modify existing ones
5. **Interface segregation** - Small, focused repository interfaces
6. **Transaction management** - Use Prisma transactions for multi-step operations
7. **Event-driven architecture** - Decouple modules with domain events
8. **Security first** - Validate, sanitize, authorize at every layer
9. **Performance optimization** - Add indexes, use pagination, avoid N+1 queries
10. **Logging** - Add meaningful logs for debugging and monitoring

### Frontend Specific
1. **Server state vs client state** - React Query for server, useState for client
2. **Optimistic updates** - Update UI immediately, rollback on error
3. **Debouncing** - Debounce search inputs (300-500ms)
4. **Memoization** - Use useMemo/useCallback for expensive computations
5. **Code splitting** - Lazy load routes and heavy components
6. **Bundle size** - Monitor impact, tree-shake unused code
7. **Accessibility** - Semantic HTML, ARIA labels, keyboard navigation
8. **Progressive enhancement** - Works without JavaScript where possible
9. **SEO considerations** - Server components, meta tags, structured data
10. **Performance monitoring** - Lighthouse scores, Core Web Vitals

---

## 🔄 AFTER IMPLEMENTATION

Once the feature is complete:

### Documentation
1. **Update API documentation** - Swagger auto-generated, verify accuracy
2. **Document deviations** - If you broke patterns, explain why
3. **Note temporary workarounds** - Mark with TODO comments
4. **Suggest future improvements** - Add comments for refactoring opportunities

### Testing
1. **Manual testing** - Test all user flows, edge cases, error scenarios
2. **API testing** - Verify endpoints with Postman/curl
3. **Integration testing** - Test backend-frontend integration
4. **Cross-browser testing** - Chrome, Firefox, Safari, Edge
5. **Mobile testing** - iOS Safari, Android Chrome
6. **Accessibility testing** - axe DevTools, keyboard navigation
7. **Performance testing** - Lighthouse, network throttling

### Code Quality
1. **Run linters** - `npm run lint` (both backend and frontend)
2. **Type checking** - `npm run build` (ensure no TypeScript errors)
3. **Code review** - Self-review against this checklist
4. **Refactor if needed** - Clean up any technical debt
5. **Remove debug code** - Console.logs, temporary comments

### Deployment Preparation
1. **Database migrations** - Ensure migrations are created and tested
2. **Environment variables** - Document any new env vars needed
3. **Configuration updates** - Update config files if needed
4. **Dependency updates** - Note any new packages added
5. **Breaking changes** - Document any breaking changes for other developers

### Communication
1. **Update team** - Notify team of new feature
2. **Share documentation** - Link to API docs, usage examples
3. **Demo** - Show feature to stakeholders if applicable
4. **Gather feedback** - Collect user feedback for improvements

---

## 📝 EXAMPLE: COMPLETE FEATURE REQUEST

Here's how to fill out this template effectively:

```markdown
## 🎯 FEATURE REQUEST

**Feature Name**: Player Management - Create & Edit Player Profile

**Module**: Both (Backend + Frontend)

**Priority**: High

**Description**: 
Implement CRUD operations for player profiles allowing coaches and admins to create, view, edit, and delete player records. Includes form validation, image upload, and role-based access control.

**User Stories**:
- As a coach, I want to create new player profiles so that I can onboard new players to the team
- As an admin, I want to edit existing player information so that I can keep records up-to-date
- As a coach, I want to view detailed player profiles so that I can access all player information in one place
- As an admin, I want to delete player records so that I can remove inactive or duplicate entries

**Business Value**:
Centralized player management reduces administrative overhead, improves data accuracy, and enables better team organization. Essential for core platform functionality.

---

## 📋 REQUIREMENTS

### Functional Requirements
1. Create player with required fields: fullName, dateOfBirth, position, nationality
2. Optional fields: height, weight, footPreference, bio, emergency contact
3. Upload player photo (max 5MB, JPG/PNG)
4. Edit existing player profiles (all fields except ID)
5. Soft delete players (mark as deleted, don't permanently remove)
6. View paginated list of all players with search/filter
7. View single player detail page with all information
8. Only COACH, ASSISTANT_COACH, ADMIN, OWNER roles can create/edit/delete
9. All authenticated users can view player lists and details

### Non-Functional Requirements
- **Performance**: Load player list in <500ms with pagination (20 items per page)
- **Security**: Role-based access control, validate all inputs, sanitize HTML
- **Accessibility**: Full keyboard navigation, screen reader support, proper form labels
- **Responsive Design**: Mobile-first, works on screens 320px to 1920px+

### Acceptance Criteria
- [ ] Create player form validates all required fields
- [ ] Photo upload shows preview before submission
- [ ] Edit form pre-populates with existing data
- [ ] Delete shows confirmation dialog
- [ ] List page displays players in table with sorting
- [ ] Search filters players by name (debounced, 300ms)
- [ ] Detail page shows all player information
- [ ] Unauthorized users see 403 error
- [ ] Mobile layout stacks vertically
- [ ] All operations show loading states
```

[Continue filling out all sections...]

---

## ✨ FINAL REMINDERS

1. **This template is MANDATORY** - Use it for EVERY feature request
2. **Don't skip sections** - Each section serves a purpose
3. **Be specific** - Vague requirements lead to poor implementations
4. **Think ahead** - Consider edge cases, scalability, maintenance
5. **Quality over speed** - Take time to do it right the first time
6. **Consistency matters** - Follow patterns exactly as shown in references
7. **Ask questions** - If requirements are unclear, clarify before implementing
8. **Test thoroughly** - Don't assume it works, verify it works
9. **Document decisions** - Future developers will thank you
10. **Continuous improvement** - Suggest template improvements based on learnings

---

**Remember**: This template exists to ensure consistency, quality, and maintainability across the entire platform. Following it rigorously will result in a codebase that is easy to understand, extend, and maintain. When in doubt, refer to the auth module as the gold standard implementation.
