# Swagger/OpenAPI Documentation - Complete Guide

**Date:** May 10, 2026  
**Status:** ✅ **IMPLEMENTED** - Ready to Use

---

## What is Swagger?

**Swagger** (now called **OpenAPI**) is an API documentation tool that automatically generates interactive documentation for your REST APIs.

### Key Benefits:
1. **Interactive Documentation** - Test APIs directly from the browser
2. **Auto-Generated** - No manual documentation writing needed
3. **Standard Format** - Industry-standard OpenAPI specification
4. **Client Generation** - Auto-generate API clients in any language
5. **Validation** - Validate requests/responses against schema
6. **Collaboration** - Share API docs with frontend developers, testers, partners

---

## Your Current Swagger Setup

### ✅ What's Already Configured

**File:** `backend/src/main.ts` (Lines 42-69)

```typescript
// Swagger Documentation
if (process.env.NODE_ENV !== 'production') {
  const config = new DocumentBuilder()
    .setTitle('Football Management Platform API')
    .setDescription('API documentation for the Football Management Platform')
    .setVersion('1.0')
    .addBearerAuth(
      {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
        name: 'JWT',
        description: 'Enter JWT token',
        in: 'header',
      },
      'JWT-auth',
    )
    .addTag('Authentication', 'User authentication endpoints')
    .addTag('Health', 'Health check endpoints')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document, {
    swaggerOptions: {
      persistAuthorization: true,
    },
  });
}
```

### Access Your Swagger UI:
```
http://localhost:3000/docs
```

---

## How Swagger Works

### 1. Decorators Add Metadata

You add decorators to your controllers and DTOs:

```typescript
@ApiTags('Authentication')  // Groups endpoints
@Controller('auth')
export class AuthController {
  
  @Post('login')
  @ApiOperation({ summary: 'Login with email and password' })  // Description
  @ApiResponse({ status: 200, description: 'Login successful' })  // Response
  @ApiResponse({ status: 401, description: 'Invalid credentials' })
  async login(@Body() loginDto: LoginDto) { ... }
}
```

### 2. NestJS Scans Decorators

NestJS reads all decorators and builds an OpenAPI specification (JSON/YAML).

### 3. Swagger UI Renders Documentation

The spec is rendered as an interactive web page where you can:
- Browse all endpoints
- See request/response schemas
- Test endpoints directly
- Authenticate with JWT tokens

---

## Using Swagger UI

### Step 1: Open Swagger UI

Navigate to: `http://localhost:3000/docs`

You'll see:
- List of all API tags (Authentication, Health, etc.)
- Expandable endpoint sections
- Try it out buttons

### Step 2: Authenticate with JWT

1. Click the **Authorize** button (top right, lock icon 🔒)
2. Enter your JWT token: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. Click **Authorize**
4. All subsequent requests will include the token

**Note:** `persistAuthorization: true` keeps you logged in across page refreshes.

### Step 3: Test an Endpoint

Example: Test the "Get Current User" endpoint

1. Expand the `/auth/me` endpoint
2. Click **Try it out**
3. Click **Execute**
4. View the response in the "Responses" section

You'll see:
- Request URL
- Response headers
- Response body (JSON)
- Response code (200, 401, etc.)

---

## Enhancing Your Swagger Documentation

### Currently Documented Endpoints

✅ **Authentication Module** (All endpoints have basic docs):
- POST `/auth/login`
- POST `/auth/register`
- POST `/auth/refresh`
- POST `/auth/logout`
- GET `/auth/me`
- POST `/auth/forgot-password`
- POST `/auth/reset-password`
- POST `/auth/change-password`
- GET `/auth/verify-email`
- POST `/auth/resend-verification`
- POST `/auth/2fa/enable`
- POST `/auth/2fa/verify`
- POST `/auth/2fa/disable`
- GET `/auth/sessions`

✅ **Health Check**:
- GET `/api/health`

### Adding More Detailed Documentation

#### Example: Enhanced Login Endpoint

**File:** `backend/src/modules/auth/presentation/auth.controller.ts`

```typescript
@Public()
@Post('login')
@HttpCode(HttpStatus.OK)
@ApiOperation({ 
  summary: 'Authenticate user and return JWT tokens',
  description: `
    Authenticates a user with email and password.
    Returns access token (15min expiry) and refresh token (7 days expiry).
    
    Failed login attempts are tracked. Account locks after 5 failures.
  `,
})
@ApiBody({
  type: LoginDto,
  examples: {
    valid: {
      summary: 'Valid credentials',
      value: {
        email: 'user@example.com',
        password: 'SecurePass123!',
      },
    },
    invalid: {
      summary: 'Invalid credentials',
      value: {
        email: 'wrong@example.com',
        password: 'wrongpassword',
      },
    },
  },
})
@ApiOkResponse({
  description: 'Login successful',
  schema: {
    example: {
      user: {
        id: 'uuid-here',
        email: 'user@example.com',
        firstName: 'John',
        lastName: 'Doe',
        role: 'COACH',
        tenantId: 'tenant-uuid',
      },
      accessToken: 'eyJhbGci...',
      refreshToken: 'eyJhbGci...',
    },
  },
})
@ApiUnauthorizedResponse({
  description: 'Invalid credentials or account locked',
  schema: {
    example: {
      statusCode: 401,
      message: 'Invalid credentials',
      error: 'Unauthorized',
    },
  },
})
@ApiTooManyRequestsResponse({
  description: 'Rate limit exceeded (max 5 requests per minute)',
})
@Throttle({ default: { limit: 5, ttl: 60000 } })
async login(@Body() loginDto: LoginDto, @Req() req: RequestWithUser) {
  const tenantId = req.tenantId || 'default-tenant';
  return this.loginUseCase.execute(loginDto, tenantId);
}
```

---

## Swagger Decorators Reference

### Controller-Level Decorators

```typescript
@ApiTags('Players')  // Group endpoints under "Players" tag
@Controller('players')
export class PlayersController { ... }
```

### Method-Level Decorators

```typescript
@ApiOperation({
  summary: 'Short description',
  description: 'Detailed markdown description',
})
@Get(':id')
findOne() { ... }
```

### Request Body

```typescript
@ApiBody({
  type: CreatePlayerDto,
  description: 'Player creation data',
  required: true,
})
@Post()
create(@Body() dto: CreatePlayerDto) { ... }
```

### Query Parameters

```typescript
@ApiQuery({
  name: 'page',
  required: false,
  type: Number,
  example: 1,
  description: 'Page number for pagination',
})
@ApiQuery({
  name: 'limit',
  required: false,
  type: Number,
  example: 10,
  description: 'Items per page',
})
@Get()
findAll(@Query('page') page: number, @Query('limit') limit: number) { ... }
```

### Path Parameters

```typescript
@ApiParam({
  name: 'id',
  required: true,
  type: String,
  description: 'Player UUID',
  example: '123e4567-e89b-12d3-a456-426614174000',
})
@Get(':id')
findOne(@Param('id') id: string) { ... }
```

### Responses

```typescript
@ApiOkResponse({
  description: 'Success',
  type: PlayerResponseDto,  // Auto-generates schema from DTO
})
@ApiCreatedResponse({
  description: 'Resource created',
  type: PlayerResponseDto,
})
@ApiBadRequestResponse({
  description: 'Validation failed',
})
@ApiUnauthorizedResponse({
  description: 'Not authenticated',
})
@ApiForbiddenResponse({
  description: 'Insufficient permissions',
})
@ApiNotFoundResponse({
  description: 'Resource not found',
})
@ApiInternalServerErrorResponse({
  description: 'Server error',
})
```

### Security/Authentication

```typescript
// For protected endpoints (JWT required)
@UseGuards(JwtAuthGuard)
@Get('protected')
@ApiBearerAuth('JWT-auth')  // Shows lock icon in Swagger UI
getProtected() { ... }

// For public endpoints (no auth required)
@Public()
@Post('login')
getPublic() { ... }
```

---

## DTO Documentation

### Example: LoginDto with Swagger Docs

**File:** `backend/src/modules/auth/presentation/dto/login.dto.ts`

```typescript
import { IsEmail, IsNotEmpty, IsString, MinLength } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class LoginDto {
  @ApiProperty({
    description: 'User email address',
    example: 'user@example.com',
    required: true,
  })
  @IsEmail()
  @IsNotEmpty()
  email: string;

  @ApiProperty({
    description: 'User password (min 8 chars, must include uppercase, lowercase, number, special char)',
    example: 'SecurePass123!',
    required: true,
    minLength: 8,
  })
  @IsString()
  @IsNotEmpty()
  @MinLength(8)
  password: string;
}
```

### Example: RegisterDto

```typescript
import { ApiProperty } from '@nestjs/swagger';

export class RegisterDto {
  @ApiProperty({
    description: 'User first name',
    example: 'John',
    minLength: 2,
  })
  firstName: string;

  @ApiProperty({
    description: 'User last name',
    example: 'Doe',
    minLength: 2,
  })
  lastName: string;

  @ApiProperty({
    description: 'User email (must be unique within tenant)',
    example: 'john.doe@example.com',
  })
  @IsEmail()
  email: string;

  @ApiProperty({
    description: 'Password (min 8 chars, uppercase, lowercase, number, special char)',
    example: 'SecurePass123!',
  })
  password: string;

  @ApiProperty({
    description: 'Tenant ID (organization identifier)',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  tenantId: string;

  @ApiProperty({
    description: 'User role (defaults to PLAYER if not specified)',
    example: 'COACH',
    enum: UserRole,
    required: false,
  })
  role?: UserRole;
}
```

---

## Advanced Swagger Features

### 1. Custom Schemas

For complex responses not tied to DTOs:

```typescript
@ApiOkResponse({
  description: 'Login successful',
  schema: {
    properties: {
      user: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
          email: { type: 'string', format: 'email' },
          role: { type: 'string', enum: ['SUPER_ADMIN', 'OWNER', 'COACH'] },
        },
      },
      accessToken: { type: 'string', example: 'eyJhbGci...' },
      refreshToken: { type: 'string', example: 'eyJhbGci...' },
    },
  },
})
```

### 2. File Upload Documentation

```typescript
@Post('upload')
@ApiOperation({ summary: 'Upload player photo' })
@ApiConsumes('multipart/form-data')
@ApiBody({
  schema: {
    type: 'object',
    properties: {
      file: {
        type: 'string',
        format: 'binary',
      },
      playerId: {
        type: 'string',
        format: 'uuid',
      },
    },
  },
})
uploadFile(@UploadedFile() file: Express.Multer.File) { ... }
```

### 3. Pagination Documentation

```typescript
@ApiOkResponse({
  description: 'Paginated player list',
  schema: {
    properties: {
      data: {
        type: 'array',
        items: { $ref: '#/components/schemas/Player' },
      },
      meta: {
        type: 'object',
        properties: {
          total: { type: 'number', example: 100 },
          page: { type: 'number', example: 1 },
          limit: { type: 'number', example: 10 },
          totalPages: { type: 'number', example: 10 },
        },
      },
    },
  },
})
```

### 4. Enum Documentation

```typescript
@ApiProperty({
  description: 'Player position',
  enum: PlayerPosition,
  enumName: 'PlayerPosition',
  example: PlayerPosition.ST,
})
position: PlayerPosition;
```

---

## Making Swagger Useful for Your Team

### For Frontend Developers

1. **API Discovery**
   - Browse all available endpoints
   - See required parameters
   - Understand response structures

2. **Testing Without Code**
   - Test endpoints before writing frontend code
   - Verify API behavior
   - Debug issues quickly

3. **Type Safety**
   - Generate TypeScript types from OpenAPI spec
   - Use tools like `openapi-typescript-codegen`

**Generate TypeScript Client:**
```bash
npm install openapi-typescript-codegen

# Generate client from running API
npx openapi-typescript-codegen --input http://localhost:3000/docs-json --output ./src/api
```

### For QA/Testers

1. **Manual Testing**
   - Test all endpoints without Postman
   - Verify request/response formats
   - Test edge cases

2. **Automated Testing**
   - Export OpenAPI spec
   - Generate automated tests
   - Integrate with CI/CD

### For External Partners

1. **API Documentation**
   - Share Swagger URL with partners
   - They can explore and test your API
   - No need for separate documentation

2. **Client Generation**
   - Partners can generate SDKs in their language
   - Python, Java, C#, JavaScript, etc.

---

## Best Practices

### ✅ DO

1. **Document All Endpoints**
   ```typescript
   @ApiOperation({ summary: 'Clear description' })
   @ApiOkResponse({ description: 'Success case' })
   @ApiErrorResponses(...)  // Document all error cases
   ```

2. **Provide Examples**
   ```typescript
   @ApiProperty({ example: 'user@example.com' })
   email: string;
   ```

3. **Use Descriptive Summaries**
   ```typescript
   // ❌ BAD
   @ApiOperation({ summary: 'Get data' })
   
   // ✅ GOOD
   @ApiOperation({ summary: 'Retrieve player profile by ID' })
   ```

4. **Group Related Endpoints**
   ```typescript
   @ApiTags('Players')
   @Controller('players')
   ```

5. **Document Authentication Requirements**
   ```typescript
   @ApiBearerAuth('JWT-auth')
   @UseGuards(JwtAuthGuard)
   ```

### ❌ DON'T

1. **Don't Skip Error Responses**
   ```typescript
   // ❌ BAD - Only documents success
   @ApiOkResponse({ ... })
   
   // ✅ GOOD - Documents all scenarios
   @ApiOkResponse({ ... })
   @ApiBadRequestResponse({ ... })
   @ApiUnauthorizedResponse({ ... })
   @ApiNotFoundResponse({ ... })
   ```

2. **Don't Expose Sensitive Info**
   ```typescript
   // ❌ BAD - Shows password in example
   @ApiProperty({ example: 'password123' })
   password: string;
   
   // ✅ GOOD - Generic example
   @ApiProperty({ example: '••••••••' })
   password: string;
   ```

3. **Don't Forget to Update Docs**
   - When you change API, update decorators
   - Keep examples current
   - Remove deprecated endpoints from docs

---

## Production Considerations

### Disable Swagger in Production

Your current setup already does this:

```typescript
if (process.env.NODE_ENV !== 'production') {
  // Swagger setup
}
```

**Why?**
- Security: Don't expose API structure publicly
- Performance: Reduce overhead
- Professionalism: Internal docs shouldn't be public

### Alternative: Protected Swagger

If you need Swagger in production:

```typescript
import { BasicAuth } from 'swagger-ui-express';

SwaggerModule.setup('docs', app, document, {
  swaggerOptions: {
    persistAuthorization: true,
  },
  customSiteTitle: 'API Docs',
  // Add authentication
  auth: {
    user: process.env.SWAGGER_USER,
    pass: process.env.SWAGGER_PASSWORD,
  },
});
```

---

## Swagger vs Alternatives

| Feature | Swagger/OpenAPI | Postman | Insomnia |
|---------|----------------|---------|----------|
| Auto-generated | ✅ Yes | ❌ Manual | ❌ Manual |
| Interactive testing | ✅ Yes | ✅ Yes | ✅ Yes |
| Code generation | ✅ Yes | ⚠️ Limited | ❌ No |
| Version control | ✅ Spec in Git | ⚠️ Collections | ⚠️ Collections |
| Collaboration | ✅ Share URL | ✅ Teams | ✅ Teams |
| Learning curve | Low | Medium | Low |

**Recommendation:** Use Swagger for documentation + Postman for advanced testing workflows.

---

## Troubleshooting

### Issue: Swagger UI Not Loading

**Check:**
1. Is server running? `npm run start:dev`
2. Correct URL? `http://localhost:3000/docs`
3. Environment variable? `NODE_ENV !== 'production'`

### Issue: Endpoint Not Showing

**Check:**
1. Is controller imported in module?
2. Does controller have `@ApiTags()`?
3. Are methods decorated with `@ApiOperation()`?

### Issue: JWT Authentication Not Working

**Check:**
1. Did you click "Authorize" button?
2. Entered token with "Bearer " prefix?
3. Token is valid (not expired)?

### Issue: DTO Schema Not Showing

**Check:**
1. DTO has `@ApiProperty()` decorators?
2. DTO imported correctly?
3. Used `@ApiBody({ type: YourDto })`?

---

## Quick Reference Card

### Minimal Endpoint Documentation

```typescript
@Post('login')
@ApiOperation({ summary: 'Login user' })
@ApiOkResponse({ description: 'Success' })
@ApiUnauthorizedResponse({ description: 'Invalid credentials' })
async login(@Body() dto: LoginDto) { ... }
```

### Complete Endpoint Documentation

```typescript
@Post('login')
@ApiOperation({ 
  summary: 'Authenticate user',
  description: 'Longer description with markdown support'
})
@ApiBody({ type: LoginDto })
@ApiOkResponse({ type: AuthResponseDto })
@ApiUnauthorizedResponse({ description: 'Invalid credentials' })
@ApiTooManyRequestsResponse({ description: 'Rate limited' })
@ApiBearerAuth('JWT-auth')
async login(@Body() dto: LoginDto) { ... }
```

### DTO Property Documentation

```typescript
@ApiProperty({
  description: 'Field description',
  example: 'example value',
  required: true,
  minimum: 1,
  maximum: 100,
  enum: MyEnum,
})
fieldName: string;
```

---

## Summary

### What You Have:
✅ Swagger configured and working  
✅ Basic documentation on auth endpoints  
✅ JWT authentication support  
✅ Accessible at `http://localhost:3000/docs`  

### What to Improve:
🔧 Add detailed descriptions to all endpoints  
🔧 Document all error responses  
🔧 Add request/response examples  
🔧 Document query/path parameters  
🔧 Add DTO property descriptions  

### Next Steps:
1. Review all auth endpoints and enhance documentation
2. Add Swagger docs to other modules (Players, Scouting, Medical, etc.)
3. Test Swagger UI with actual API calls
4. Share Swagger URL with frontend team
5. Consider generating TypeScript client from spec

---

**Swagger is already set up and working!** Just navigate to `http://localhost:3000/docs` and start exploring your API. The more decorators you add, the better the documentation becomes.

For questions or issues, refer to:
- [NestJS Swagger Documentation](https://docs.nestjs.com/openapi/introduction)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI Documentation](https://swagger.io/docs/open-source-tools/swagger-ui/)
