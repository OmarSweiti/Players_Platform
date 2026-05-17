# Professional Logging Implementation Guide

**Date:** May 10, 2026  
**Status:** ⚠️ **PARTIALLY IMPLEMENTED** - Needs Enhancement

---

## Current Logging Status

### ❌ Problem Identified

Your authentication module has **NO professional logging**. The current implementation uses:
- `console.log()` in interceptors (basic, not structured)
- No Logger instances in auth use cases
- No audit trail for security events
- No error tracking or monitoring integration

### ✅ What Exists Elsewhere

Only these services have proper logging:
- `PrismaService` - Database connection logs
- `MailService` - Email sending logs

**Authentication & Authorization is missing critical logging!**

---

## Why Logging Matters for Authentication

### Security Requirements
1. **Audit Trail**: Track all login attempts (successful/failed)
2. **Compliance**: GDPR, SOC2, ISO 27001 require auth logging
3. **Incident Response**: Detect brute force attacks, suspicious activity
4. **Debugging**: Troubleshoot authentication issues
5. **Monitoring**: Track authentication success rates, performance

### What to Log
- ✅ Login attempts (success/failure)
- ✅ Failed password attempts
- ✅ Account lockouts
- ✅ Password changes
- ✅ Password reset requests
- ✅ Email verification
- ✅ 2FA enable/disable
- ✅ Token refresh events
- ✅ Permission checks (optional, can be verbose)
- ❌ **NEVER log**: Passwords, tokens, sensitive data

---

## Professional Logging Implementation

### Step 1: Add Logger to All Auth Use Cases

#### Example: LoginUseCase with Logging

**File:** `backend/src/modules/auth/application/use-cases/login.usecase.ts`

```typescript
import { Injectable, UnauthorizedException, Logger } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { UserRepository } from '../../infrastructure/repositories/user.repository';
import { PasswordService } from '../services/password.service';
import { LoginDto } from '../../presentation/dto/login.dto';

@Injectable()
export class LoginUseCase {
  private readonly logger = new Logger(LoginUseCase.name);

  constructor(
    private userRepository: UserRepository,
    private passwordService: PasswordService,
    private jwtService: JwtService,
  ) {}

  async validateUser(email: string, password: string, tenantId: string): Promise<any> {
    const user = await this.userRepository.findByEmail(email, tenantId);
    
    if (!user) {
      // SECURITY: Log failed login attempt (don't reveal if email exists)
      this.logger.warn(`Failed login attempt for email: ${email} (user not found)`);
      return null;
    }

    // Check if account is locked
    if (user.lockedUntil && new Date() < user.lockedUntil) {
      this.logger.warn(
        `Login blocked - Account locked: ${user.email} (locked until: ${user.lockedUntil})`,
      );
      throw new UnauthorizedException('Account is temporarily locked due to too many failed attempts');
    }

    const isValid = await this.passwordService.verify(user.passwordHash, password);
    
    if (!isValid) {
      this.logger.warn(`Invalid password for user: ${user.email}`);
      await this.handleFailedLogin(user.id);
      return null;
    }

    return user;
  }

  async execute(dto: LoginDto, tenantId: string) {
    const startTime = Date.now();
    
    try {
      const user = await this.validateUser(dto.email, dto.password, tenantId);
      
      if (!user) {
        const duration = Date.now() - startTime;
        this.logger.warn(`Login failed for ${dto.email} after ${duration}ms`);
        throw new UnauthorizedException('Invalid credentials');
      }

      const tokens = this.generateTokens(user);
      
      await this.userRepository.updateLastLogin(user.id);

      const duration = Date.now() - startTime;
      this.logger.log(`Successful login: ${user.email} (tenant: ${tenantId}, duration: ${duration}ms)`);

      return {
        user: {
          id: user.id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          role: user.role,
          tenantId: user.tenantId,
        },
        ...tokens,
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      this.logger.error(`Login error for ${dto.email}: ${error.message}`, error.stack);
      throw error;
    }
  }

  private async handleFailedLogin(userId: string) {
    const user = await this.userRepository.incrementFailedLoginAttempts(userId);
    
    this.logger.warn(
      `Failed login attempt #${user.failedLoginAttempts} for user ID: ${userId}`,
    );
    
    // Lock account after 5 failed attempts
    if (user.failedLoginAttempts >= 5) {
      const lockedUntil = new Date();
      lockedUntil.setMinutes(lockedUntil.getMinutes() + 30);
      await this.userRepository.lockAccount(userId, lockedUntil);
      
      this.logger.warn(
        `Account LOCKED: User ID ${userId} locked until ${lockedUntil.toISOString()}`,
      );
    }
  }

  private generateTokens(user: any) {
    const payload = {
      sub: user.id,
      email: user.email,
      role: user.role,
      tenantId: user.tenantId,
    };

    return {
      accessToken: this.jwtService.sign(payload),
      refreshToken: this.jwtService.sign(payload, {
        secret: process.env.JWT_REFRESH_SECRET,
        expiresIn: '7d',
      }),
    };
  }
}
```

---

### Step 2: Add Logging to All Auth Endpoints

#### RegisterUseCase

```typescript
import { Injectable, ConflictException, BadRequestException, Logger } from '@nestjs/common';
import * as crypto from 'crypto';
import { UserRepository } from '../../infrastructure/repositories/user.repository';
import { PasswordService } from '../services/password.service';
import { MailService } from '../../../../infrastructure/mail/mail.service';
import { RegisterDto } from '../../presentation/dto/register.dto';

@Injectable()
export class RegisterUseCase {
  private readonly logger = new Logger(RegisterUseCase.name);

  constructor(
    private userRepository: UserRepository,
    private passwordService: PasswordService,
    private mailService: MailService,
  ) {}

  async execute(dto: RegisterDto, tenantId: string) {
    const startTime = Date.now();
    
    try {
      // Check if user already exists
      const existingUser = await this.userRepository.findByEmail(dto.email, tenantId);
      
      if (existingUser) {
        this.logger.warn(`Registration attempt with existing email: ${dto.email}`);
        throw new ConflictException('User with this email already exists');
      }

      // Validate password strength
      this.validatePasswordStrength(dto.password);

      // Hash password
      const passwordHash = await this.passwordService.hash(dto.password);

      // Generate email verification token
      const verificationToken = crypto.randomBytes(32).toString('hex');
      const verificationTokenExpiry = new Date();
      verificationTokenExpiry.setHours(verificationTokenExpiry.getHours() + 24);

      // Create user
      const user = await this.userRepository.create({
        email: dto.email,
        passwordHash,
        role: dto.role || 'PLAYER', // Default role
        firstName: dto.firstName,
        lastName: dto.lastName,
        phone: dto.phone,
        tenantId,
        emailVerificationToken: verificationToken,
        emailVerificationExpiry: verificationTokenExpiry,
      });

      // Send verification email
      await this.mailService.sendVerificationEmail(user.email, verificationToken);

      const duration = Date.now() - startTime;
      this.logger.log(
        `New user registered: ${user.email} (tenant: ${tenantId}, role: ${user.role}, duration: ${duration}ms)`,
      );

      return {
        message: 'Registration successful. Please check your email to verify your account.',
        userId: user.id,
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      this.logger.error(
        `Registration failed for ${dto.email}: ${error.message}`,
        error.stack,
      );
      throw error;
    }
  }

  private validatePasswordStrength(password: string): void {
    // ... validation logic
  }
}
```

---

### Step 3: Enhanced Logging Interceptor

**File:** `backend/src/common/interceptors/logging.interceptor.ts`

Replace basic console.log with structured logging:

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger('HTTP');

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const response = context.switchToHttp().getResponse();
    
    const method = request.method;
    const url = request.url;
    const ip = request.ip || request.headers['x-forwarded-for'];
    const userAgent = request.headers['user-agent'];
    const tenantId = request.headers['x-tenant-id'] || 'N/A';
    
    const now = Date.now();
    const requestId = this.generateRequestId();

    // Log incoming request
    this.logger.log(
      `[${requestId}] ${method} ${url} | IP: ${ip} | Tenant: ${tenantId}`,
    );

    return next.handle().pipe(
      tap(() => {
        const statusCode = response.statusCode;
        const responseTime = Date.now() - now;

        // Log successful response
        this.logger.log(
          `[${requestId}] ${method} ${url} - ${statusCode} - ${responseTime}ms`,
        );

        // Warn on slow requests (>1000ms)
        if (responseTime > 1000) {
          this.logger.warn(
            `[${requestId}] SLOW REQUEST: ${method} ${url} took ${responseTime}ms`,
          );
        }
      }),
      catchError((error) => {
        const responseTime = Date.now() - now;
        const statusCode = error.status || 500;

        // Log error
        this.logger.error(
          `[${requestId}] ${method} ${url} - ${statusCode} - ${responseTime}ms | Error: ${error.message}`,
          error.stack,
        );

        throw error;
      }),
    );
  }

  private generateRequestId(): string {
    return Math.random().toString(36).substring(2, 15);
  }
}
```

---

### Step 4: Apply Logging Interceptor Globally

**File:** `backend/src/main.ts`

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe, Logger } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import helmet from 'helmet';
import compression from 'compression';
import { AppModule } from './app.module';
import { ConfigService } from '@nestjs/config';
import { LoggingInterceptor } from './common/interceptors/logging.interceptor';
import { TransformInterceptor } from './common/interceptors/transform.interceptor';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const configService = app.get(ConfigService);
  const logger = new Logger('Bootstrap');

  // Apply global interceptors
  app.useGlobalInterceptors(new LoggingInterceptor());
  app.useGlobalInterceptors(new TransformInterceptor());

  // ... rest of bootstrap code

  const port = configService.get<number>('app.port') || 3000;
  await app.listen(port);
  
  logger.log(`Application is running on: http://localhost:${port}`);
  logger.log(`API Documentation: http://localhost:${port}/docs`);
  logger.log(`Health Check: http://localhost:${port}/api/health`);
}
bootstrap();
```

---

## Advanced Logging Strategies

### Option 1: Winston (Production-Ready)

Install Winston for advanced logging:

```bash
npm install nest-winston winston winston-daily-rotate-file
```

**File:** `backend/src/config/logger.config.ts`

```typescript
import { utilities as nestWinstonModuleUtilities, WinstonModule } from 'nest-winston';
import * as winston from 'winston';
import 'winston-daily-rotate-file';

export const createLogger = () => {
  const isProduction = process.env.NODE_ENV === 'production';

  const transports: winston.transport[] = [
    // Console transport
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.ms(),
        nestWinstonModuleUtilities.format.nestLike('FootballPlatform', {
          colors: !isProduction,
          prettyPrint: true,
        }),
      ),
    }),
  ];

  // File transports (only in production)
  if (isProduction) {
    // Error log file
    transports.push(
      new winston.transports.DailyRotateFile({
        filename: 'logs/error-%DATE%.log',
        datePattern: 'YYYY-MM-DD',
        level: 'error',
        maxFiles: '30d', // Keep logs for 30 days
        maxSize: '20m', // 20MB per file
        zippedArchive: true,
      }),
    );

    // Combined log file
    transports.push(
      new winston.transports.DailyRotateFile({
        filename: 'logs/combined-%DATE%.log',
        datePattern: 'YYYY-MM-DD',
        maxFiles: '30d',
        maxSize: '20m',
        zippedArchive: true,
      }),
    );
  }

  return WinstonModule.createLogger({
    transports,
    level: isProduction ? 'info' : 'debug',
  });
};
```

**File:** `backend/src/main.ts`

```typescript
import { createLogger } from './config/logger.config';

async function bootstrap() {
  const logger = createLogger();
  const app = await NestFactory.create(AppModule, {
    logger, // Use Winston logger
  });
  
  // ... rest of bootstrap
}
```

---

### Option 2: Sentry Integration (Error Tracking)

For production error tracking and monitoring:

```bash
npm install @sentry/node @sentry/nestjs
```

**File:** `backend/src/main.ts`

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
});

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Sentry error handler
  app.use(Sentry.Handlers.requestHandler());
  
  // ... rest of bootstrap
  
  app.use(Sentry.Handlers.errorHandler());
}
```

---

## Logging Best Practices

### ✅ DO

1. **Log Security Events**
   ```typescript
   this.logger.log(`Successful login: ${user.email}`);
   this.logger.warn(`Failed login attempt: ${email}`);
   this.logger.warn(`Account locked: ${userId}`);
   ```

2. **Include Context**
   ```typescript
   this.logger.log(`Action completed`, {
     userId: user.id,
     tenantId: user.tenantId,
     action: 'login',
     timestamp: new Date().toISOString(),
   });
   ```

3. **Use Appropriate Log Levels**
   - `logger.log()` - Normal operations
   - `logger.debug()` - Detailed debugging info
   - `logger.warn()` - Unexpected but handled situations
   - `logger.error()` - Errors that need attention
   - `logger.fatal()` - Critical errors causing shutdown

4. **Log Performance Metrics**
   ```typescript
   const duration = Date.now() - startTime;
   this.logger.log(`Operation completed in ${duration}ms`);
   ```

### ❌ DON'T

1. **Never Log Sensitive Data**
   ```typescript
   // ❌ BAD - Logs password
   this.logger.log(`Login with password: ${password}`);
   
   // ✅ GOOD - Log without sensitive data
   this.logger.log(`Login attempt for user: ${email}`);
   ```

2. **Don't Log Tokens**
   ```typescript
   // ❌ BAD
   this.logger.log(`Generated token: ${accessToken}`);
   
   // ✅ GOOD
   this.logger.log(`Access token generated for user: ${userId}`);
   ```

3. **Avoid Excessive Logging**
   ```typescript
   // ❌ BAD - Too verbose
   this.logger.debug(`Processing request...`);
   this.logger.debug(`Validating input...`);
   this.logger.debug(`Checking database...`);
   
   // ✅ GOOD - Log meaningful events only
   this.logger.log(`Request processed successfully`);
   ```

---

## Audit Logging for Compliance

Create a dedicated audit log service:

**File:** `backend/src/modules/auth/application/services/audit-log.service.ts`

```typescript
import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../../../infrastructure/prisma/prisma.service';

export enum AuditAction {
  LOGIN_SUCCESS = 'LOGIN_SUCCESS',
  LOGIN_FAILED = 'LOGIN_FAILED',
  REGISTER = 'USER_REGISTERED',
  PASSWORD_CHANGE = 'PASSWORD_CHANGED',
  PASSWORD_RESET_REQUEST = 'PASSWORD_RESET_REQUESTED',
  EMAIL_VERIFIED = 'EMAIL_VERIFIED',
  TWO_FA_ENABLED = 'TWO_FA_ENABLED',
  TWO_FA_DISABLED = 'TWO_FA_DISABLED',
  ACCOUNT_LOCKED = 'ACCOUNT_LOCKED',
}

@Injectable()
export class AuditLogService {
  constructor(private prisma: PrismaService) {}

  async logAuditEvent(data: {
    userId?: string;
    tenantId: string;
    action: AuditAction;
    entityType: string;
    entityId: string;
    ipAddress?: string;
    userAgent?: string;
    metadata?: any;
  }) {
    await this.prisma.auditLog.create({
      data: {
        userId: data.userId,
        tenantId: data.tenantId,
        action: data.action,
        entityType: data.entityType,
        entityId: data.entityId,
        ipAddress: data.ipAddress,
        userAgent: data.userAgent,
        newValues: data.metadata,
      },
    });
  }
}
```

**Usage in LoginUseCase:**

```typescript
constructor(
  private userRepository: UserRepository,
  private passwordService: PasswordService,
  private jwtService: JwtService,
  private auditLogService: AuditLogService, // Inject audit service
) {}

async execute(dto: LoginDto, tenantId: string, request: any) {
  const user = await this.validateUser(dto.email, dto.password, tenantId);
  
  if (!user) {
    // Log failed login to audit table
    await this.auditLogService.logAuditEvent({
      tenantId,
      action: AuditAction.LOGIN_FAILED,
      entityType: 'User',
      entityId: 'unknown',
      ipAddress: request.ip,
      userAgent: request.headers['user-agent'],
      metadata: { email: dto.email, reason: 'invalid_credentials' },
    });
    
    throw new UnauthorizedException('Invalid credentials');
  }

  // Log successful login to audit table
  await this.auditLogService.logAuditEvent({
    userId: user.id,
    tenantId,
    action: AuditAction.LOGIN_SUCCESS,
    entityType: 'User',
    entityId: user.id,
    ipAddress: request.ip,
    userAgent: request.headers['user-agent'],
  });

  // ... rest of logic
}
```

---

## Monitoring & Alerting

### Key Metrics to Track

1. **Authentication Success Rate**
   - Monitor ratio of successful vs failed logins
   - Alert if failure rate spikes (>20%)

2. **Account Lockouts**
   - Track number of locked accounts
   - Alert on unusual patterns

3. **Response Times**
   - Monitor auth endpoint latency
   - Alert if >500ms consistently

4. **Geographic Anomalies**
   - Detect logins from unusual locations
   - Alert on impossible travel scenarios

### Integration with Monitoring Tools

- **Datadog**: Send logs and metrics
- **New Relic**: Application performance monitoring
- **Prometheus + Grafana**: Custom dashboards
- **ELK Stack**: Elasticsearch, Logstash, Kibana for log aggregation

---

## Implementation Checklist

### Phase 1: Basic Logging (1-2 days)
- [ ] Add Logger to all auth use cases
- [ ] Enhance logging interceptor
- [ ] Apply interceptor globally
- [ ] Test log output in development

### Phase 2: Structured Logging (2-3 days)
- [ ] Install and configure Winston
- [ ] Set up file rotation
- [ ] Add request IDs for tracing
- [ ] Implement JSON logging for production

### Phase 3: Audit Logging (2-3 days)
- [ ] Create AuditLogService
- [ ] Integrate with all auth events
- [ ] Add audit log query endpoints
- [ ] Create admin UI for viewing audit logs

### Phase 4: Monitoring (3-5 days)
- [ ] Integrate with Sentry (error tracking)
- [ ] Set up Datadog/New Relic (APM)
- [ ] Create monitoring dashboards
- [ ] Configure alerts for security events

---

## Summary

**Current State:** ⚠️ Minimal logging (console.log only)  
**Target State:** ✅ Professional, structured, auditable logging  

**Priority:** HIGH - Security and compliance requirement  
**Estimated Time:** 1-2 weeks for full implementation  

**Next Steps:**
1. Start with Phase 1 (add Logger to all auth use cases)
2. Implement audit logging for compliance
3. Set up Winston for production-ready logging
4. Integrate with monitoring tools

For detailed examples, see the code samples above. All authentication events should be logged for security, debugging, and compliance purposes.
