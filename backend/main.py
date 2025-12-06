"""
FastAPI Backend for AWS Certifications Coach - PRODUCTION VERSION
Enhanced with security, monitoring, and production-ready features
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import os
from datetime import datetime, timedelta
from collections import defaultdict
import logging

# Import application modules
from database import (
    get_db_connection, 
    close_db_connection, 
    create_tables,
    insert_user,
    get_user_by_email,
    check_if_user_exists,
)
from models import User, UserCreate, UserLogin, ChatMessage, ChatResponse
from ai_service import AIService
from auth import get_password_hash, verify_password

# Import security modules
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Initialize Sentry for error tracking
if SENTRY_AVAILABLE and os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1 if os.getenv("APP_ENV") == "production" else 1.0,
        environment=os.getenv("APP_ENV", "production"),
        release="aws-certifications-coach@2.0.0"
    )

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AWS Certifications Coach API",
    description="Production backend API for AWS certification learning platform",
    version="2.0.0",
    docs_url="/docs" if os.getenv("APP_ENV") != "production" else None,
    redoc_url="/redoc" if os.getenv("APP_ENV") != "production" else None,
)

# ============================================
# SECURITY MIDDLEWARE
# ============================================

# Force HTTPS in production
if os.getenv("APP_ENV") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    
    # Trusted host middleware
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
    if "*" not in allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=allowed_hosts
        )

# Gzip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS Configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)

# ============================================
# RATE LIMITING
# ============================================

class RateLimiter:
    """Simple in-memory rate limiter"""
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def check_rate_limit(self, request: Request):
        if not os.getenv("RATE_LIMIT_ENABLED", "true") == "true":
            return
        
        client_ip = request.client.host
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        self.requests[client_ip].append(now)

rate_limiter = RateLimiter(
    requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
)

# ============================================
# MIDDLEWARE
# ============================================

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    if os.getenv("ENABLE_HSTS", "true") == "true":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    if os.getenv("ENABLE_CSP", "true") == "true":
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    
    return response

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to requests"""
    # Skip rate limiting for health checks
    if request.url.path == "/health":
        return await call_next(request)
    
    await rate_limiter.check_rate_limit(request)
    response = await call_next(request)
    return response

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Duration: {process_time:.3f}s "
        f"IP: {request.client.host}"
    )
    
    return response

# ============================================
# INITIALIZE AI SERVICE
# ============================================

ai_service = AIService()

# ============================================
# HEALTH CHECK & STATUS ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": os.getenv("APP_ENV", "unknown"),
        "checks": {}
    }
    
    # Database connectivity check
    try:
        conn = get_db_connection()
        if conn:
            close_db_connection(conn)
            checks["checks"]["database"] = "healthy"
        else:
            checks["checks"]["database"] = "unhealthy"
            checks["status"] = "degraded"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["checks"]["database"] = f"unhealthy: {str(e)}"
        checks["status"] = "unhealthy"
    
    # N8N webhook check (optional)
    try:
        if os.getenv("N8N_CHAT_WEBHOOK_URL"):
            checks["checks"]["n8n"] = "configured"
        else:
            checks["checks"]["n8n"] = "not_configured"
    except Exception as e:
        checks["checks"]["n8n"] = f"error: {str(e)}"
    
    # System resources check
    try:
        import psutil
        disk = psutil.disk_usage('/')
        memory = psutil.virtual_memory()
        
        checks["checks"]["disk_usage"] = f"{disk.percent:.1f}%"
        checks["checks"]["memory_usage"] = f"{memory.percent:.1f}%"
        
        if disk.percent > 90 or memory.percent > 90:
            checks["status"] = "degraded"
            logger.warning(f"High resource usage - Disk: {disk.percent}%, Memory: {memory.percent}%")
    except ImportError:
        checks["checks"]["resources"] = "psutil not available"
    except Exception as e:
        checks["checks"]["resources"] = f"error: {str(e)}"
    
    # Return appropriate status code
    if checks["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=checks)
    elif checks["status"] == "degraded":
        return JSONResponse(status_code=200, content=checks)
    
    return checks

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "AWS Certifications Coach API",
        "version": "2.0.0",
        "environment": os.getenv("APP_ENV", "unknown"),
        "status": "operational",
        "documentation": "/docs" if os.getenv("APP_ENV") != "production" else "disabled in production",
        "endpoints": {
            "health": "/health",
            "register": "/api/register",
            "login": "/api/login",
            "user": "/api/user/{email}",
            "chat": "/api/chat"
        }
    }

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, request: Request):
    """Register a new user with secure password hashing"""
    try:
        # Check if user exists
        if check_if_user_exists(user.email):
            logger.warning(f"Registration attempt with existing email: {user.email} from IP: {request.client.host}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Validate password strength
        if len(user.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Hash password using bcrypt
        hashed_password = get_password_hash(user.password)
        
        # Insert user into database
        success = insert_user(
            name=user.name,
            email=user.email,
            password=hashed_password,
            target_certification=user.target_certification,
            age=user.age
        )

        if not success:
            logger.error(f"Failed to create user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Retrieve created user
        created_user = get_user_by_email(user.email)
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created but could not be retrieved"
            )
        
        logger.info(f"New user registered: {user.email}")
        return created_user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@app.post("/api/login")
async def login_user(form_data: UserLogin, request: Request):
    """User login with secure password verification"""
    try:
        # Retrieve user
        user = get_user_by_email(form_data.email)
        
        # Check credentials
        if not user or not verify_password(form_data.password, user['password']):
            logger.warning(f"Failed login attempt for: {form_data.email} from IP: {request.client.host}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Successful login: {form_data.email}")
        
        # Remove password from response
        user_response = {k: v for k, v in user.items() if k != 'password'}
        
        return {
            "message": "Login successful",
            "user": user_response
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@app.get("/api/user/{email}", response_model=User)
async def get_user_details(email: str):
    """Get user details by email"""
    try:
        user = get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user details"
        )

# ============================================
# AI CHAT ENDPOINT
# ============================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """AI Chat endpoint for answering AWS certification questions"""
    try:
        # Get AI response
        response = await ai_service.answer_question(
            user_id=message.user_id,
            question=message.question,
            context=message.context
        )
        
        return ChatResponse(
            answer=response,
            timestamp=datetime.utcnow(),
            user_id=message.user_id
        )
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing chat request"
        )

# ============================================
# USER STATS & PROGRESS
# ============================================

@app.get("/api/user/{user_id}/stats")
async def get_user_stats(user_id: int):
    """Get user statistics and progress"""
    try:
        # TODO: Implement actual stats fetching from database
        return {
            "user_id": user_id,
            "total_study_time": "12h 45m",
            "practice_tests": 8,
            "average_score": 85,
            "progress": 75,
            "last_activity": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user statistics"
        )

# ============================================
# EXAM PRACTICE ENDPOINTS
# ============================================

@app.post("/api/exam/practice")
async def generate_practice_exam(
    user_id: int,
    certification: str,
    difficulty: str = "medium",
    num_questions: int = 5
):
    """Generate practice exam questions via n8n workflow"""
    try:
        result = await ai_service.generate_exam_practice(
            user_id=user_id,
            certification=certification,
            difficulty=difficulty,
            num_questions=num_questions
        )
        return result
    except Exception as e:
        logger.error(f"Error generating practice exam: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating practice exam"
        )

@app.get("/api/study/tricks")
async def get_study_tricks(
    user_id: int,
    certification: str,
    topic: str = None
):
    """Get study tricks and tips via n8n workflow"""
    try:
        result = await ai_service.get_study_tricks(
            user_id=user_id,
            certification=certification,
            topic=topic
        )
        return {"tricks": result}
    except Exception as e:
        logger.error(f"Error fetching study tricks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching study tricks"
        )

@app.post("/api/evaluate/answer")
async def evaluate_answer(
    user_id: int,
    question: str,
    user_answer: str,
    correct_answer: str
):
    """Evaluate user's answer via n8n workflow"""
    try:
        result = await ai_service.evaluate_answer(
            user_id=user_id,
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer
        )
        return result
    except Exception as e:
        logger.error(f"Error evaluating answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error evaluating answer"
        )

# ============================================
# LEARNING RESOURCES
# ============================================

@app.get("/api/resources/{certification}")
async def get_learning_resources(certification: str):
    """Get learning resources for a specific certification"""
    resources = {
        "videos": [
            {
                "title": "AWS Certified Solutions Architect | A Practical Guide",
                "url": "https://www.youtube.com/watch?v=ulprqHHWlng",
                "duration": "10:00:00",
                "provider": "YouTube"
            },
            {
                "title": "AWS Certified Solutions Architect | Full Course",
                "url": "https://www.youtube.com/watch?v=Ia-UEYYR44s",
                "duration": "12:00:00",
                "provider": "YouTube"
            }
        ],
        "documentation": [
            {
                "title": "AWS Documentation",
                "url": "https://docs.aws.amazon.com/",
                "type": "official"
            }
        ],
        "practice_tests": []
    }
    
    return resources

# ============================================
# STARTUP & SHUTDOWN EVENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Starting AWS Certifications Coach Backend...")
    logger.info(f"Environment: {os.getenv('APP_ENV', 'unknown')}")
    logger.info(f"Debug Mode: {os.getenv('DEBUG', 'false')}")
    
    try:
        create_tables()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
    
    logger.info("✅ Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AWS Certifications Coach Backend...")

# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        workers=int(os.getenv("WORKERS", "4")),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

