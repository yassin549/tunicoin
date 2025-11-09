"""NOWPayments.io API integration service."""

import httpx
import hmac
import hashlib
import json
from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.core.config import settings


class NOWPaymentsService:
    """
    Service for interacting with NOWPayments.io API.
    
    Handles:
    - Payment creation
    - Payment status checking
    - Webhook verification
    - Currency information
    - Payout (withdrawal) creation
    """
    
    def __init__(self):
        self.api_key = settings.NOWPAYMENTS_API_KEY
        self.public_key = settings.NOWPAYMENTS_PUBLIC_KEY
        self.ipn_secret = settings.NOWPAYMENTS_IPN_SECRET
        self.base_url = settings.NOWPAYMENTS_BASE_URL
        
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
    
    async def get_available_currencies(self) -> List[str]:
        """
        Get list of available cryptocurrencies.
        
        Returns:
            List of currency codes (e.g., ['btc', 'eth', 'usdt'])
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/currencies",
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("currencies", [])
    
    async def get_estimate(self, amount: float, currency_from: str, currency_to: str) -> Dict[str, Any]:
        """
        Get estimated exchange amount.
        
        Args:
            amount: Amount to convert
            currency_from: Source currency (e.g., 'usd')
            currency_to: Target currency (e.g., 'btc')
            
        Returns:
            Estimate data with converted amount
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/estimate",
                headers=self.headers,
                params={
                    "amount": amount,
                    "currency_from": currency_from,
                    "currency_to": currency_to,
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_minimum_payment_amount(self, currency_from: str, currency_to: str) -> Dict[str, Any]:
        """
        Get minimum payment amount for a currency pair.
        
        Args:
            currency_from: Source currency (e.g., 'usd')
            currency_to: Target currency (e.g., 'btc')
            
        Returns:
            Minimum amount data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/min-amount",
                headers=self.headers,
                params={
                    "currency_from": currency_from,
                    "currency_to": currency_to,
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def create_payment(
        self,
        price_amount: float,
        price_currency: str,
        pay_currency: str,
        order_id: str,
        order_description: str,
        ipn_callback_url: str,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new payment.
        
        Args:
            price_amount: Amount in price_currency
            price_currency: Currency of the price (e.g., 'usd')
            pay_currency: Currency customer will pay in (e.g., 'btc')
            order_id: Your internal order ID
            order_description: Description of the order
            ipn_callback_url: IPN callback URL for notifications
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment cancelled
            
        Returns:
            Payment data with payment_id and pay_address
        """
        payload = {
            "price_amount": price_amount,
            "price_currency": price_currency,
            "pay_currency": pay_currency,
            "order_id": order_id,
            "order_description": order_description,
            "ipn_callback_url": ipn_callback_url,
        }
        
        if success_url:
            payload["success_url"] = success_url
        if cancel_url:
            payload["cancel_url"] = cancel_url
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/payment",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()
    
    async def create_invoice(
        self,
        price_amount: float,
        price_currency: str,
        order_id: str,
        order_description: str,
        ipn_callback_url: str,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a payment invoice (allows customer to choose cryptocurrency).
        
        Args:
            price_amount: Amount in price_currency
            price_currency: Currency of the price (e.g., 'usd')
            order_id: Your internal order ID
            order_description: Description of the order
            ipn_callback_url: IPN callback URL for notifications
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment cancelled
            
        Returns:
            Invoice data with invoice_id and invoice_url
        """
        payload = {
            "price_amount": price_amount,
            "price_currency": price_currency,
            "order_id": order_id,
            "order_description": order_description,
            "ipn_callback_url": ipn_callback_url,
        }
        
        if success_url:
            payload["success_url"] = success_url
        if cancel_url:
            payload["cancel_url"] = cancel_url
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/invoice",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment status.
        
        Args:
            payment_id: NOWPayments payment ID
            
        Returns:
            Payment status data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/payment/{payment_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()
    
    async def create_payout(
        self,
        withdrawals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a payout (withdrawal) batch.
        
        Args:
            withdrawals: List of withdrawal dicts with:
                - address: Recipient crypto address
                - currency: Crypto currency code
                - amount: Amount to send
                - ipn_callback_url: IPN callback URL
                - extra_id: Optional memo/tag for certain currencies
                
        Returns:
            Payout batch data
            
        Example:
            withdrawals = [{
                "address": "0x123...",
                "currency": "eth",
                "amount": 0.5,
                "ipn_callback_url": "https://..."
            }]
        """
        payload = {"withdrawals": withdrawals}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/payout",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_payout_status(self, payout_id: str) -> Dict[str, Any]:
        """
        Get payout status.
        
        Args:
            payout_id: NOWPayments payout ID
            
        Returns:
            Payout status data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/payout/{payout_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()
    
    def verify_ipn_signature(self, request_data: bytes, signature: str) -> bool:
        """
        Verify IPN callback signature.
        
        Args:
            request_data: Raw request body (bytes)
            signature: Signature from x-nowpayments-sig header
            
        Returns:
            True if signature is valid
        """
        # Calculate HMAC-SHA512 signature
        calculated_sig = hmac.new(
            self.ipn_secret.encode('utf-8'),
            request_data,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(calculated_sig, signature)
    
    async def validate_address(self, currency: str, address: str) -> Dict[str, Any]:
        """
        Validate a cryptocurrency address.
        
        Args:
            currency: Crypto currency code (e.g., 'btc')
            address: Address to validate
            
        Returns:
            Validation result
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/payout/validate-address",
                headers=self.headers,
                json={
                    "currency": currency,
                    "address": address,
                }
            )
            response.raise_for_status()
            return response.json()


# Global instance
nowpayments = NOWPaymentsService()
