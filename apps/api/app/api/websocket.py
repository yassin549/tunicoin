"""WebSocket manager for real-time updates."""

from typing import Dict, Set
from fastapi import WebSocket
from uuid import UUID
import json
import asyncio


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    
    Supports:
    - Per-account subscriptions
    - Broadcasting to multiple clients
    - Connection lifecycle management
    """
    
    def __init__(self):
        # Dictionary mapping account_id to set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, account_id: str):
        """
        Accept a new WebSocket connection for an account.
        
        Args:
            websocket: WebSocket connection
            account_id: Account ID to subscribe to
        """
        await websocket.accept()
        
        if account_id not in self.active_connections:
            self.active_connections[account_id] = set()
        
        self.active_connections[account_id].add(websocket)
        
        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connected",
                "account_id": account_id,
                "message": "Connected to account stream",
            },
            websocket
        )
    
    def disconnect(self, websocket: WebSocket, account_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove
            account_id: Account ID
        """
        if account_id in self.active_connections:
            self.active_connections[account_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[account_id]:
                del self.active_connections[account_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to a specific WebSocket connection.
        
        Args:
            message: Message dictionary to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast_to_account(self, message: dict, account_id: str):
        """
        Broadcast message to all connections subscribed to an account.
        
        Args:
            message: Message dictionary to broadcast
            account_id: Target account ID
        """
        if account_id not in self.active_connections:
            return
        
        # Get all connections for this account
        connections = list(self.active_connections[account_id])
        
        # Send to all connections
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                # Remove failed connection
                self.disconnect(connection, account_id)
    
    async def send_order_update(self, account_id: str, order_data: dict):
        """
        Send order update to account subscribers.
        
        Args:
            account_id: Account ID
            order_data: Order data dictionary
        """
        message = {
            "type": "order_update",
            "account_id": account_id,
            "data": order_data,
        }
        await self.broadcast_to_account(message, account_id)
    
    async def send_position_update(self, account_id: str, position_data: dict):
        """
        Send position update to account subscribers.
        
        Args:
            account_id: Account ID
            position_data: Position data dictionary
        """
        message = {
            "type": "position_update",
            "account_id": account_id,
            "data": position_data,
        }
        await self.broadcast_to_account(message, account_id)
    
    async def send_balance_update(self, account_id: str, balance_data: dict):
        """
        Send balance update to account subscribers.
        
        Args:
            account_id: Account ID
            balance_data: Balance data dictionary
        """
        message = {
            "type": "balance_update",
            "account_id": account_id,
            "data": balance_data,
        }
        await self.broadcast_to_account(message, account_id)
    
    async def send_pnl_update(self, account_id: str, pnl_data: dict):
        """
        Send P&L update to account subscribers.
        
        Args:
            account_id: Account ID
            pnl_data: P&L data dictionary
        """
        message = {
            "type": "pnl_update",
            "account_id": account_id,
            "data": pnl_data,
        }
        await self.broadcast_to_account(message, account_id)


# Global connection manager instance
manager = ConnectionManager()
