"""WebSocket endpoint for real-time account streams."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID
import asyncio

from app.core.database import get_session
from app.core.security import verify_token
from app.models.user import User
from app.models.account import Account
from app.api.websocket import manager

router = APIRouter()


async def get_user_from_token(token: str, session: AsyncSession) -> User:
    """
    Validate WebSocket connection token and return user.
    
    Args:
        token: JWT token
        session: Database session
        
    Returns:
        User object
        
    Raises:
        Exception if token is invalid or user not found
    """
    user_id = verify_token(token, token_type="access")
    
    if user_id is None:
        raise Exception("Invalid token")
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise Exception("Invalid user ID")
    
    result = await session.execute(
        select(User).where(User.id == user_uuid)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise Exception("User not found or inactive")
    
    return user


@router.websocket("/ws/accounts/{account_id}")
async def websocket_account_stream(
    websocket: WebSocket,
    account_id: str,
):
    """
    WebSocket endpoint for real-time account updates.
    
    **Authentication:**
    - Send JWT token as first message: `{"token": "your-jwt-token"}`
    - Connection will be rejected if token is invalid
    
    **Message Types Received:**
    1. `order_update` - Order status changes
    2. `position_update` - Position P&L updates
    3. `balance_update` - Account balance changes
    4. `pnl_update` - P&L calculations
    
    **Example Messages:**
    ```json
    {
        "type": "order_update",
        "account_id": "uuid",
        "data": {
            "order_id": "uuid",
            "status": "filled",
            "fill_price": 50000.00
        }
    }
    ```
    
    **Usage:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/accounts/{account_id}');
    
    ws.onopen = () => {
        ws.send(JSON.stringify({token: 'your-jwt-token'}));
    };
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log('Received:', message);
    };
    ```
    """
    # Validate account_id format
    try:
        account_uuid = UUID(account_id)
    except ValueError:
        await websocket.close(code=1008, reason="Invalid account ID format")
        return
    
    # Accept connection first (required to receive messages)
    await websocket.accept()
    
    try:
        # Wait for authentication token (first message must be auth)
        auth_message = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=10.0
        )
        
        if "token" not in auth_message:
            await websocket.close(code=1008, reason="Missing token")
            return
        
        token = auth_message["token"]
        
        # Create database session for auth check
        from app.core.database import async_session
        async with async_session() as session:
            # Authenticate user
            try:
                user = await get_user_from_token(token, session)
            except Exception as e:
                await websocket.close(code=1008, reason=str(e))
                return
            
            # Verify user owns this account
            result = await session.execute(
                select(Account).where(
                    Account.id == account_uuid,
                    Account.user_id == user.id,
                )
            )
            account = result.scalar_one_or_none()
            
            if not account:
                await websocket.close(code=1008, reason="Account not found")
                return
        
        # Authentication successful - register connection
        await manager.connect(websocket, account_id)
        
        try:
            # Keep connection alive and handle incoming messages
            while True:
                # Wait for any message from client (e.g., heartbeat)
                data = await websocket.receive_json()
                
                # Handle ping/pong for keepalive
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
        except WebSocketDisconnect:
            # Client disconnected
            manager.disconnect(websocket, account_id)
            print(f"Client disconnected from account {account_id}")
        
    except asyncio.TimeoutError:
        await websocket.close(code=1008, reason="Authentication timeout")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal error")
        except:
            pass
        finally:
            manager.disconnect(websocket, account_id)
