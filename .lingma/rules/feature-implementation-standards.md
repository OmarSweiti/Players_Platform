---
trigger: always_on
---
# Feature Implementation Standards & Best Practices

**CRITICAL: This rule MUST be followed for ALL feature implementations. Violation of these standards is unacceptable.**

---

## 🎯 Core Principles

1. **Architecture Compliance First**: Never compromise Clean Architecture + DDD principles
2. **Type Safety Always**: ZERO `any` types allowed anywhere in the codebase
3. **Security by Default**: All routes protected unless explicitly marked `@Public()`
4. **Multi-Tenancy Automatic**: NEVER manually add `tenantId` to queries - middleware handles it
5. **Bottom-Up Implementation**: Database → Domain → Application → Presentation (backend); Types → API → Hooks → Components → Page (frontend)
6. **Reuse Over Reinvention**: Always check existing modules (especially `auth/`) before creating new patterns
7. **Testing Responsibility**: User performs all testing - focus on correct implementation only

---

## 🔴 ABSOLUTE PROHIBITIONS (NEVER DO THESE)

### Backend Prohibitions
❌ **NEVER** put business logic in controllers - controllers must ONLY delegate to use cases  
❌ **NEVER** call Prisma directly in use cases - ALWAYS use repository interfaces  
❌ **NEVER** manually add `where: { tenantId }` in Prisma queries - TenantGuard middleware handles this automatically  
❌ **NEVER** inject repository implementations - ALWAYS inject repository INTERFACES  
❌ **NEVER** skip DTO validation decorators - all inputs must be validated with class-validator  
❌ **NEVER** forget `@Roles()` decorator for authorization on protected endpoints  
❌ **NEVER** create circular dependencies between modules - use domain events instead  
❌ **NEVER** hardcode tenantId - always extract from `req.tenantId`  
❌ **NEVER** return custom response format - TransformInterceptor handles standardization automatically  
❌ **NEVER** forget to register module in `app.module.ts` imports array  
❌ **NEVER** store passwords in plaintext - ALWAYS use PasswordService with bcrypt/argon2  
❌ **NEVER** expose sensitive data in responses - filter in use case/repository layer  

### Frontend Prohibitions
❌ **NEVER** create new axios instances - ALWAYS use singleton `apiClient` from `@/shared/lib/api-client`  
❌ **NEVER** store tokens in localStorage - authentication uses HTTP-only cookies only  
❌ **NEVER** use `any` types - define proper TypeScript interfaces for everything  
❌ **NEVER** put business logic in pages - delegate to custom hooks  
❌ **NEVER** skip error handling - handle loading, error, and empty states  
❌ **NEVER** forget to invalidate cache after mutations - use `queryClient.invalidateQueries()`  
❌ **NEVER** import directly from deep paths - ALWAYS use barrel exports from feature's `index.ts`  
❌ **NEVER** create duplicate types - reuse shared types from `@/shared/types`  
❌ **NEVER** hardcode route strings - ALWAYS use `ROUTES` constant from `@/shared/lib/constants`  
❌ **NEVER** forget `'use client'` directive for client-side hooks/components  
❌ **NEVER** fetch data directly in components - use React Query in custom hooks  
❌ **NEVER** mutate state directly - use proper React patterns (useState, useReducer)  
❌ **NEVER** ignore accessibility - semantic HTML, ARIA labels, keyboard navigation required  
❌ **NEVER** skip loading/error/empty states - implement all three for every async operation  

---

## ✅ MANDATORY PATTERNS (ALWAYS FOLLOW)

### Backend Layer Structure (Clean Architecture + DDD)

#### 1. Domain Layer (Pure Business Logic)
```typescript
// Location: src/modules/[module]/domain/entities/[entity].entity.ts
// Rules:
- NO external dependencies (no Prisma, no NestJS, no infrastructure imports)
- Pure TypeScript classes/interfaces
- Contains business rules and validations
- Defines repository interfaces in domain/interfaces/
```

#### 2. Application Layer (Business Orchestration)
```typescript
// Location: src/modules/[module]/application/use-cases/[action]-[entity].usecase.ts
// Rules:
- ONE use case per operation (CreateX, GetX, UpdateX, DeleteX)
- Single execute() method as entry point
- Inject repository INTERFACES (not implementations) via constructor
- Handle transactions, business rules, domain events
- Throw appropriate NestJS exceptions (UnauthorizedException, ForbiddenException, etc.)
- NO direct Prisma calls - use repository interface methods
```

#### 3. Infrastructure Layer (Technical Implementation)
```typescript
// Location: src/modules/[module]/infrastructure/repositories/[entity].repository.ts
// Rules:
- Implements domain repository interface
- Uses PrismaService for database operations
- Maps Prisma models to domain entities
- NO manual tenantId filtering (middleware adds it automatically)
- Handle soft deletes (deletedAt field)
- Add proper indexes for performance
```

#### 4. Presentation Layer (HTTP/WebSocket Endpoints)
```typescript
// Location: src/modules/[module]/presentation/[entities].controller.ts
// Rules:
- Controllers are THIN - only delegate to use cases
- DTOs with class-validator decorators (@IsString, @IsEmail, etc.)
- Swagger annotations (@ApiTags, @ApiOperation, @ApiResponse)
- Role-based access control (@Roles(UserRole.ADMIN, ...))
- Permission-based access (@RequirePermissions('player.create')) when needed
- NO business logic - delegate everything to use cases
```

### Multi-Tenancy Implementation (CRITICAL)
```prisma
// Schema requirements for ALL models:
model Example {
  id        String   @id @default(uuid()) @db.Uuid
  tenantId  String   @db.Uuid  // REQUIRED
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  deletedAt DateTime? // Soft delete support
  
  @@unique([id, tenantId])  // Composite unique constraint
  @@index([tenantId])       // Index for tenant queries
}
```

**Middleware Behavior:**
- TenantGuard extracts tenant from JWT token or request context
- Sets `req.tenantId` automatically
- Prisma middleware adds `where: { tenantId }` to ALL queries
- Developers NEVER manually filter by tenantId

### Security & Authorization
```typescript
// Global JWT guard protects ALL routes by default
// Use @Public() ONLY for:
- Login endpoint
- Register endpoint  
- Forgot password endpoint
- Reset password endpoint
- Email verification endpoint

// Apply @Roles() for role-based access:
@Roles(UserRole.ADMIN, UserRole.COACH, UserRole.SPORTING_DIRECTOR)

// Available roles:
SUPER_ADMIN, OWNER, ADMIN, SPORTING_DIRECTOR, SCOUT, COACH, 
ASSISTANT_COACH, GOALKEEPER_COACH, FITNESS_COACH, MEDICAL, 
PHYSIOTHERAPIST, LEGAL, FINANCE_MANAGER, PERFORMANCE_ANALYST, 
VIDEO_ANALYST, TRAINING_MANAGER, PLAYER, GUARDIAN

// Permission-based access (granular):
@RequirePermissions('player.create', 'player.edit')
```

### Error Handling Pattern
```typescript
// Throw NestJS built-in exceptions:
throw new UnauthorizedException('Invalid credentials');
throw new ForbiddenException('Insufficient permissions');
throw new NotFoundException('Player not found');
throw new ConflictException('Player already exists');
throw new BadRequestException('Invalid input data');

// HttpExceptionFilter catches all exceptions automatically
// TransformInterceptor wraps responses in standard format:
{
  "statusCode": 201,
  "message": "Success",
  "data": { },
  "timestamp": "2026-05-10T12:00:00.000Z"
}
```

### File Naming Conventions (STRICT)
```
Backend:
- Use cases: <action>-<entity>.usecase.ts (e.g., create-player.usecase.ts)
- Repositories: <entity>.repository.ts
- Controllers: <entities>.controller.ts (plural, e.g., players.controller.ts)
- DTOs: <action>-<entity>.dto.ts (e.g., create-player.dto.ts)
- Entities: <entity>.entity.ts
- Interfaces: <entity>-repository.interface.ts

Frontend:
- API service: [feature].api.ts
- Custom hooks: use-[feature].ts
- Types: [feature].types.ts
- Components: PascalCase.tsx (e.g., PlayerCard.tsx)
- Pages: page.tsx (Next.js App Router)
```

---

### Frontend Feature-Sliced Architecture

#### Standard Feature Structure
```
src/features/[feature-name]/
├── api/              # API service layer (singleton apiClient)
│   └── [feature].api.ts
├── hooks/            # Custom React Query hooks
│   └── use-[feature].ts
├── types/            # TypeScript interfaces
│   └── [feature].types.ts
├── components/       # Reusable feature components (optional)
│   └── [Component].tsx
└── index.ts          # Barrel export (REQUIRED)
```

#### Type Safety Requirements
```typescript
// Define TypeScript interfaces matching backend response EXACTLY
import { BaseEntity } from '@/shared/types';

export interface Player extends BaseEntity {
  fullName: string;
  dateOfBirth: Date;
  position: string;
  // ... all fields from backend
}

export interface CreatePlayerPayload {
  fullName: string;
  dateOfBirth: string; // ISO string for forms
  position: string;
  // ... creation fields
}

export interface UpdatePlayerPayload extends Partial<CreatePlayerPayload> {}

// ZERO 'any' types allowed - everything must be typed
```

#### API Service Pattern
```typescript
import { apiClient } from '@/shared/lib/api-client';
import type { ApiResponse, PaginatedResponse, ListQueryParams } from '@/shared/types';

export const playerApi = {
  getList: (params: ListQueryParams): Promise<ApiResponse<PaginatedResponse<Player>>> => {
    return apiClient.get('/players', { params });
  },

  getById: (id: string): Promise<ApiResponse<Player>> => {
    return apiClient.get(`/players/${id}`);
  },

  create: (data: CreatePlayerPayload): Promise<ApiResponse<Player>> => {
    return apiClient.post('/players', data);
  },

  update: (id: string, data: UpdatePlayerPayload): Promise<ApiResponse<Player>> => {
    return apiClient.put(`/players/${id}`, data);
  },

  delete: (id: string): Promise<ApiResponse<void>> => {
    return apiClient.delete(`/players/${id}`);
  },
};
```

**Rules:**
- Use singleton `apiClient` (NEVER create new axios instances)
- All methods return `Promise<ApiResponse<T>>`
- Include JSDoc comments for each method
- Cookie-based authentication (HTTP-only cookies, NOT localStorage)

#### Custom Hooks Pattern (React Query)
```typescript
'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { playerApi } from '../api/player.api';
import { queryKeys } from '@/shared/lib/query-keys';

export function usePlayerList(params: ListQueryParams) {
  return useQuery({
    queryKey: queryKeys.players.list(params),
    queryFn: async () => {
      const response = await playerApi.getList(params);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function usePlayer(id: string) {
  return useQuery({
    queryKey: queryKeys.players.detail(id),
    queryFn: async () => {
      const response = await playerApi.getById(id);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreatePlayer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: playerApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.players.lists() });
    },
  });
}

export function useUpdatePlayer(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => playerApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.players.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.players.lists() });
    },
  });
}

export function useDeletePlayer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: playerApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.players.lists() });
    },
  });
}
```

**Rules:**
- Mark with `'use client'` directive
- Use React Query for ALL server state
- Use centralized `queryKeys` from `@/shared/lib/query-keys`
- Add query keys to `query-keys.ts` if not present
- Handle cache invalidation on mutations
- Include proper `enabled` conditions for conditional queries
- Return typed results from hooks

#### Component Architecture
```typescript
// Pages are Server Components by default (add 'use client' ONLY when needed)
// Pages are THIN - delegate logic to hooks (max 100 lines)

import { usePlayerList } from '@/features/players/hooks/use-players';
import { LoadingSpinner } from '@/shared/ui/loading-spinner';
import { EmptyState } from '@/shared/components/empty-state';

export default function PlayersPage() {
  const { data, isLoading, error } = usePlayerList({ page: 1, limit: 20 });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <div>Error: {error.message}</div>;
  if (!data?.items.length) return <EmptyState message="No players found" />;

  return (
    <div>
      {/* Render player list */}
    </div>
  );
}
```

**Rules:**
- Use existing UI components from `@/shared/ui/` (Button, Input, Label, etc.)
- Use `cn()` utility for className merging
- Implement loading states (use `LoadingSpinner` or skeletons)
- Implement error states (display user-friendly messages)
- Implement empty states (use `EmptyState` component)
- Forms use `react-hook-form` + `zod` validation
- Buttons show loading state during mutations

#### State Management Rules
- **Server state** → React Query (data fetching, caching, synchronization)
- **Client state** → React local state (`useState`) or form state
- **NO localStorage** for sensitive data (tokens handled via HTTP-only cookies)
- Use `useAuth()` for authentication state
- Invalidate relevant queries after mutations

#### Routing & Navigation
```typescript
// Add route constants to ROUTES in @/shared/lib/constants.ts
export const ROUTES = {
  PLAYERS: '/dashboard/players',
  PLAYER_DETAIL: (id: string) => `/dashboard/players/${id}`,
  PLAYER_NEW: '/dashboard/players/new',
} as const;

// Use Next.js App Router file structure:
// app/(dashboard)/players/page.tsx
// app/(dashboard)/players/[id]/page.tsx
// app/(dashboard)/players/new/page.tsx

// Use useRouter() for programmatic navigation
// Use <Link> for declarative navigation
// Protected routes automatically handled by middleware
```

---

## 🔍 PRE-IMPLEMENTATION VERIFICATION (MANDATORY)

Before starting ANY implementation, verify:

### Backend Checklist
1. ✅ Does this feature already exist partially? Check `backend/src/modules/`
2. ✅ Are database changes needed? Review `prisma/schema.prisma`
3. ✅ What dependencies are needed? Check `package.json` - reuse existing
4. ✅ What existing patterns should I follow? Review `backend/src/modules/auth/`
5. ✅ Cross-module communication needed? Use domain events (EventEmitter2)

### Frontend Checklist
1. ✅ Does this feature already exist partially? Check `src/features/` and `app/`
2. ✅ Are backend endpoints ready? Confirm API endpoints exist and documented
3. ✅ What dependencies are needed? Check `package.json` - reuse existing
4. ✅ What existing patterns should I follow? Review `src/features/auth/`
5. ✅ What shared utilities can I reuse? `cn()`, `formatDate()`, UI components

---

## 📊 QUALITY ASSURANCE CHECKLIST (VERIFY BEFORE COMPLETION)

### Backend QA (ALL Must Pass)
- [ ] TypeScript compilation passes (`npm run build`)
- [ ] No ESLint errors (`npm run lint`)
- [ ] All layers follow dependency rule (Domain → Application → Infrastructure → Presentation)
- [ ] Controllers are thin (only delegate to use cases)
- [ ] Use cases inject repository interfaces (not implementations)
- [ ] All DTOs validated with class-validator decorators
- [ ] Routes protected with @Roles() decorators
- [ ] Swagger annotations present on all endpoints
- [ ] Module registered in app.module.ts imports array
- [ ] NO manual tenantId in queries (middleware handles it)
- [ ] Proper error handling (throw NestJS exceptions)
- [ ] Domain events emitted for cross-module communication
- [ ] Response format consistent (TransformInterceptor handles it)
- [ ] Database migrations created and applied
- [ ] Indexes added for performance
- [ ] Soft deletes implemented (deletedAt field)
- [ ] File naming conventions followed exactly

### Frontend QA (ALL Must Pass)
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
- [ ] NO `any` types used
- [ ] Barrel exports updated in feature's index.ts
- [ ] Route constants added to ROUTES
- [ ] Query keys added to queryKeys
- [ ] File naming conventions followed exactly

### Integration QA (ALL Must Pass)
- [ ] Backend and frontend communicate correctly
- [ ] API response types match frontend expectations exactly
- [ ] Authentication flow works end-to-end
- [ ] Authorization enforced on both backend and frontend
- [ ] Error handling consistent across stack
- [ ] Multi-tenancy isolation working
- [ ] Performance acceptable (load times <500ms for typical operations)
- [ ] No security vulnerabilities (input validation, XSS protection, CSRF protection)

---

## 🎨 UI/UX STANDARDS (Frontend)

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
- Toast notifications for success/error
- Inline errors for form validation
- Loading spinners for async operations
- Skeleton loaders for content placeholders
- Progress indicators for multi-step processes

---

## 💡 IMPLEMENTATION WORKFLOW

### Step-by-Step Process (Follow Exactly)

#### For Backend Features:
1. **Database Schema** (if needed)
   - Add model with `tenantId`, timestamps, soft delete
   - Add composite unique constraint: `@@unique([id, tenantId])`
   - Add indexes: `@@index([tenantId])`, relevant field indexes
   - Run: `npx prisma migrate dev --name <description>` then `npx prisma generate`

2. **Domain Layer**
   - Create entity in `domain/entities/[entity].entity.ts`
   - Create repository interface in `domain/interfaces/[entity]-repository.interface.ts`
   - Pure business objects with NO external dependencies

3. **Infrastructure Layer**
   - Implement repository in `infrastructure/repositories/[entity].repository.ts`
   - Use PrismaService for database operations
   - Map Prisma models to domain entities
   - NO manual tenantId filtering

4. **Application Layer**
   - Create use cases in `application/use-cases/*.usecase.ts`
   - Single `execute()` method per use case
   - Inject repository INTERFACES (not implementations)
   - Handle business rules, transactions, domain events
   - Throw appropriate NestJS exceptions

5. **Presentation Layer**
   - Create DTOs in `presentation/dto/*.dto.ts` with class-validator decorators
   - Create controller in `presentation/[entities].controller.ts`
   - Controllers delegate to use cases only
   - Add Swagger annotations and @Roles() decorators

6. **Module Definition**
   - Register providers in `[module].module.ts`
   - Provide repository interface with implementation
   - Export repositories if other modules need them
   - Import required modules (PrismaModule, etc.)

7. **App Module Registration**
   - Import module in `src/app.module.ts` imports array

#### For Frontend Features:
1. **Define Types**
   - Create `src/features/[feature]/types/[feature].types.ts`
   - Match backend response structures EXACTLY
   - Use existing shared types: `BaseEntity`, `ApiResponse`, `PaginatedResponse`

2. **Create API Service**
   - Create `src/features/[feature]/api/[feature].api.ts`
   - Use singleton `apiClient` (NEVER create new axios instances)
   - All methods return `Promise<ApiResponse<T>>`
   - Include JSDoc comments

3. **Update Query Keys**
   - Add query keys to `src/shared/lib/query-keys.ts`
   - Follow pattern: all, lists, list, details, detail

4. **Create Custom Hooks**
   - Create `src/features/[feature]/hooks/use-[feature].ts`
   - Mark with `'use client'` directive
   - Use React Query for ALL server state
   - Handle cache invalidation on mutations

5. **Update Barrel Export**
   - Update `src/features/[feature]/index.ts`
   - Export all public APIs

6. **Create Page Component**
   - Create `app/(dashboard)/[feature]/page.tsx`
   - Server Component by default (add `'use client'` only if needed)
   - Thin page - delegate to hooks (max 100 lines)
   - Use existing UI components
   - Handle loading, error, empty states

7. **Add Route Constants** (if needed)
   - Add to `ROUTES` in `src/shared/lib/constants.ts`

---

## 📚 REFERENCE IMPLEMENTATIONS

Study these files as GOLD STANDARD examples:

### Backend References
- **Complete Module**: `backend/src/modules/auth/`
  - Use Cases: `application/use-cases/login.usecase.ts`
  - Repository: `infrastructure/repositories/user.repository.ts`
  - Controller: `presentation/auth.controller.ts`
  - DTOs: `presentation/dto/login.dto.ts`
- **Prisma Service**: `backend/src/infrastructure/prisma/prisma.service.ts`
- **Guards**: `backend/src/common/guards/jwt-auth.guard.ts`, `roles.guard.ts`
- **Decorators**: `backend/src/common/decorators/*.decorator.ts`
- **Interceptors**: `backend/src/common/interceptors/transform.interceptor.ts`

### Frontend References
- **Complete Feature**: `frontend/src/features/auth/`
  - API: `api/auth.api.ts`
  - Hooks: `hooks/use-auth.ts`
  - Types: `types/auth.types.ts`
- **API Client**: `frontend/src/shared/lib/api-client.ts`
- **Query Keys**: `frontend/src/shared/lib/query-keys.ts`
- **UI Components**: `frontend/src/shared/ui/button.tsx` (CVA pattern)
- **Login Page**: `frontend/app/(auth)/login/page.tsx`
- **Dashboard Layout**: `frontend/app/(dashboard)/layout.tsx`
- **Constants**: `frontend/src/shared/lib/constants.ts`

---

## ⚠️ COMMON PITFALLS & SOLUTIONS

### Pitfall 1: Manual Tenant Filtering
❌ **Wrong**:
```typescript
await this.prisma.player.findMany({
  where: { tenantId: req.tenantId, deletedAt: null }
});
```

✅ **Correct**:
```typescript
await this.prisma.player.findMany({
  where: { deletedAt: null }
  // tenantId automatically added by Prisma middleware
});
```

### Pitfall 2: Direct Prisma Calls in Use Cases
❌ **Wrong**:
```typescript
@Injectable()
export class CreatePlayerUseCase {
  constructor(private prisma: PrismaService) {}
  
  async execute(data: CreatePlayerDto) {
    return this.prisma.player.create({ data });
  }
}
```

✅ **Correct**:
```typescript
@Injectable()
export class CreatePlayerUseCase {
  constructor(
    @Inject('IPlayerRepository')
    private playerRepository: IPlayerRepository
  ) {}
  
  async execute(data: CreatePlayerDto) {
    return this.playerRepository.create(data);
  }
}
```

### Pitfall 3: New Axios Instance
❌ **Wrong**:
```typescript
const axios = require('axios');
const api = axios.create({ baseURL: '...' });
```

✅ **Correct**:
```typescript
import { apiClient } from '@/shared/lib/api-client';
// Use apiClient directly - it's a singleton with interceptors
```

### Pitfall 4: Any Types
❌ **Wrong**:
```typescript
const data: any = await fetchData();
```

✅ **Correct**:
```typescript
interface PlayerData {
  id: string;
  name: string;
}
const data: PlayerData = await fetchData();
```

### Pitfall 5: Business Logic in Controllers
❌ **Wrong**:
```typescript
@Controller('players')
export class PlayersController {
  @Post()
  create(@Body() dto: CreatePlayerDto) {
    // Business logic here - WRONG!
    if (!dto.name) throw new BadRequestException();
    return this.prisma.player.create({ data: dto });
  }
}
```

✅ **Correct**:
```typescript
@Controller('players')
export class PlayersController {
  constructor(private createPlayerUseCase: CreatePlayerUseCase) {}
  
  @Post()
  create(@Body() dto: CreatePlayerDto) {
    return this.createPlayerUseCase.execute(dto);
  }
}
```

---

## 🔄 POST-IMPLEMENTATION CHECKLIST

After completing implementation:

### Documentation
1. Verify Swagger API documentation is accurate
2. Document any deviations from standards (explain WHY)
3. Add TODO comments for temporary workarounds
4. Suggest future improvements in comments

### Code Quality
1. Run linters: `npm run lint` (both backend and frontend)
2. Type checking: `npm run build` (ensure no TypeScript errors)
3. Self-review against this checklist
4. Remove debug code (console.logs, temporary comments)
5. Refactor if needed to meet standards

### Verification
1. Verify all QA checklist items pass
2. Confirm architecture compliance
3. Check file naming conventions
4. Ensure no prohibited patterns used
5. Verify mandatory patterns followed

---

## 🎯 SUCCESS CRITERIA

An implementation is considered SUCCESSFUL when:

1. ✅ All ABSOLUTE PROHIBITIONS avoided
2. ✅ All MANDATORY PATTERNS followed
3. ✅ All QA CHECKLIST items pass
4. ✅ Architecture compliance verified
5. ✅ Type safety maintained (zero `any` types)
6. ✅ Security enforced (proper guards, validation)
7. ✅ Multi-tenancy automatic (no manual filtering)
8. ✅ Code quality standards met (linting, formatting)
9. ✅ Reference patterns followed (auth module examples)
10. ✅ File naming conventions exact

---

## 📝 FINAL NOTES

1. **This rule is NON-NEGOTIABLE** - Every feature MUST comply
2. **When in doubt, check auth module** - It's the gold standard
3. **Ask questions if unclear** - Don't assume, verify
4. **Quality over speed** - Take time to do it right
5. **Consistency is critical** - Follow patterns exactly
6. **No shortcuts** - Every layer matters
7. **Test assumptions** - Verify before marking complete
8. **Document decisions** - Future developers depend on it
9. **Continuous improvement** - Learn from each implementation
10. **Standards protect the codebase** - They exist for good reasons

**REMEMBER**: These standards ensure the platform remains maintainable, scalable, and secure. Violating them introduces technical debt, security risks, and maintenance nightmares. Follow them rigorously.
