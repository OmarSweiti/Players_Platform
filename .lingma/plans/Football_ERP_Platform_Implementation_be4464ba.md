# Football Operations ERP Platform - Comprehensive Implementation Plan

## Current State Assessment

**Foundation Completeness: 70-75%**

### What's Already Built ✅
- Multi-tenant architecture with Tenant model
- Core authentication (JWT + refresh tokens)
- Role-based access control (8 roles)
- Player lifecycle management
- Contract system with versions & approvals
- Training & attendance tracking
- Medical records
- Performance records & ratings
- Legal ticketing system
- Chat/messaging with WebSocket support
- Document management system
- Audit logging
- Notification system
- Clean DDD architecture (domain/application/infrastructure/presentation)
- Global guards, interceptors, filters, validation pipes
- Event system infrastructure (BullMQ)
- Mail service
- Storage abstraction (local/S3)
- Next.js frontend with feature-based architecture

### Critical Gaps ❌
1. **Missing Roles** (9 additional roles needed): SUPER_ADMIN, SPORTING_DIRECTOR, ASSISTANT_COACH, GOALKEEPER_COACH, FITNESS_COACH, PHYSIOTHERAPIST, FINANCE_MANAGER, PERFORMANCE_ANALYST, VIDEO_ANALYST, GUARDIAN
2. **No Permission Matrix**: Currently role-based only, need fine-grained permissions
3. **Missing Domains**: Scouting, Match/Fixture Management, Finance/Payroll, Automation Engine, Advanced Analytics/BI
4. **Incomplete User Profiles**: Staff profiles lack departments, certifications, employment history

---

## Implementation Philosophy

**Order of Execution:**
1. Permission system foundation (enables everything else)
2. Role expansion (immediate value)
3. Missing domain modules (complete feature parity)
4. Advanced features (automation, analytics)

**Key Principles:**
- Database schema changes FIRST, then backend, then frontend
- Each phase is independently testable
- Backward compatibility maintained throughout
- Permission checks at both backend (guards) and frontend (UI visibility)

---

## Phase 1: Permission Matrix System (Week 1-2)

### Goal
Transform from pure role-based to role + granular permission system without breaking existing functionality.

### 1.1 Database Schema Updates

**File**: `backend/prisma/schema.prisma`

Add these models after the existing enums section:

```prisma
// New enums for permission system
enum PermissionCategory {
  PLAYER
  CONTRACT
  TRAINING
  MEDICAL
  SCOUTING
  MATCH
  FINANCE
  LEGAL
  CHAT
  USER
  TENANT
  REPORT
  DOCUMENT
  NOTIFICATION
}

enum PermissionAction {
  CREATE
  READ
  UPDATE
  DELETE
  APPROVE
  EXPORT
  IMPORT
  ASSIGN
  VIEW_CONFIDENTIAL
  MANAGE
}
```

Add new models at the end of schema (before closing):

```prisma
model Permission {
  id          String            @id @default(uuid()) @db.Uuid
  name        String            @unique @db.VarChar(100) // e.g., "player.create"
  category    PermissionCategory
  action      PermissionAction
  description String?           @db.VarChar(255)
  
  roles       RolePermission[]
  
  createdAt   DateTime          @default(now())
  updatedAt   DateTime          @updatedAt
  
  @@map("permissions")
  @@index([category])
  @@index([action])
}

model RolePermission {
  id             String     @id @default(uuid()) @db.Uuid
  roleId         UserRole
  permissionId   String     @db.Uuid
  
  role           UserRole   // This will be mapped via enum
  permission     Permission @relation(fields: [permissionId], references: [id], onDelete: Cascade)
  
  createdAt      DateTime   @default(now())
  
  @@unique([roleId, permissionId])
  @@map("role_permissions")
  @@index([roleId])
  @@index([permissionId])
}
```

**Note**: Prisma doesn't support enum-to-table relations directly. We'll use a string field `roleId` that stores the enum value as string, and handle mapping in application layer.

### 1.2 Backend Implementation

#### Step 1: Create Permission Constants

**File**: `backend/src/shared/constants/permissions.constants.ts`

```typescript
export const PERMISSIONS = {
  // Player Management
  PLAYER_CREATE: 'player.create',
  PLAYER_READ: 'player.read',
  PLAYER_UPDATE: 'player.update',
  PLAYER_DELETE: 'player.delete',
  PLAYER_EXPORT: 'player.export',
  
  // Contract Management
  CONTRACT_CREATE: 'contract.create',
  CONTRACT_READ: 'contract.read',
  CONTRACT_UPDATE: 'contract.update',
  CONTRACT_DELETE: 'contract.delete',
  CONTRACT_APPROVE: 'contract.approve',
  CONTRACT_REJECT: 'contract.reject',
  
  // Training
  TRAINING_CREATE: 'training.create',
  TRAINING_READ: 'training.read',
  TRAINING_UPDATE: 'training.update',
  TRAINING_DELETE: 'training.delete',
  TRAINING_ASSIGN: 'training.assign',
  
  // Medical (confidential)
  MEDICAL_CREATE: 'medical.create',
  MEDICAL_READ: 'medical.read',
  MEDICAL_UPDATE: 'medical.update',
  MEDICAL_VIEW_CONFIDENTIAL: 'medical.view_confidential',
  
  // Scouting
  SCOUTING_CREATE: 'scouting.create',
  SCOUTING_READ: 'scouting.read',
  SCOUTING_UPDATE: 'scouting.update',
  SCOUTING_DELETE: 'scouting.delete',
  
  // Match Management
  MATCH_CREATE: 'match.create',
  MATCH_READ: 'match.read',
  MATCH_UPDATE: 'match.update',
  MATCH_DELETE: 'match.delete',
  
  // Finance
  FINANCE_READ: 'finance.read',
  FINANCE_MANAGE: 'finance.manage',
  FINANCE_EXPORT: 'finance.export',
  
  // Legal
  LEGAL_CREATE: 'legal.create',
  LEGAL_READ: 'legal.read',
  LEGAL_UPDATE: 'legal.update',
  LEGAL_APPROVE: 'legal.approve',
  
  // User Management
  USER_CREATE: 'user.create',
  USER_READ: 'user.read',
  USER_UPDATE: 'user.update',
  USER_DELETE: 'user.delete',
  USER_ASSIGN_ROLE: 'user.assign_role',
  
  // Tenant Management
  TENANT_MANAGE: 'tenant.manage',
  
  // Reports & Analytics
  REPORT_VIEW: 'report.view',
  REPORT_EXPORT: 'report.export',
  
  // Documents
  DOCUMENT_UPLOAD: 'document.upload',
  DOCUMENT_DELETE: 'document.delete',
  
  // Chat
  CHAT_SEND: 'chat.send',
  CHAT_READ: 'chat.read',
  CHAT_DELETE: 'chat.delete',
} as const;

export type PermissionType = typeof PERMISSIONS[keyof typeof PERMISSIONS];
```

#### Step 2: Create Permission Service

**File**: `backend/src/modules/users/application/services/permission.service.ts`

```typescript
import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../../../infrastructure/prisma/prisma.service';
import { UserRole } from '@prisma/client';
import { PERMISSIONS, PermissionType } from '../../../../shared/constants/permissions.constants';

@Injectable()
export class PermissionService {
  constructor(private prisma: PrismaService) {}

  /**
   * Check if a user role has a specific permission
   */
  async hasPermission(role: UserRole, permission: PermissionType): Promise<boolean> {
    const permissionRecord = await this.prisma.permission.findUnique({
      where: { name: permission },
      include: {
        roles: {
          where: { roleId: role },
        },
      },
    });

    return !!permissionRecord && permissionRecord.roles.length > 0;
  }

  /**
   * Get all permissions for a role
   */
  async getRolePermissions(role: UserRole): Promise<string[]> {
    const rolePermissions = await this.prisma.rolePermission.findMany({
      where: { roleId: role },
      include: { permission: true },
    });

    return rolePermissions.map(rp => rp.permission.name);
  }

  /**
   * Seed default permissions for all roles
   */
  async seedDefaultPermissions(): Promise<void> {
    // Create all permission records
    const permissionValues = Object.values(PERMISSIONS);
    
    for (const permName of permissionValues) {
      const [category, action] = permName.split('.');
      
      await this.prisma.permission.upsert({
        where: { name: permName },
        update: {},
        create: {
          name: permName,
          category: category.toUpperCase() as any,
          action: action.toUpperCase() as any,
          description: `${action} ${category}`,
        },
      });
    }

    // Assign default permissions to each role
    const rolePermissionMap = this.getDefaultRolePermissions();
    
    for (const [role, permissions] of Object.entries(rolePermissionMap)) {
      for (const permName of permissions) {
        const permission = await this.prisma.permission.findUnique({
          where: { name: permName },
        });

        if (permission) {
          await this.prisma.rolePermission.upsert({
            where: {
              roleId_permissionId: {
                roleId: role as UserRole,
                permissionId: permission.id,
              },
            },
            update: {},
            create: {
              roleId: role as UserRole,
              permissionId: permission.id,
            },
          });
        }
      }
    }
  }

  /**
   * Define default permissions for each role
   */
  private getDefaultRolePermissions(): Record<string, string[]> {
    return {
      SUPER_ADMIN: Object.values(PERMISSIONS), // All permissions
      
      OWNER: [
        PERMISSIONS.PLAYER_CREATE, PERMISSIONS.PLAYER_READ, PERMISSIONS.PLAYER_UPDATE,
        PERMISSIONS.CONTRACT_CREATE, PERMISSIONS.CONTRACT_READ, PERMISSIONS.CONTRACT_APPROVE,
        PERMISSIONS.TRAINING_READ,
        PERMISSIONS.MEDICAL_READ, PERMISSIONS.MEDICAL_VIEW_CONFIDENTIAL,
        PERMISSIONS.Scouting_READ,
        PERMISSIONS.MATCH_READ,
        PERMISSIONS.FINANCE_READ, PERMISSIONS.FINANCE_EXPORT,
        PERMISSIONS.LEGAL_READ,
        PERMISSIONS.USER_READ,
        PERMISSIONS.TENANT_MANAGE,
        PERMISSIONS.REPORT_VIEW, PERMISSIONS.REPORT_EXPORT,
        PERMISSIONS.CHAT_READ,
      ],
      
      ADMIN: [
        PERMISSIONS.PLAYER_CREATE, PERMISSIONS.PLAYER_READ, PERMISSIONS.PLAYER_UPDATE,
        PERMISSIONS.CONTRACT_CREATE, PERMISSIONS.CONTRACT_READ,
        PERMISSIONS.TRAINING_CREATE, PERMISSIONS.TRAINING_READ, PERMISSIONS.TRAINING_UPDATE,
        PERMISSIONS.MEDICAL_READ,
        PERMISSIONS.Scouting_READ,
        PERMISSIONS.MATCH_READ,
        PERMISSIONS.LEGAL_CREATE, PERMISSIONS.LEGAL_READ,
        PERMISSIONS.USER_CREATE, PERMISSIONS.USER_READ, PERMISSIONS.USER_UPDATE,
        PERMISSIONS.REPORT_VIEW,
        PERMISSIONS.DOCUMENT_UPLOAD,
        PERMISSIONS.CHAT_SEND, PERMISSIONS.CHAT_READ,
      ],
      
      SPORTING_DIRECTOR: [
        PERMISSIONS.PLAYER_READ, PERMISSIONS.PLAYER_UPDATE,
        PERMISSIONS.CONTRACT_READ, PERMISSIONS.CONTRACT_APPROVE,
        PERMISSIONS.Scouting_CREATE, PERMISSIONS.Scouting_READ, PERMISSIONS.Scouting_UPDATE,
        PERMISSIONS.MATCH_READ,
        PERMISSIONS.TRAINING_READ,
        PERMISSIONS.PERFORMANCE_READ,
        PERMISSIONS.REPORT_VIEW,
      ],
      
      COACH: [
        PERMISSIONS.PLAYER_READ,
        PERMISSIONS.TRAINING_CREATE, PERMISSIONS.TRAINING_READ, PERMISSIONS.TRAINING_UPDATE,
        PERMISSIONS.MATCH_READ, PERMISSIONS.MATCH_UPDATE,
        PERMISSIONS.PERFORMANCE_READ,
        PERMISSIONS.CHAT_SEND, PERMISSIONS.CHAT_READ,
      ],
      
      SCOUT: [
        PERMISSIONS.PLAYER_READ,
        PERMISSIONS.Scouting_CREATE, PERMISSIONS.Scouting_READ, PERMISSIONS.Scouting_UPDATE,
        PERMISSIONS.DOCUMENT_UPLOAD,
      ],
      
      MEDICAL: [
        PERMISSIONS.PLAYER_READ,
        PERMISSIONS.MEDICAL_CREATE, PERMISSIONS.MEDICAL_READ, PERMISSIONS.MEDICAL_UPDATE,
        PERMISSIONS.MEDICAL_VIEW_CONFIDENTIAL,
        PERMISSIONS.TRAINING_READ,
      ],
      
      FITNESS_COACH: [
        PERMISSIONS.PLAYER_READ,
        PERMISSIONS.TRAINING_CREATE, PERMISSIONS.TRAINING_READ,
        PERMISSIONS.MEDICAL_READ,
      ],
      
      LEGAL: [
        PERMISSIONS.CONTRACT_READ, PERMISSIONS.CONTRACT_APPROVE,
        PERMISSIONS.LEGAL_CREATE, PERMISSIONS.LEGAL_READ, PERMISSIONS.LEGAL_UPDATE, PERMISSIONS.LEGAL_APPROVE,
        PERMISSIONS.DOCUMENT_UPLOAD,
      ],
      
      FINANCE_MANAGER: [
        PERMISSIONS.CONTRACT_READ,
        PERMISSIONS.FINANCE_READ, PERMISSIONS.FINANCE_MANAGE, PERMISSIONS.FINANCE_EXPORT,
        PERMISSIONS.REPORT_VIEW,
      ],
      
      PERFORMANCE_ANALYST: [
        PERMISSIONS.PLAYER_READ,
        PERMISSIONS.MATCH_READ,
        PERMISSIONS.PERFORMANCE_CREATE, PERMISSIONS.PERFORMANCE_READ,
        PERMISSIONS.REPORT_VIEW, PERMISSIONS.REPORT_EXPORT,
      ],
      
      PLAYER: [
        PERMISSIONS.PLAYER_READ, // Own profile only (handled in service)
        PERMISSIONS.CONTRACT_READ, // Own contracts only
        PERMISSIONS.TRAINING_READ, // Assigned trainings
        PERMISSIONS.MEDICAL_READ, // Own medical only
        PERMISSIONS.CHAT_SEND, PERMISSIONS.CHAT_READ,
      ],
      
      GUARDIAN: [
        PERMISSIONS.PLAYER_READ, // Linked players only
        PERMISSIONS.TRAINING_READ,
      ],
    };
  }
}
```

#### Step 3: Update Roles Guard to Support Permissions

**File**: `backend/src/common/guards/roles.guard.ts`

Replace existing implementation:

```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { ROLES_KEY } from '../decorators/roles.decorator';
import { PERMISSIONS_KEY } from '../decorators/permissions.decorator';
import { UserRole } from '@prisma/client';
import { RequestWithUser } from '../interfaces/request-with-user.interface';
import { PermissionService } from '../../modules/users/application/services/permission.service';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(
    private reflector: Reflector,
    private permissionService: PermissionService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const requiredRoles = this.reflector.getAllAndOverride<UserRole[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    
    const requiredPermissions = this.reflector.getAllAndOverride<string[]>(PERMISSIONS_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    
    // If no roles or permissions required, allow access
    if (!requiredRoles && !requiredPermissions) {
      return true;
    }
    
    const request = context.switchToHttp().getRequest<RequestWithUser>();
    const user = request.user;
    
    if (!user) {
      throw new ForbiddenException('User not authenticated');
    }
    
    // Check role-based access
    if (requiredRoles && requiredRoles.length > 0) {
      const hasRole = requiredRoles.some((role) => user.role === role);
      
      if (!hasRole) {
        throw new ForbiddenException('Insufficient role permissions');
      }
    }
    
    // Check permission-based access
    if (requiredPermissions && requiredPermissions.length > 0) {
      const hasPermission = await this.checkPermissions(user.role, requiredPermissions);
      
      if (!hasPermission) {
        throw new ForbiddenException('Insufficient permissions');
      }
    }
    
    return true;
  }

  private async checkPermissions(role: UserRole, permissions: string[]): Promise<boolean> {
    // Check if user has ALL required permissions
    for (const permission of permissions) {
      const hasPerm = await this.permissionService.hasPermission(role, permission as any);
      if (!hasPerm) {
        return false;
      }
    }
    return true;
  }
}
```

#### Step 4: Create Permissions Decorator

**File**: `backend/src/common/decorators/permissions.decorator.ts`

```typescript
import { SetMetadata } from '@nestjs/common';

export const PERMISSIONS_KEY = 'permissions';
export const RequirePermissions = (...permissions: string[]) => 
  SetMetadata(PERMISSIONS_KEY, permissions);
```

#### Step 5: Create Database Seeder Script

**File**: `backend/src/database/seed.ts`

```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from '../app.module';
import { PermissionService } from '../modules/users/application/services/permission.service';

async function bootstrap() {
  const app = await NestFactory.createApplicationContext(AppModule);
  const permissionService = app.get(PermissionService);

  console.log('Seeding permissions...');
  await permissionService.seedDefaultPermissions();
  console.log('Permissions seeded successfully!');

  await app.close();
}

bootstrap();
```

### 1.3 Frontend Permission Utilities

**File**: `frontend/src/shared/lib/permissions.ts`

```typescript
import { useAuthStore } from '@/features/auth/stores/auth.store';

// Mirror backend permissions
export const PERMISSIONS = {
  PLAYER_CREATE: 'player.create',
  PLAYER_READ: 'player.read',
  PLAYER_UPDATE: 'player.update',
  PLAYER_DELETE: 'player.delete',
  CONTRACT_CREATE: 'contract.create',
  CONTRACT_APPROVE: 'contract.approve',
  TRAINING_CREATE: 'training.create',
  MEDICAL_VIEW_CONFIDENTIAL: 'medical.view_confidential',
  SCOUTING_CREATE: 'scouting.create',
  MATCH_CREATE: 'match.create',
  FINANCE_MANAGE: 'finance.manage',
  LEGAL_APPROVE: 'legal.approve',
  USER_ASSIGN_ROLE: 'user.assign_role',
  TENANT_MANAGE: 'tenant.manage',
  REPORT_EXPORT: 'report.export',
  // ... add all permissions
} as const;

export type PermissionType = typeof PERMISSIONS[keyof typeof PERMISSIONS];

/**
 * Hook to check if current user has permission
 */
export function usePermission(permission: PermissionType): boolean {
  const { user } = useAuthStore();
  
  if (!user) return false;
  
  // For now, check based on role (will be enhanced when we fetch user permissions)
  return hasPermissionForRole(user.role, permission);
}

/**
 * Check if a role typically has a permission (client-side fallback)
 * This should be replaced with actual permission data from backend
 */
function hasPermissionForRole(role: string, permission: PermissionType): boolean {
  const rolePermissions: Record<string, PermissionType[]> = {
    SUPER_ADMIN: Object.values(PERMISSIONS),
    OWNER: [PERMISSIONS.PLAYER_READ, PERMISSIONS.CONTRACT_APPROVE, /* ... */],
    ADMIN: [PERMISSIONS.PLAYER_CREATE, PERMISSIONS.PLAYER_READ, /* ... */],
    // ... define for all roles
  };
  
  return rolePermissions[role]?.includes(permission) || false;
}

/**
 * Component to conditionally render based on permission
 */
export function RequirePermission({ 
  permission, 
  children, 
  fallback = null 
}: { 
  permission: PermissionType; 
  children: React.ReactNode; 
  fallback?: React.ReactNode;
}) {
  const hasPermission = usePermission(permission);
  
  return hasPermission ? <>{children}</> : <>{fallback}</>;
}
```

### 1.4 Migration & Testing

**Steps:**
1. Run Prisma migration: `npx prisma migrate dev --name add_permission_system`
2. Run seeder: `npm run seed` (add script to package.json)
3. Test permission checks in Postman/curl
4. Update 2-3 existing endpoints to use `@RequirePermissions()` decorator
5. Verify backward compatibility (existing role-based checks still work)

---

## Phase 2: Expand User Roles (Week 2-3)

### Goal
Add 9 new professional roles to support enterprise football operations.

### 2.1 Update Prisma Schema

**File**: `backend/prisma/schema.prisma`

Update the `UserRole` enum:

```prisma
enum UserRole {
  SUPER_ADMIN        // Platform-level admin (multi-tenant SaaS)
  OWNER              // Club/academy owner
  ADMIN              // Operational administrator
  SPORTING_DIRECTOR  // Oversees squad planning, transfers, recruitment
  SCOUT              // Talent discovery and reporting
  COACH              // Head coach
  ASSISTANT_COACH    // Assistant coaching staff
  GOALKEEPER_COACH   // Specialized GK coach
  FITNESS_COACH      // Physical conditioning
  MEDICAL            // Medical staff
  PHYSIOTHERAPIST    // Rehabilitation specialist
  LEGAL              // Legal department
  FINANCE_MANAGER    // Salary, payroll, transfers
  PERFORMANCE_ANALYST // Match/stats analysis
  VIDEO_ANALYST      // Video tagging and review
  TRAINING_MANAGER   // Training coordination
  PLAYER             // Athlete
  GUARDIAN           // Parent/guardian (academy)
}
```

### 2.2 Update Backend Type Definitions

**File**: `backend/src/shared/types/user.types.ts` (create if doesn't exist)

```typescript
import { UserRole } from '@prisma/client';

export const ROLE_HIERARCHY: Record<UserRole, number> = {
  SUPER_ADMIN: 100,
  OWNER: 90,
  ADMIN: 80,
  SPORTING_DIRECTOR: 70,
  LEGAL: 65,
  FINANCE_MANAGER: 60,
  COACH: 55,
  PERFORMANCE_ANALYST: 50,
  VIDEO_ANALYST: 48,
  TRAINING_MANAGER: 45,
  ASSISTANT_COACH: 40,
  GOALKEEPER_COACH: 40,
  FITNESS_COACH: 40,
  MEDICAL: 50,
  PHYSIOTHERAPIST: 45,
  SCOUT: 45,
  PLAYER: 10,
  GUARDIAN: 15,
};

export const ROLE_DISPLAY_NAMES: Record<UserRole, string> = {
  SUPER_ADMIN: 'Super Administrator',
  OWNER: 'Club Owner',
  ADMIN: 'Administrator',
  SPORTING_DIRECTOR: 'Sporting Director',
  SCOUT: 'Scout',
  COACH: 'Head Coach',
  ASSISTANT_COACH: 'Assistant Coach',
  GOALKEEPER_COACH: 'Goalkeeper Coach',
  FITNESS_COACH: 'Fitness Coach',
  MEDICAL: 'Medical Staff',
  PHYSIOTHERAPIST: 'Physiotherapist',
  LEGAL: 'Legal Counsel',
  FINANCE_MANAGER: 'Finance Manager',
  PERFORMANCE_ANALYST: 'Performance Analyst',
  VIDEO_ANALYST: 'Video Analyst',
  TRAINING_MANAGER: 'Training Manager',
  PLAYER: 'Player',
  GUARDIAN: 'Guardian',
};

export const ROLE_CATEGORIES: Record<UserRole, 'executive' | 'operations' | 'football' | 'medical' | 'legal' | 'finance' | 'analysis' | 'player' | 'guardian'> = {
  SUPER_ADMIN: 'executive',
  OWNER: 'executive',
  ADMIN: 'operations',
  SPORTING_DIRECTOR: 'football',
  SCOUT: 'football',
  COACH: 'football',
  ASSISTANT_COACH: 'football',
  GOALKEEPER_COACH: 'football',
  FITNESS_COACH: 'football',
  MEDICAL: 'medical',
  PHYSIOTHERAPIST: 'medical',
  LEGAL: 'legal',
  FINANCE_MANAGER: 'finance',
  PERFORMANCE_ANALYST: 'analysis',
  VIDEO_ANALYST: 'analysis',
  TRAINING_MANAGER: 'operations',
  PLAYER: 'player',
  GUARDIAN: 'guardian',
};
```

### 2.3 Enhance User Profile Model

**File**: `backend/prisma/schema.prisma`

Add fields to User model (after `preferences` field):

```prisma
model User {
  // ... existing fields ...
  
  /// Staff profile enhancements
  department          String?   @db.VarChar(100) // e.g., "Coaching", "Medical", "Legal"
  position            String?   @db.VarChar(150) // Job title
  certifications      Json?     // Array of certifications/licenses
  employmentStartDate DateTime?
  employmentEndDate   DateTime?
  bio                 String?   @db.Text
  emergencyContact    String?   @db.VarChar(150)
  emergencyPhone      String?   @db.VarChar(20)
  
  // ... rest of existing fields ...
}
```

Run migration: `npx prisma migrate dev --name enhance_user_profiles`

### 2.4 Update Frontend Role Types

**File**: `frontend/src/features/auth/types/auth.types.ts`

Update to include all new roles with display names and categories.

### 2.5 Update Permission Seeds

**File**: `backend/src/modules/users/application/services/permission.service.ts`

Add permission mappings for new roles in `getDefaultRolePermissions()`:

```typescript
SPORTING_DIRECTOR: [
  PERMISSIONS.PLAYER_READ, PERMISSIONS.PLAYER_UPDATE,
  PERMISSIONS.CONTRACT_READ, PERMISSIONS.CONTRACT_APPROVE,
  PERMISSIONS.Scouting_CREATE, PERMISSIONS.Scouting_READ, PERMISSIONS.Scouting_UPDATE,
  PERMISSIONS.MATCH_READ,
  PERMISSIONS.TRAINING_READ,
  PERMISSIONS.REPORT_VIEW, PERMISSIONS.REPORT_EXPORT,
],

ASSISTANT_COACH: [
  PERMISSIONS.PLAYER_READ,
  PERMISSIONS.TRAINING_READ, PERMISSIONS.TRAINING_UPDATE,
  PERMISSIONS.MATCH_READ,
],

GOALKEEPER_COACH: [
  PERMISSIONS.PLAYER_READ,
  PERMISSIONS.TRAINING_CREATE, PERMISSIONS.TRAINING_READ,
],

FITNESS_COACH: [
  PERMISSIONS.PLAYER_READ,
  PERMISSIONS.TRAINING_CREATE, PERMISSIONS.TRAINING_READ,
  PERMISSIONS.MEDICAL_READ,
],

PHYSIOTHERAPIST: [
  PERMISSIONS.PLAYER_READ,
  PERMISSIONS.MEDICAL_CREATE, PERMISSIONS.MEDICAL_READ, PERMISSIONS.MEDICAL_UPDATE,
],

FINANCE_MANAGER: [
  PERMISSIONS.CONTRACT_READ,
  PERMISSIONS.FINANCE_READ, PERMISSIONS.FINANCE_MANAGE, PERMISSIONS.FINANCE_EXPORT,
  PERMISSIONS.REPORT_VIEW,
],

PERFORMANCE_ANALYST: [
  PERMISSIONS.PLAYER_READ,
  PERMISSIONS.MATCH_READ,
  PERMISSIONS.PERFORMANCE_CREATE, PERMISSIONS.PERFORMANCE_READ,
  PERMISSIONS.REPORT_VIEW, PERMISSIONS.REPORT_EXPORT,
],

VIDEO_ANALYST: [
  PERMISSIONS.PLAYER_READ,
  PERMISSIONS.MATCH_READ,
  PERMISSIONS.DOCUMENT_UPLOAD,
  PERMISSIONS.REPORT_VIEW,
],

GUARDIAN: [
  PERMISSIONS.PLAYER_READ, // Only linked players
  PERMISSIONS.TRAINING_READ,
],
```

Re-run seeder after updates.

---

## Phase 3: Scouting Module (Week 3-4)

### Goal
Build comprehensive scouting system for talent discovery and player evaluation.

### 3.1 Database Schema

**File**: `backend/prisma/schema.prisma`

Add new models:

```prisma
enum ScoutReportStatus {
  DRAFT
  SUBMITTED
  UNDER_REVIEW
  APPROVED
  REJECTED
}

enum RecommendationLevel {
  STRONG_SIGN
  SIGN
  MONITOR
  NOT_SUITABLE
}

model ScoutingReport {
  id              String             @id @default(uuid()) @db.Uuid
  tenantId        String             @db.Uuid
  scoutId         String             @db.Uuid
  playerId        String?            @db.Uuid  // Null for external prospects
  
  // Player being scouted (if not in system yet)
  prospectName    String?            @db.VarChar(255)
  prospectAge     Int?
  prospectClub    String?            @db.VarChar(255)
  prospectPosition PlayerPosition?
  prospectNationality String?        @db.VarChar(100)
  
  status          ScoutReportStatus  @default(DRAFT)
  recommendation  RecommendationLevel?
  
  // Evaluation scores (1-10)
  technicalScore  Decimal?           @db.Decimal(3, 1)
  physicalScore   Decimal?           @db.Decimal(3, 1)
  tacticalScore   Decimal?           @db.Decimal(3, 1)
  mentalScore     Decimal?           @db.Decimal(3, 1)
  
  strengths       String?            @db.Text
  weaknesses      String?            @db.Text
  personalityNotes String?           @db.Text
  tacticalFit     String?            @db.Text
  
  overallRating   Decimal?           @db.Decimal(3, 1)
  potentialRating Decimal?           @db.Decimal(3, 1)
  
  reportDate      DateTime
  matchObserved   String?            @db.VarChar(255)
  
  metadata        Json?
  
  tenant          Tenant             @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  scout           User               @relation(fields: [scoutId, tenantId], references: [id, tenantId], onDelete: Restrict)
  player          Player?            @relation(fields: [playerId, tenantId], references: [id, tenantId], onDelete: SetNull)
  
  createdAt       DateTime           @default(now())
  updatedAt       DateTime           @updatedAt
  deletedAt       DateTime?
  
  @@unique([id, tenantId])
  @@map("scouting_reports")
  @@index([tenantId])
  @@index([scoutId])
  @@index([playerId])
  @@index([status])
  @@index([recommendation])
}

model PlayerWatchlist {
  id          String   @id @default(uuid()) @db.Uuid
  tenantId    String   @db.Uuid
  userId      String   @db.Uuid  // Scout or Sporting Director
  playerId    String   @db.Uuid
  
  priority    String?  @db.VarChar(50) // HIGH, MEDIUM, LOW
  notes       String?  @db.Text
  
  tenant      Tenant   @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  user        User     @relation(fields: [userId, tenantId], references: [id, tenantId], onDelete: Restrict)
  player      Player   @relation(fields: [playerId, tenantId], references: [id, tenantId], onDelete: Restrict)
  
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  @@unique([userId, playerId])
  @@unique([id, tenantId])
  @@map("player_watchlists")
  @@index([tenantId])
  @@index([userId])
}

model ScoutingAssignment {
  id            String   @id @default(uuid()) @db.Uuid
  tenantId      String   @db.Uuid
  assignedToId  String   @db.Uuid  // Scout
  assignedById  String   @db.Uuid  // Sporting Director
  
  region        String?  @db.VarChar(100)
  competition   String?  @db.VarChar(150)
  targetPosition PlayerPosition?
  minAge        Int?
  maxAge        Int?
  
  dueDate       DateTime?
  status        String   @db.VarChar(50) @default("OPEN") // OPEN, IN_PROGRESS, COMPLETED
  
  notes         String?  @db.Text
  
  tenant        Tenant   @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  assignedTo    User     @relation(fields: [assignedToId, tenantId], references: [id, tenantId], onDelete: Restrict)
  assignedBy    User     @relation(fields: [assignedById, tenantId], references: [id, tenantId], onDelete: Restrict)
  
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  
  @@unique([id, tenantId])
  @@map("scouting_assignments")
  @@index([tenantId])
  @@index([assignedToId])
  @@index([status])
}
```

Run migration: `npx prisma migrate dev --name add_scouting_module`

### 3.2 Backend Module Structure

Create directory structure:
```
backend/src/modules/scouting/
├── application/
│   ├── use-cases/
│   │   ├── create-scout-report.usecase.ts
│   │   ├── update-scout-report.usecase.ts
│   │   ├── submit-scout-report.usecase.ts
│   │   ├── approve-scout-report.usecase.ts
│   │   ├── list-scout-reports.usecase.ts
│   │   ├── get-scout-report.usecase.ts
│   │   ├── add-to-watchlist.usecase.ts
│   │   ├── remove-from-watchlist.usecase.ts
│   │   ├── create-assignment.usecase.ts
│   │   └── list-assignments.usecase.ts
│   └── services/
│       └── scouting-analytics.service.ts
├── domain/
│   ├── entities/
│   │   └── scouting-report.entity.ts
│   └── enums/
│       └── recommendation-level.enum.ts
├── infrastructure/
│   └── repositories/
│       ├── scouting-report.repository.ts
│       ├── watchlist.repository.ts
│       └── assignment.repository.ts
├── presentation/
│   ├── scouting.controller.ts
│   └── dto/
│       ├── create-scout-report.dto.ts
│       ├── update-scout-report.dto.ts
│       └── scouting-filters.dto.ts
└── scouting.module.ts
```

### 3.3 Example Use Case

**File**: `backend/src/modules/scouting/application/use-cases/create-scout-report.usecase.ts`

```typescript
import { Injectable } from '@nestjs/common';
import { ScoutingReportRepository } from '../../infrastructure/repositories/scouting-report.repository';
import { CreateScoutReportDto } from '../../presentation/dto/create-scout-report.dto';
import { EventService } from '../../../../infrastructure/events/event.service';

@Injectable()
export class CreateScoutReportUseCase {
  constructor(
    private repository: ScoutingReportRepository,
    private eventService: EventService,
  ) {}

  async execute(dto: CreateScoutReportDto, userId: string, tenantId: string) {
    const report = await this.repository.create({
      ...dto,
      scoutId: userId,
      tenantId,
      status: 'DRAFT',
      reportDate: new Date(),
    });

    // Emit event for notifications
    this.eventService.emitNotification({
      type: 'SCOUT_REPORT_CREATED',
      userId: userId,
      title: 'Scouting Report Created',
      content: `New scouting report created for ${dto.prospectName || 'player'}`,
      referenceType: 'SCOUTING_REPORT',
      referenceId: report.id,
    });

    return report;
  }
}
```

### 3.4 Controller with Permissions

**File**: `backend/src/modules/scouting/presentation/scouting.controller.ts`

```typescript
import { Controller, Get, Post, Put, Body, Param, Query } from '@nestjs/common';
import { RequirePermissions } from '../../../common/decorators/permissions.decorator';
import { PERMISSIONS } from '../../../shared/constants/permissions.constants';
import { CurrentUser } from '../../../common/decorators/current-user.decorator';
import { RequestWithUser } from '../../../common/interfaces/request-with-user.interface';

@Controller('scouting')
export class ScoutingController {
  constructor(
    private createReportUseCase: CreateScoutReportUseCase,
    // ... inject other use cases
  ) {}

  @Post('reports')
  @RequirePermissions(PERMISSIONS.SCOUTING_CREATE)
  async createReport(
    @Body() dto: CreateScoutReportDto,
    @CurrentUser() user: RequestWithUser['user'],
  ) {
    return this.createReportUseCase.execute(dto, user.id, user.tenantId);
  }

  @Get('reports')
  @RequirePermissions(PERMISSIONS.SCOUTING_READ)
  async listReports(@Query() filters: any, @CurrentUser() user: RequestWithUser['user']) {
    return this.listReportsUseCase.execute(filters, user.tenantId);
  }

  @Get('watchlist')
  @RequirePermissions(PERMISSIONS.SCOUTING_READ)
  async getWatchlist(@CurrentUser() user: RequestWithUser['user']) {
    return this.getWatchlistUseCase.execute(user.id, user.tenantId);
  }

  @Post('watchlist')
  @RequirePermissions(PERMISSIONS.SCOUTING_CREATE)
  async addToWatchlist(@Body() dto: any, @CurrentUser() user: RequestWithUser['user']) {
    return this.addToWatchlistUseCase.execute(dto, user.id, user.tenantId);
  }
}
```

### 3.5 Frontend Feature Module

Create structure:
```
frontend/src/features/scouting/
├── api/
│   └── scouting.api.ts
├── components/
│   ├── scout-report-form.tsx
│   ├── scout-report-card.tsx
│   ├── watchlist-table.tsx
│   ├── player-comparison.tsx
│   └── scouting-dashboard.tsx
├── hooks/
│   ├── use-scout-reports.ts
│   ├── use-watchlist.ts
│   └── use-assignments.ts
├── types/
│   └── scouting.types.ts
└── index.ts
```

**File**: `frontend/src/features/scouting/api/scouting.api.ts`

```typescript
import apiClient from '@/shared/lib/api-client';
import { ScoutReport, WatchlistItem } from '../types/scouting.types';

export const scoutingApi = {
  createReport: (data: Partial<ScoutReport>) =>
    apiClient.post<ScoutReport>('/scouting/reports', data),
  
  listReports: (filters?: any) =>
    apiClient.get<ScoutReport[]>('/scouting/reports', { params: filters }),
  
  getReport: (id: string) =>
    apiClient.get<ScoutReport>(`/scouting/reports/${id}`),
  
  updateReport: (id: string, data: Partial<ScoutReport>) =>
    apiClient.put<ScoutReport>(`/scouting/reports/${id}`, data),
  
  submitReport: (id: string) =>
    apiClient.post<ScoutReport>(`/scouting/reports/${id}/submit`),
  
  getWatchlist: () =>
    apiClient.get<WatchlistItem[]>('/scouting/watchlist'),
  
  addToWatchlist: (playerId: string, notes?: string) =>
    apiClient.post<WatchlistItem>('/scouting/watchlist', { playerId, notes }),
  
  removeFromWatchlist: (playerId: string) =>
    apiClient.delete(`/scouting/watchlist/${playerId}`),
};
```

---

## Phase 4: Match Management Module (Week 4-5)

### Goal
Implement comprehensive match/fixture management with lineups, events, and statistics.

### 4.1 Database Schema

**File**: `backend/prisma/schema.prisma`

```prisma
enum MatchStatus {
  SCHEDULED
  LIVE
  COMPLETED
  POSTPONED
  CANCELLED
}

enum MatchVenue {
  HOME
  AWAY
  NEUTRAL
}

enum CardType {
  YELLOW
  RED
}

enum SubstitutionReason {
  TACTICAL
  INJURY
  FATIGUE
  OTHER
}

model Match {
  id              String       @id @default(uuid()) @db.Uuid
  tenantId        String       @db.Uuid
  seasonId        String?      @db.Uuid
  
  homeTeam        String       @db.VarChar(150)
  awayTeam        String       @db.VarChar(150)
  
  competition     String?      @db.VarChar(150)
  round           String?      @db.VarChar(50)  // e.g., "Round 1", "Quarter-final"
  
  matchDate       DateTime
  venue           String?      @db.VarChar(255)
  referee         String?      @db.VarChar(150)
  
  status          MatchStatus  @default(SCHEDULED)
  
  homeScore       Int?         @default(0)
  awayScore       Int?         @default(0)
  
  homeLineup      Json?        // Array of player IDs + formation
  awayLineup      Json?
  
  homeSubstitutes Json?
  awaySubstitutes Json?
  
  attendance      Int?
  weather         String?      @db.VarChar(100)
  
  matchReport     String?      @db.Text
  
  metadata        Json?
  
  tenant          Tenant       @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  season          Season?      @relation(fields: [seasonId], references: [id], onDelete: SetNull)
  
  events          MatchEvent[]
  statistics      MatchStatistics[]
  
  createdAt       DateTime     @default(now())
  updatedAt       DateTime     @updatedAt
  deletedAt       DateTime?
  
  @@unique([id, tenantId])
  @@map("matches")
  @@index([tenantId])
  @@index([matchDate])
  @@index([status])
  @@index([seasonId])
}

model MatchEvent {
  id          String   @id @default(uuid()) @db.Uuid
  tenantId    String   @db.Uuid
  matchId     String   @db.Uuid
  
  eventType   String   @db.VarChar(50)  // GOAL, ASSIST, CARD, SUBSTITUTION, INJURY, etc.
  minute      Int
  
  playerId    String?  @db.Uuid
  team        String   @db.VarChar(10)  // HOME or AWAY
  
  // Event-specific data
  cardType    CardType?
  substitutionInId  String? @db.Uuid
  substitutionOutId String? @db.Uuid
  subReason   SubstitutionReason?
  
  description String?  @db.VarChar(500)
  
  match       Match    @relation(fields: [matchId, tenantId], references: [id, tenantId], onDelete: Restrict)
  
  createdAt   DateTime @default(now())
  
  @@unique([id, tenantId])
  @@map("match_events")
  @@index([matchId])
  @@index([eventType])
}

model MatchStatistics {
  id          String   @id @default(uuid()) @db.Uuid
  tenantId    String   @db.Uuid
  matchId     String   @db.Uuid
  playerId    String?  @db.Uuid  // Null for team-level stats
  
  team        String   @db.VarChar(10)  // HOME or AWAY
  
  minutesPlayed Int?
  goals       Int      @default(0)
  assists     Int      @default(0)
  shots       Int      @default(0)
  shotsOnTarget Int?   @default(0)
  passes      Int      @default(0)
  passAccuracy Decimal? @db.Decimal(5, 2)
  tackles     Int      @default(0)
  interceptions Int?   @default(0)
  fouls       Int      @default(0)
  yellowCards Int      @default(0)
  redCards    Int      @default(0)
  
  rating      Decimal? @db.Decimal(3, 1)
  
  extraStats  Json?
  
  match       Match    @relation(fields: [matchId, tenantId], references: [id, tenantId], onDelete: Restrict)
  
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  @@unique([id, tenantId])
  @@map("match_statistics")
  @@index([matchId])
  @@index([playerId])
}
```

Run migration: `npx prisma migrate dev --name add_match_management`

### 4.2 Backend Module

Similar structure to scouting module. Key use cases:
- CreateMatchUseCase
- UpdateLineupUseCase
- RecordMatchEventUseCase (goal, card, substitution)
- UpdateMatchStatisticsUseCase
- ListMatchesUseCase (with filters: date range, competition, status)

**Critical Business Logic:**
- When recording a goal, automatically update match score
- When recording a substitution, update lineup JSON
- Validate that substituted player is in starting lineup
- Calculate match statistics aggregates from events

---

## Phase 5: Finance Module (Week 5-6)

### Goal
Build salary management, payroll, and financial tracking system.

### 5.1 Database Schema

**File**: `backend/prisma/schema.prisma`

```prisma
enum PaymentMethod {
  BANK_TRANSFER
  CASH
  CHECK
  DIGITAL_WALLET
}

enum InvoiceStatus {
  DRAFT
  SENT
  PAID
  OVERDUE
  CANCELLED
}

model SalaryPayment {
  id            String         @id @default(uuid()) @db.Uuid
  tenantId      String         @db.Uuid
  playerId      String         @db.Uuid
  contractId    String?        @db.Uuid
  
  periodStart   DateTime
  periodEnd     DateTime
  
  grossAmount   Decimal        @db.Decimal(14, 2)
  deductions    Decimal?       @db.Decimal(14, 2)
  netAmount     Decimal        @db.Decimal(14, 2)
  
  currency      Currency       @default(USD)
  
  paymentDate   DateTime?
  paymentMethod PaymentMethod?
  
  status        String         @db.VarChar(50) @default("PENDING")
  // PENDING, PROCESSED, PAID, FAILED
  
  notes         String?        @db.Text
  
  tenant        Tenant         @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  player        Player         @relation(fields: [playerId, tenantId], references: [id, tenantId], onDelete: Restrict)
  contract      Contract?      @relation(fields: [contractId, tenantId], references: [id, tenantId], onDelete: SetNull)
  
  createdAt     DateTime       @default(now())
  updatedAt     DateTime       @updatedAt
  
  @@unique([id, tenantId])
  @@map("salary_payments")
  @@index([tenantId])
  @@index([playerId])
  @@index([paymentDate])
  @@index([status])
}

model BonusPayment {
  id            String   @id @default(uuid()) @db.Uuid
  tenantId      String   @db.Uuid
  playerId      String   @db.Uuid
  contractId    String?  @db.Uuid
  
  bonusType     String   @db.VarChar(100)  // PERFORMANCE, LOYALTY, SIGNING, etc.
  description   String?  @db.Text
  
  amount        Decimal  @db.Decimal(14, 2)
  currency      Currency @default(USD)
  
  awardedDate   DateTime
  paymentDate   DateTime?
  
  status        String   @db.VarChar(50) @default("PENDING")
  
  tenant        Tenant   @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  player        Player   @relation(fields: [playerId, tenantId], references: [id, tenantId], onDelete: Restrict)
  contract      Contract? @relation(fields: [contractId, tenantId], references: [id, tenantId], onDelete: SetNull)
  
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  
  @@unique([id, tenantId])
  @@map("bonus_payments")
  @@index([tenantId])
  @@index([playerId])
}

model Invoice {
  id            String        @id @default(uuid()) @db.Uuid
  tenantId      String        @db.Uuid
  
  invoiceNumber String        @unique @db.VarChar(50)
  
  recipientType String        @db.VarChar(50)  // PLAYER, VENDOR, SPONSOR
  recipientId   String?       @db.Uuid
  
  recipientName String        @db.VarChar(255)
  recipientEmail String?      @db.VarChar(255)
  
  issueDate     DateTime
  dueDate       DateTime
  
  items         Json          // Array of line items
  
  subtotal      Decimal       @db.Decimal(14, 2)
  tax           Decimal?      @db.Decimal(14, 2)
  total         Decimal       @db.Decimal(14, 2)
  
  currency      Currency      @default(USD)
  
  status        InvoiceStatus @default(DRAFT)
  
  paidAt        DateTime?
  paymentMethod PaymentMethod?
  
  notes         String?       @db.Text
  
  tenant        Tenant        @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  
  createdAt     DateTime      @default(now())
  updatedAt     DateTime      @updatedAt
  
  @@unique([id, tenantId])
  @@map("invoices")
  @@index([tenantId])
  @@index([status])
  @@index([dueDate])
}

model TransferFee {
  id              String   @id @default(uuid()) @db.Uuid
  tenantId        String   @db.Uuid
  playerId        String   @db.Uuid
  
  fromClub        String   @db.VarChar(255)
  toClub          String   @db.VarChar(255)
  
  transferDate    DateTime
  
  feeAmount       Decimal  @db.Decimal(16, 2)
  currency        Currency @default(USD)
  
  paymentSchedule Json?    // Installment plan
  
  status          String   @db.VarChar(50) @default("PENDING")
  
  notes           String?  @db.Text
  
  tenant          Tenant   @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  player          Player   @relation(fields: [playerId, tenantId], references: [id, tenantId], onDelete: Restrict)
  
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  @@unique([id, tenantId])
  @@map("transfer_fees")
  @@index([tenantId])
  @@index([playerId])
}
```

Run migration: `npx prisma migrate dev --name add_finance_module`

### 5.2 Key Features to Implement

1. **Automated Salary Calculation**: Based on contract salary + period
2. **Payroll Generation**: Monthly batch processing
3. **Bonus Tracking**: Link to performance metrics
4. **Invoice Management**: CRUD with status workflow
5. **Financial Reports**: Export to CSV/PDF
6. **Budget Tracking**: Compare actual vs. budgeted expenses

---

## Phase 6: Automation Engine (Week 6-7)

### Goal
Build workflow automation system for scheduled tasks and triggers.

### 6.1 Database Schema

**File**: `backend/prisma/schema.prisma`

```prisma
enum AutomationTriggerType {
  SCHEDULED
  EVENT_BASED
  CONDITIONAL
}

enum AutomationStatus {
  ACTIVE
  PAUSED
  DISABLED
}

model AutomationRule {
  id            String               @id @default(uuid()) @db.Uuid
  tenantId      String               @db.Uuid
  
  name          String               @db.VarChar(255)
  description   String?              @db.Text
  
  triggerType   AutomationTriggerType
  triggerConfig Json                 // Cron expression or event config
  
  actions       Json                 // Array of actions to execute
  
  status        AutomationStatus     @default(ACTIVE)
  
  lastExecutedAt DateTime?
  nextRunAt     DateTime?
  
  metadata      Json?
  
  tenant        Tenant               @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  
  executionLogs AutomationExecutionLog[]
  
  createdAt     DateTime             @default(now())
  updatedAt     DateTime             @updatedAt
  
  @@unique([id, tenantId])
  @@map("automation_rules")
  @@index([tenantId])
  @@index([status])
  @@index([nextRunAt])
}

model AutomationExecutionLog {
  id            String   @id @default(uuid()) @db.Uuid
  tenantId      String   @db.Uuid
  ruleId        String   @db.Uuid
  
  executedAt    DateTime @default(now())
  status        String   @db.VarChar(50)  // SUCCESS, FAILED
  
  result        Json?
  errorMessage  String?  @db.Text
  
  duration      Int?     // milliseconds
  
  tenant        Tenant   @relation(fields: [tenantId], references: [id], onDelete: Restrict)
  rule          AutomationRule @relation(fields: [ruleId, tenantId], references: [id, tenantId], onDelete: Restrict)
  
  @@unique([id, tenantId])
  @@map("automation_execution_logs")
  @@index([ruleId])
  @@index([executedAt])
}
```

Run migration: `npx prisma migrate dev --name add_automation_engine`

### 6.2 Pre-built Automation Rules

**File**: `backend/src/modules/automation/application/services/default-automations.service.ts`

```typescript
export const DEFAULT_AUTOMATIONS = [
  {
    name: 'Contract Expiration Reminder',
    triggerType: 'SCHEDULED',
    triggerConfig: { cron: '0 9 * * *' }, // Daily at 9 AM
    actions: [
      {
        type: 'QUERY',
        entity: 'Contract',
        filter: { endDate: { lte: '+30 days' }, status: 'APPROVED' },
      },
      {
        type: 'NOTIFY',
        recipients: ['LEGAL', 'ADMIN'],
        template: 'contract_expiring_soon',
      },
    ],
  },
  {
    name: 'Injury Recovery Follow-up',
    triggerType: 'SCHEDULED',
    triggerConfig: { cron: '0 10 * * 1' }, // Every Monday at 10 AM
    actions: [
      {
        type: 'QUERY',
        entity: 'MedicalRecord',
        filter: { recoveryDate: { lte: '+7 days' }, returnToPlayDate: null },
      },
      {
        type: 'NOTIFY',
        recipients: ['MEDICAL', 'COACH'],
        template: 'injury_recovery_check',
      },
    ],
  },
  {
    name: 'Training Attendance Alert',
    triggerType: 'EVENT_BASED',
    triggerConfig: { event: 'attendance.marked_absent' },
    actions: [
      {
        type: 'NOTIFY',
        recipients: ['COACH', 'TRAINING_MANAGER'],
        template: 'player_absent_training',
      },
    ],
  },
];
```

### 6.3 Automation Processor

**File**: `backend/src/modules/automation/infrastructure/processors/automation.processor.ts`

```typescript
import { Processor, WorkerHost } from '@nestjs/bullmq';
import { Job } from 'bullmq';
import { AutomationService } from '../../application/services/automation.service';

@Processor('automation-queue')
export class AutomationProcessor extends WorkerHost {
  constructor(private automationService: AutomationService) {
    super();
  }

  async process(job: Job<any, any, string>): Promise<any> {
    const { ruleId } = job.data;
    
    try {
      await this.automationService.executeRule(ruleId);
      return { status: 'success' };
    } catch (error) {
      console.error(`Automation rule ${ruleId} failed:`, error);
      return { status: 'failed', error: error.message };
    }
  }
}
```

---

## Phase 7: Analytics & Reporting Dashboard (Week 7-8)

### Goal
Build comprehensive BI dashboards for different user roles.

### 7.1 Backend Analytics Service

**File**: `backend/src/modules/analytics/application/services/analytics.service.ts`

```typescript
@Injectable()
export class AnalyticsService {
  constructor(private prisma: PrismaService) {}

  async getOwnerDashboard(tenantId: string) {
    const [
      totalPlayers,
      activeContracts,
      expiringContracts,
      totalSalaryExpense,
      injuredPlayers,
      upcomingMatches,
    ] = await Promise.all([
      this.prisma.player.count({ where: { tenantId, deletedAt: null } }),
      this.prisma.contract.count({ 
        where: { tenantId, status: 'APPROVED', deletedAt: null } 
      }),
      this.prisma.contract.count({
        where: {
          tenantId,
          status: 'APPROVED',
          endDate: { lte: addMonths(new Date(), 3) },
        },
      }),
      this.prisma.contract.aggregate({
        where: { tenantId, status: 'APPROVED' },
        _sum: { salaryAmount: true },
      }),
      this.prisma.medicalRecord.count({
        where: {
          tenantId,
          recoveryDate: { gte: new Date() },
          deletedAt: null,
        },
      }),
      this.prisma.match.count({
        where: {
          tenantId,
          matchDate: { gte: new Date() },
          status: 'SCHEDULED',
        },
      }),
    ]);

    return {
      totalPlayers,
      activeContracts,
      expiringContracts: expiringContracts,
      monthlySalaryExpense: totalSalaryExpense._sum.salaryAmount || 0,
      injuredPlayers,
      upcomingMatches,
    };
  }

  async getCoachDashboard(tenantId: string) {
    // Training attendance rates
    // Player performance trends
    // Upcoming training sessions
    // Squad availability
  }

  async getScoutDashboard(tenantId: string) {
    // Active scouting assignments
    // Reports pending review
    // Watchlist size
    // Top recommendations
  }

  async exportReport(tenantId: string, reportType: string, filters: any) {
    // Generate CSV/PDF exports
  }
}
```

### 7.2 Frontend Dashboard Components

Create role-specific dashboards:
- `OwnerDashboard.tsx` - Financial overview, contracts, injuries
- `CoachDashboard.tsx` - Training, performance, squad availability
- `ScoutDashboard.tsx` - Assignments, reports, watchlist
- `MedicalDashboard.tsx` - Injured players, recovery progress
- `FinanceDashboard.tsx` - Payroll, invoices, budgets

---

## Phase 8: Polish & Integration (Week 8-9)

### Tasks

1. **Update All Existing Modules** to use new permission system
2. **Add Search Functionality** across all modules
3. **Implement Audit Trail** for critical operations
4. **Add Data Export** (CSV/Excel) for lists
5. **Mobile Responsiveness** testing and fixes
6. **Performance Optimization** (database indexes, query optimization)
7. **Error Handling** improvements
8. **Documentation** (API docs, user guides)

---

## Testing Strategy

### Unit Tests
- All use cases (business logic)
- Permission service
- Validation DTOs

### Integration Tests
- Controllers with real database
- Repository methods
- Event listeners

### E2E Tests
- Complete user flows (registration → create player → create contract → approve)
- Permission enforcement
- Multi-tenant isolation

---

## Deployment Checklist

Before production:
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Permissions seeded
- [ ] SSL certificates installed
- [ ] Rate limiting enabled
- [ ] Monitoring/logging setup (Sentry, LogRocket)
- [ ] Backup strategy in place
- [ ] Load testing completed

---

## Timeline Summary

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| 1. Permission System | Week 1-2 | Permission matrix, updated guards, seeder |
| 2. Role Expansion | Week 2-3 | 9 new roles, enhanced profiles |
| 3. Scouting Module | Week 3-4 | Reports, watchlists, assignments |
| 4. Match Management | Week 4-5 | Fixtures, lineups, events, stats |
| 5. Finance Module | Week 5-6 | Salaries, payroll, invoices |
| 6. Automation Engine | Week 6-7 | Scheduled tasks, workflows |
| 7. Analytics & BI | Week 7-8 | Dashboards, exports |
| 8. Polish & Integration | Week 8-9 | Search, audit, optimization |

**Total Estimated Time: 9 weeks**

---

## Success Metrics

After completion:
1. ✅ 17+ professional roles with granular permissions
2. ✅ Complete scouting pipeline with reports and watchlists
3. ✅ Full match management with lineups and statistics
4. ✅ Finance system handling salaries and invoices
5. ✅ Automation engine running scheduled tasks
6. ✅ Role-specific dashboards with key metrics
7. ✅ Enterprise-grade permission enforcement
8. ✅ Multi-tenant isolation verified
9. ✅ Comprehensive audit trails
10. ✅ Production-ready deployment configuration

---

## Risk Mitigation

**Risk**: Permission system complexity
**Mitigation**: Start with role-based, gradually add permissions. Provide admin UI to manage permissions.

**Risk**: Database migration conflicts
**Mitigation**: Test migrations on staging first. Keep rollback scripts.

**Risk**: Performance degradation with complex queries
**Mitigation**: Add proper indexes. Use pagination. Cache frequently accessed data with Redis.

**Risk**: Frontend-backend integration issues
**Mitigation**: Share TypeScript types between FE and BE. Use OpenAPI/Swagger for API documentation.

---

## Next Steps After Plan Approval

1. Start with Phase 1.1 (Database schema updates for permissions)
2. Run migration and verify tables created
3. Implement PermissionService
4. Update RolesGuard
5. Test with existing endpoints
6. Proceed to Phase 2 (Role expansion)
7. Continue sequentially through all phases
8. Test each phase before moving to next

This plan provides a clear, actionable roadmap to transform your platform into a complete football operations ERP system.
