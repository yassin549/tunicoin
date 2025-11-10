from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import os

# Import routers
from app.api.auth import router as auth_router
from app.api.market import router as market_router
from app.api.accounts import router as accounts_router
from app.api.orders import router as orders_router
from app.api.positions import router as positions_router
from app.api.backtests import router as backtests_router
from app.api.crypto import router as crypto_router
from app.api.investment import router as investment_router
from app.api.kyc import router as kyc_router
from app.api.admin import router as admin_router
from app.api.ws import router as ws_router

app = FastAPI(
    title="ExtraCoin API",
    description="AI-Powered Trading & Investment Platform API - Simulated trading and real investment management",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "ExtraCoin Support",
        "email": "support@extracoin.com",
    },
    license_info={
        "name": "Proprietary - CMF Regulated",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "ExtraCoin API",
        "version": "2.0.0",
        "status": "online",
        "docs": "/docs",
        "regulation": "CMF (Conseil du Marché Financier)",
        "endpoints": {
            "auth": "/api/auth",
            "market": "/api/market",
            "accounts": "/api/accounts",
            "orders": "/api/accounts/{account_id}/orders",
            "positions": "/api/accounts/{account_id}/positions",
            "backtests": "/api/backtests",
            "crypto": "/api/crypto",
            "investment": "/api/investment",
            "kyc": "/api/kyc",
            "websocket": "/ws/accounts/{account_id}",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {"status": "healthy", "version": "2.0.0"}


# Register API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(market_router, prefix="/api/market", tags=["Market Data"])
app.include_router(accounts_router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(orders_router, prefix="/api/accounts", tags=["Orders"])
app.include_router(positions_router, prefix="/api/accounts", tags=["Positions"])
app.include_router(backtests_router, prefix="/api/backtests", tags=["Backtests"])
app.include_router(crypto_router, prefix="/api/crypto", tags=["Crypto Payments"])
app.include_router(investment_router, prefix="/api", tags=["Investment Management"])
app.include_router(kyc_router, prefix="/api", tags=["KYC Verification"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])

# Temporary endpoint to make user admin (remove after use)
@app.post("/api/make-admin-temp")
async def make_admin_temp(email: str, secret: str, db: AsyncSession = Depends(get_db)):
    """Temporary endpoint to make a user admin. Remove after use!"""
    # Simple secret check (change this to something only you know)
    if secret != "CHANGE_ME_SECRET_123":
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    from app.models.user import User
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_admin = True
    db.add(user)
    await db.commit()
    
    return {"message": f"User {email} is now an admin!", "user_id": str(user.id)}

# Register WebSocket router (no prefix needed for WebSocket)
app.include_router(ws_router, tags=["WebSocket"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors"""
    import traceback
    print(f"Unhandled exception: {exc}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": str(type(exc).__name__),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
