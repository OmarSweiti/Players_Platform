# Football Management Platform - Architecture Setup

## Current State Analysis

**Backend (NestJS):**
- Basic NestJS project initialized
- Prisma schema defined with complete data model (1056 lines)
- PostgreSQL database configured
- No modules or features implemented yet

**Frontend (Next.js 16):**
- Next.js App Router initialized
- Tailwind CSS configured
- No features or pages implemented yet

---

## Phase 1: Backend Foundation Setup

### 1.1 Install Core Dependencies

Run in `backend/`:

```bash
npm install @nestjs/config @nestjs/jwt @nestjs/passport passport passport-jwt passport-local class-validator class-transformer @nestjs/swagger swagger-ui-express argon2 @nestjs/event-emitter bullmq @nestjs/bullmq ioredis multer @nestjs/platform-socket.io @nestjs/websockets socket.io aws-sdk uuid dayjs
```

Dev dependencies:
```bash
npm install --save-dev @types/passport-jwt @types/passport-local @types/multer @types/bcrypt @types/uuid
```

### 1.2 Create Project Structure

Create the following directory structure in `backend/src/`:

```
src/
├── common/
│   ├── decorators/
│   │   ├── public.decorator.ts
│   │   ├── roles.decorator.ts
│   │   └── current-user.decorator.ts
│   ├── guards/
│   │   ├── jwt-auth.guard.ts
│   │   ├── roles.guard.ts
│   │   └── tenant.guard.ts
│   ├── interceptors/
│   │   ├── transform.interceptor.ts
│   │   └── logging.interceptor.ts
│   ├── filters/
│   │   └── http-exception.filter.ts
│   ├── pipes/
│   │   └── validation.pipe.ts
│   └── interfaces/
│       ├── request-with-user.interface.ts
│       └── pagination.interface.ts
│
├── config/
│   ├── configuration.ts
│   ├── database.config.ts
│   ├── jwt.config.ts
│   └── redis.config.ts
│
├── infrastructure/
│   ├── prisma/
│   │   ├── prisma.module.ts
│   │   ├── prisma.service.ts
│   │   └── prisma.repository.ts (base repository)
│   ├── storage/
│   │   ├── storage.module.ts
│   │   ├── storage.service.ts (abstract)
│   │   ├── local.storage.service.ts
│   │   └── s3.storage.service.ts
│   ├── events/
│   │   ├── events.module.ts
│   │   └── event.service.ts
│   └── mail/
│       ├── mail.module.ts
│       └── mail.service.ts
│
├── modules/
│   ├── auth/
│   │   ├── application/
│   │   │   ├── use-cases/
│   │   │   │   ├── login.usecase.ts
│   │   │   │   ├── register.usecase.ts
│   │   │   │   ├── refresh-token.usecase.ts
│   │   │   │   └── logout.usecase.ts
│   │   │   └── services/
│   │   │       ├── auth.service.ts
│   │   │       └── password.service.ts (argon2 wrapper)
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── user.entity.ts
│   │   │   └── interfaces/
│   │   │       └── auth.interface.ts
│   │   ├── infrastructure/
│   │   │   ├── repositories/
│   │   │   │   └── user.repository.ts
│   │   │   └── strategies/
│   │   │       ├── jwt.strategy.ts
│   │   │       └── local.strategy.ts
│   │   └── presentation/
│   │       ├── auth.controller.ts
│   │       ├── dto/
│   │       │   ├── login.dto.ts
│   │       │   ├── register.dto.ts
│   │       │   └── refresh-token.dto.ts
│   │       └── responses/
│   │           └── auth.response.ts
│   │
│   ├── users/
│   │   ├── application/
│   │   │   ├── use-cases/
│   │   │   │   ├── get-user.usecase.ts
│   │   │   │   ├── update-user.usecase.ts
│   │   │   │   └── delete-user.usecase.ts
│   │   │   └── services/
│   │   │       └── user-management.service.ts
│   │   ├── domain/
│   │   │   └── entities/
│   │   │       └── user-profile.entity.ts
│   │   ├── infrastructure/
│   │   │   └── repositories/
│   │   │       └── user-profile.repository.ts
│   │   └── presentation/
│   │       ├── users.controller.ts
│   │       └── dto/
│   │
│   ├── players/
│   │   ├── application/
│   │   │   ├── use-cases/
│   │   │   │   ├── create-player.usecase.ts
│   │   │   │   ├── get-player.usecase.ts
│   │   │   │   ├── update-player.usecase.ts
│   │   │   │   ├── delete-player.usecase.ts
│   │   │   │   └── list-players.usecase.ts
│   │   │   └── services/
│   │   │       └── player-media.service.ts
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── player.entity.ts
│   │   │   └── enums/
│   │   │       └── player-position.enum.ts
│   │   ├── infrastructure/
│   │   │   └── repositories/
│   │   │       ├── player.repository.ts
│   │   │       └── player-media.repository.ts
│   │   └── presentation/
│   │       ├── players.controller.ts
│   │       └── dto/
│   │
│   ├── contracts/
│   │   ├── application/
│   │   │   ├── use-cases/
│   │   │   │   ├── create-contract.usecase.ts
│   │   │   │   ├── approve-contract.usecase.ts
│   │   │   │   ├── reject-contract.usecase.ts
│   │   │   │   ├── upload-contract-version.usecase.ts
│   │   │   │   └── get-contract-history.usecase.ts
│   │   │   └── services/
│   │   │       └── contract-validation.service.ts
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── contract.entity.ts
│   │   │   ├── enums/
│   │   │   │   └── contract-status.enum.ts
│   │   │   └── events/
│   │   │       ├── contract-created.event.ts
│   │   │       └── contract-approved.event.ts
│   │   ├── infrastructure/
│   │   │   └── repositories/
│   │   │       ├── contract.repository.ts
│   │   │       └── contract-version.repository.ts
│   │   └── presentation/
│   │       ├── contracts.controller.ts
│   │       └── dto/
│   │
│   ├── training/
│   │   ├── application/
│   │   │   ├── use-cases/
│   │   │   └── services/
│   │   ├── domain/
│   │   │   └── entities/
│   │   ├── infrastructure/
│   │   │   └── repositories/
│   │   └── presentation/
│   │       └── training.controller.ts
│   │
│   ├── performance/
│   │   └── ... (similar structure)
│   │
│   ├── legal/
│   │   └── ... (similar structure)
│   │
│   ├── chat/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   │   └── gateways/
│   │   │       └── chat.gateway.ts (WebSocket)
│   │   └── presentation/
│   │
│   └── notifications/
│       ├── application/
│       │   └── listeners/
│       │       ├── contract-event.listener.ts
│       │       ├── training-event.listener.ts
│       │       └── message-event.listener.ts
│       ├── infrastructure/
│       │   └── queues/
│       │       └── notification.processor.ts
│       └── presentation/
│           └── notifications.controller.ts
│
├── shared/
│   ├── types/
│   ├── utils/
│   └── constants/
│
├── app.module.ts
├── main.ts
└── health/
    └── health.controller.ts
```

### 1.3 Core Configuration Files

**`backend/src/config/configuration.ts`:**
```typescript
export default () => ({
  port: parseInt(process.env.PORT, 10) || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: process.env.JWT_EXPIRES_IN || '15m',
    refreshSecret: process.env.JWT_REFRESH_SECRET,
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d',
  },
  database: {
    url: process.env.DATABASE_URL,
  },
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT, 10) || 6379,
  },
  storage: {
    type: process.env.STORAGE_TYPE || 'local', // 'local' or 's3'
    localPath: process.env.LOCAL_STORAGE_PATH || './uploads',
    s3: {
      bucket: process.env.S3_BUCKET,
      region: process.env.S3_REGION,
      accessKeyId: process.env.S3_ACCESS_KEY_ID,
      secretAccessKey: process.env.S3_SECRET_ACCESS_KEY,
    },
  },
});
```

**`backend/src/infrastructure/prisma/prisma.module.ts`:**
```typescript
import { Global, Module } from '@nestjs/common';
import { PrismaService } from './prisma.service';

@Global()
@Module({
  providers: [PrismaService],
  exports: [PrismaService],
})
export class PrismaModule {}
```

**`backend/src/infrastructure/prisma/prisma.service.ts`:**
```typescript
import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
```

### 1.4 Authentication System

**Key files to create:**

**`backend/src/common/decorators/public.decorator.ts`:**
```typescript
import { SetMetadata } from '@nestjs/common';
export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);
```

**`backend/src/common/decorators/roles.decorator.ts`:**
```typescript
import { SetMetadata } from '@nestjs/common';
import { UserRole } from '@prisma/client';
export const ROLES_KEY = 'roles';
export const Roles = (...roles: UserRole[]) => SetMetadata(ROLES_KEY, roles);
```

**`backend/src/common/guards/jwt-auth.guard.ts`:**
```typescript
import { ExecutionContext, Injectable } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { AuthGuard } from '@nestjs/passport';
import { IS_PUBLIC_KEY } from '../decorators/public.decorator';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  constructor(private reflector: Reflector) {
    super();
  }

  canActivate(context: ExecutionContext) {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;
    return super.canActivate(context);
  }
}
```

**`backend/src/common/guards/roles.guard.ts`:**
```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { ROLES_KEY } from '../decorators/roles.decorator';
import { UserRole } from '@prisma/client';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<UserRole[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    
    if (!requiredRoles) return true;
    
    const { user } = context.switchToHttp().getRequest();
    const hasRole = requiredRoles.some(role => user.role === role);
    
    if (!hasRole) {
      throw new ForbiddenException('Insufficient permissions');
    }
    
    return true;
  }
}
```

**`backend/src/common/guards/tenant.guard.ts`:**
```typescript
import { Injectable, CanActivate, ExecutionContext, BadRequestException } from '@nestjs/common';

@Injectable()
export class TenantGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const tenantId = request.headers['x-tenant-id'] || request.user?.tenantId;
    
    if (!tenantId) {
      throw new BadRequestException('Tenant ID is required');
    }
    
    request.tenantId = tenantId;
    return true;
  }
}
```

**Password Service using Argon2:**

**`backend/src/modules/auth/application/services/password.service.ts`:**
```typescript
import { Injectable } from '@nestjs/common';
import * as argon2 from 'argon2';

@Injectable()
export class PasswordService {
  private readonly argon2Config = {
    type: argon2.argon2id,
    memoryCost: 65536,
    timeCost: 3,
    parallelism: 1,
  };

  async hash(password: string): Promise<string> {
    return argon2.hash(password, this.argon2Config);
  }

  async verify(hash: string, password: string): Promise<boolean> {
    return argon2.verify(hash, password);
  }
}
```

### 1.5 Base Repository Pattern

**`backend/src/infrastructure/prisma/prisma.repository.ts`:**
```typescript
import { Injectable } from '@nestjs/common';
import { PrismaService } from './prisma.service';

@Injectable()
export class PrismaRepository {
  constructor(protected prisma: PrismaService) {}

  protected addTenantFilter(query: any, tenantId: string) {
    return { ...query, where: { ...query.where, tenantId } };
  }
}
```

### 1.6 Event System with BullMQ

**`backend/src/infrastructure/events/events.module.ts`:**
```typescript
import { Module } from '@nestjs/common';
import { BullModule } from '@nestjs/bullmq';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { EventService } from './event.service';

@Module({
  imports: [
    BullModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (configService: ConfigService) => ({
        connection: {
          host: configService.get('redis.host'),
          port: configService.get('redis.port'),
        },
      }),
      inject: [ConfigService],
    }),
    BullModule.registerQueue({
      name: 'notifications',
    }),
    BullModule.registerQueue({
      name: 'audit-logs',
    }),
  ],
  providers: [EventService],
  exports: [EventService],
})
export class EventsModule {}
```

**`backend/src/infrastructure/events/event.service.ts`:**
```typescript
import { Injectable } from '@nestjs/common';
import { InjectQueue } from '@nestjs/bullmq';
import { Queue } from 'bullmq';

@Injectable()
export class EventService {
  constructor(
    @InjectQueue('notifications') private notificationQueue: Queue,
    @InjectQueue('audit-logs') private auditLogQueue: Queue,
  ) {}

  async emitNotification(data: any) {
    await this.notificationQueue.add('send-notification', data);
  }

  async emitAuditLog(data: any) {
    await this.auditLogQueue.add('create-audit-log', data);
  }
}
```

### 1.7 File Storage Abstraction

**`backend/src/infrastructure/storage/storage.service.ts`:**
```typescript
import { Injectable } from '@nestjs/common';

export interface UploadResult {
  url: string;
  key: string;
}

@Injectable()
export abstract class StorageService {
  abstract upload(file: Express.Multer.File, folder: string): Promise<UploadResult>;
  abstract delete(key: string): Promise<void>;
  abstract getUrl(key: string): string;
}
```

**`backend/src/infrastructure/storage/local.storage.service.ts`:**
```typescript
import { Injectable } from '@nestjs/common';
import { StorageService, UploadResult } from './storage.service';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class LocalStorageService implements StorageService {
  private uploadPath: string;

  constructor() {
    this.uploadPath = path.join(process.cwd(), 'uploads');
    if (!fs.existsSync(this.uploadPath)) {
      fs.mkdirSync(this.uploadPath, { recursive: true });
    }
  }

  async upload(file: Express.Multer.File, folder: string): Promise<UploadResult> {
    const key = `${folder}/${uuidv4()}-${file.originalname}`;
    const filePath = path.join(this.uploadPath, key);
    
    await fs.promises.mkdir(path.dirname(filePath), { recursive: true });
    await fs.promises.writeFile(filePath, file.buffer);
    
    return {
      url: `/uploads/${key}`,
      key,
    };
  }

  async delete(key: string): Promise<void> {
    const filePath = path.join(this.uploadPath, key);
    await fs.promises.unlink(filePath);
  }

  getUrl(key: string): string {
    return `/uploads/${key}`;
  }
}
```

### 1.8 Main Application Module

**Updated `backend/src/app.module.ts`:**
```typescript
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { APP_GUARD, APP_INTERCEPTOR, APP_FILTER } from '@nestjs/core';
import configuration from './config/configuration';
import { PrismaModule } from './infrastructure/prisma/prisma.module';
import { EventsModule } from './infrastructure/events/events.module';
import { AuthModule } from './modules/auth/auth.module';
import { UsersModule } from './modules/users/users.module';
import { PlayersModule } from './modules/players/players.module';
import { ContractsModule } from './modules/contracts/contracts.module';
import { TrainingModule } from './modules/training/training.module';
import { PerformanceModule } from './modules/performance/performance.module';
import { LegalModule } from './modules/legal/legal.module';
import { ChatModule } from './modules/chat/chat.module';
import { NotificationsModule } from './modules/notifications/notifications.module';
import { JwtAuthGuard } from './common/guards/jwt-auth.guard';
import { TransformInterceptor } from './common/interceptors/transform.interceptor';
import { HttpExceptionFilter } from './common/filters/http-exception.filter';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
    }),
    PrismaModule,
    EventsModule,
    AuthModule,
    UsersModule,
    PlayersModule,
    ContractsModule,
    TrainingModule,
    PerformanceModule,
    LegalModule,
    ChatModule,
    NotificationsModule,
  ],
  providers: [
    { provide: APP_GUARD, useClass: JwtAuthGuard },
    { provide: APP_INTERCEPTOR, useClass: TransformInterceptor },
    { provide: APP_FILTER, useClass: HttpExceptionFilter },
  ],
})
export class AppModule {}
```

### 1.9 Environment Variables Template

Create `backend/.env.example`:
```env
# Server
PORT=3000
NODE_ENV=development

# Database
DATABASE_URL="postgresql://postgres:password@localhost:5432/players_platform?schema=public"

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRES_IN=15m
JWT_REFRESH_SECRET=your-super-secret-refresh-key-change-in-production
JWT_REFRESH_EXPIRES_IN=7d

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Storage (local or s3)
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./uploads

# S3 (if STORAGE_TYPE=s3)
S3_BUCKET=your-bucket
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key

# CORS
CORS_ORIGIN=http://localhost:3001
```

---

## Phase 2: Frontend Foundation Setup

### 2.1 Install Core Dependencies

Run in `frontend/`:

```bash
npm install @tanstack/react-query axios zustand date-fns lucide-react next-themes react-hook-form @hookform/resolvers zod clsx tailwind-merge @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-select @radix-ui/react-tabs @radix-ui/react-toast @radix-ui/react-avatar @radix-ui/react-label class-variance-authority
```

### 2.2 Create Frontend Structure

```
frontend/src/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   │
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── page.tsx (dashboard home)
│   │   ├── players/
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx
│   │   │   └── new/
│   │   │       └── page.tsx
│   │   ├── contracts/
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── training/
│   │   │   └── page.tsx
│   │   ├── performance/
│   │   │   └── page.tsx
│   │   ├── legal/
│   │   │   └── page.tsx
│   │   ├── chat/
│   │   │   └── page.tsx
│   │   └── settings/
│   │       └── page.tsx
│   │
│   ├── api/
│   │   └── auth/
│   │       ├── [...nextauth]/
│   │       └── route.ts
│   │
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
│
├── features/
│   ├── auth/
│   │   ├── api/
│   │   │   └── auth.api.ts
│   │   ├── components/
│   │   │   ├── login-form.tsx
│   │   │   └── register-form.tsx
│   │   ├── hooks/
│   │   │   └── use-auth.ts
│   │   └── types/
│   │       └── auth.types.ts
│   │
│   ├── players/
│   │   ├── api/
│   │   │   └── players.api.ts
│   │   ├── components/
│   │   │   ├── player-card.tsx
│   │   │   ├── player-list.tsx
│   │   │   ├── player-form.tsx
│   │   │   └── player-stats.tsx
│   │   ├── hooks/
│   │   │   ├── use-players.ts
│   │   │   └── use-player.ts
│   │   └── types/
│   │       └── player.types.ts
│   │
│   ├── contracts/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── types/
│   │
│   ├── training/
│   │   └── ... (similar structure)
│   │
│   ├── performance/
│   │   └── ... (similar structure)
│   │
│   ├── legal/
│   │   └── ... (similar structure)
│   │
│   └── chat/
│       └── ... (similar structure)
│
├── shared/
│   ├── ui/
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── table.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── select.tsx
│   │   ├── tabs.tsx
│   │   ├── toast.tsx
│   │   ├── avatar.tsx
│   │   ├── label.tsx
│   │   └── index.ts
│   │
│   ├── lib/
│   │   ├── api-client.ts
│   │   ├── utils.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   ├── hooks/
│   │   ├── use-debounce.ts
│   │   ├── use-local-storage.ts
│   │   └── use-media-query.ts
│   │
│   ├── contexts/
│   │   └── tenant-context.tsx
│   │
│   └── types/
│       ├── api.types.ts
│       └── common.types.ts
│
├── components/
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   ├── providers/
│   │   ├── query-provider.tsx
│   │   ├── theme-provider.tsx
│   │   └── auth-provider.tsx
│   └── shared/
│       ├── loading-spinner.tsx
│       ├── error-boundary.tsx
│       └── empty-state.tsx
│
├── config/
│   └── site.ts
│
└── middleware.ts
```

### 2.3 API Client Setup

**`frontend/src/shared/lib/api-client.ts`:**
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add tenant ID to requests
apiClient.interceptors.request.use((config) => {
  const tenantId = localStorage.getItem('tenantId');
  if (tenantId) {
    config.headers['X-Tenant-ID'] = tenantId;
  }
  return config;
});

// Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`,
          {},
          { withCredentials: true }
        );
        
        return apiClient(originalRequest);
      } catch (refreshError) {
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 2.4 React Query Provider

**`frontend/src/components/providers/query-provider.tsx`:**
```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

### 2.5 Middleware for Route Protection

**`frontend/middleware.ts`:**
```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const protectedRoutes = ['/dashboard', '/players', '/contracts', '/training'];
const authRoutes = ['/login', '/register'];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('accessToken');
  const pathname = request.nextUrl.pathname;

  // Redirect to login if accessing protected route without token
  if (protectedRoutes.some(route => pathname.startsWith(route)) && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Redirect to dashboard if accessing auth routes with token
  if (authRoutes.includes(pathname) && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

### 2.6 Environment Variables

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:3000/api
NEXT_PUBLIC_APP_NAME=Players Platform
```

---

## Phase 3: First Feature Implementation - Auth Module

### 3.1 Backend Auth Module Structure

Create these files in order:

1. **DTOs** (`backend/src/modules/auth/presentation/dto/`)
2. **Use Cases** (`backend/src/modules/auth/application/use-cases/`)
3. **Repository** (`backend/src/modules/auth/infrastructure/repositories/`)
4. **Strategies** (`backend/src/modules/auth/infrastructure/strategies/`)
5. **Controller** (`backend/src/modules/auth/presentation/auth.controller.ts`)
6. **Module** (`backend/src/modules/auth/auth.module.ts`)

### 3.2 Key Implementation Details

**Login Use Case Example:**

**`backend/src/modules/auth/application/use-cases/login.usecase.ts`:**
```typescript
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { UserRepository } from '../../infrastructure/repositories/user.repository';
import { PasswordService } from '../services/password.service';
import { LoginDto } from '../../presentation/dto/login.dto';

@Injectable()
export class LoginUseCase {
  constructor(
    private userRepository: UserRepository,
    private passwordService: PasswordService,
    private jwtService: JwtService,
  ) {}

  async execute(dto: LoginDto, tenantId: string) {
    const user = await this.userRepository.findByEmail(dto.email, tenantId);
    
    if (!user) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const isValid = await this.passwordService.verify(user.passwordHash, dto.password);
    
    if (!isValid) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const tokens = this.generateTokens(user);
    
    await this.userRepository.updateLastLogin(user.id);

    return tokens;
  }

  private generateTokens(user: any) {
    const payload = {
      sub: user.id,
      email: user.email,
      role: user.role,
      tenantId: user.tenantId,
    };

    return {
      accessToken: this.jwtService.sign(payload, { expiresIn: '15m' }),
      refreshToken: this.jwtService.sign(payload, { 
        secret: process.env.JWT_REFRESH_SECRET,
        expiresIn: '7d' 
      }),
    };
  }
}
```

---

## Phase 4: Development Roadmap Execution

Follow this sequence strictly:

### Week 1: Foundation (Days 1-7)
**Day 1-2:**
- [ ] Install all backend dependencies
- [ ] Create directory structure
- [ ] Set up Prisma module and service
- [ ] Configure environment variables
- [ ] Test database connection

**Day 3-4:**
- [ ] Implement PasswordService with Argon2
- [ ] Create UserRepository
- [ ] Implement JWT and Local strategies
- [ ] Create guards (JwtAuth, Roles, Tenant)
- [ ] Build LoginUseCase and RegisterUseCase
- [ ] Create AuthController with endpoints
- [ ] Test authentication flow with Postman/curl

**Day 5-7:**
- [ ] Set up frontend dependencies
- [ ] Create API client with interceptors
- [ ] Implement auth forms (login/register)
- [ ] Set up React Query provider
- [ ] Create middleware for route protection
- [ ] Test end-to-end authentication

### Week 2: Player Module (Days 8-14)
- [ ] Create Player entity and repository
- [ ] Implement CRUD use cases
- [ ] Build PlayerController with RBAC
- [ ] Create frontend player components
- [ ] Implement player list and detail views
- [ ] Add player creation form
- [ ] Test player management flow

### Week 3: Contract Module (Days 15-21)
- [ ] Implement contract versioning logic
- [ ] Create approval workflow use cases
- [ ] Build contract status machine
- [ ] Add event emitters for contract events
- [ ] Create notification listeners
- [ ] Build frontend contract UI
- [ ] Test complete contract lifecycle

### Week 4+: Remaining Features
Continue with training, performance, legal, chat, and notifications following the same pattern.

---

## Critical Implementation Notes

### Security Checklist
- [ ] All passwords hashed with Argon2id before storage
- [ ] JWT tokens stored in HTTP-only cookies (not localStorage)
- [ ] Every query includes tenantId filter
- [ ] Role-based access control on all endpoints
- [ ] Input validation with class-validator on all DTOs
- [ ] Rate limiting on auth endpoints (add later)
- [ ] CORS properly configured

### Multi-Tenancy Enforcement
Every repository method MUST include tenantId:
```typescript
async findById(id: string, tenantId: string) {
  return this.prisma.player.findUnique({
    where: { id, tenantId }, // CRITICAL: always filter by tenant
  });
}
```

### Event-Driven Pattern
Use events for side effects:
```typescript
// In contract approval use case
await this.contractRepository.approve(contractId);
this.eventEmitter.emit('contract.approved', { contractId, playerId });

// In notification listener
@OnEvent('contract.approved')
async handleContractApproved(payload: any) {
  await this.notificationService.create({...});
}
```

### Error Handling
Standardized error responses via HttpExceptionFilter:
```typescript
{
  statusCode: 400,
  message: 'Validation failed',
  errors: [...],
  timestamp: '2026-05-06T...'
}
```

---

## Testing Strategy

### Backend Testing
- Unit tests for all use cases
- Integration tests for controllers
- E2E tests for critical flows (auth, contract approval)

### Frontend Testing
- Component tests for UI components
- Integration tests for forms
- E2E tests with Playwright/Cypress

---

## Deployment Considerations (Future)

### Infrastructure Requirements
- PostgreSQL database (managed service recommended)
- Redis instance for BullMQ
- S3 bucket or compatible storage
- Node.js runtime (Docker containers)
- Load balancer for horizontal scaling

### Environment-Specific Configs
- Development: Local everything
- Staging: Managed DB + Redis, local storage
- Production: Fully managed services, S3 storage

---

## Success Metrics

After completing this architecture setup:
1. ✅ User can register and login with JWT authentication
2. ✅ All routes protected by tenant isolation
3. ✅ Role-based access control working
4. ✅ File uploads working with abstraction layer
5. ✅ Event system emitting and processing events
6. ✅ Clean architecture with separated concerns
7. ✅ Frontend consuming backend APIs with React Query
8. ✅ Type-safe communication between FE and BE

---

## Next Steps After Plan Approval

1. Start with Phase 1.1 (Install Dependencies)
2. Follow the directory structure creation
3. Implement core infrastructure (Prisma, Config, Events)
4. Build Auth module completely before moving to other features
5. Test each component as you build it
6. Document any deviations from this plan

This architecture provides a solid foundation for your football management platform while maintaining flexibility for future enhancements like WebSockets, microservices, and advanced search capabilities.