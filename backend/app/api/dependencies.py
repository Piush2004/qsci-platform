from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.core.events import event_bus, DomainEventBus

# Mocked Current User for Phase 1
class CurrentUser:
    def __init__(self, id: str, tenant_id: str, role: str):
        self.id = id
        self.tenant_id = tenant_id
        self.role = role

def get_current_user(x_user_id: Optional[str] = Header(None), x_tenant_id: Optional[str] = Header(None), x_role: Optional[str] = Header(None)) -> CurrentUser:
    """
    Mock JWT/OIDC Authentication for Phase 1.
    In production, this dependency will decode the JWT from the Authorization header,
    verify the signature against JWKS, and extract the claims.
    """
    if not x_user_id or not x_tenant_id:
        # Default mock user for local development if headers are missing
        return CurrentUser(
            id="mock_user_123", 
            tenant_id="mock_tenant_456", 
            role="planner"
        )
    return CurrentUser(id=x_user_id, tenant_id=x_tenant_id, role=x_role or "viewer")

def get_event_bus() -> DomainEventBus:
    """Dependency to inject the Event Bus."""
    return event_bus

def require_role(allowed_roles: list[str]):
    """RBAC Dependency generator"""
    def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker
