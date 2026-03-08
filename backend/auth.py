"""
Clerk JWT verification for FastAPI.

Expects Authorization: Bearer <session_token> and verifies the token using
Clerk's JWKS endpoint. Returns the Clerk user id (sub claim) for use in routes.
"""
from __future__ import annotations

import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

CLERK_ISSUER_URL = os.environ.get("CLERK_ISSUER_URL", "").rstrip("/")
JWKS_URL = f"{CLERK_ISSUER_URL}/.well-known/jwks.json" if CLERK_ISSUER_URL else ""

_security = HTTPBearer(auto_error=False)


def _get_jwks_client() -> PyJWKClient | None:
    if not JWKS_URL:
        return None
    return PyJWKClient(JWKS_URL)


def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_security),
    ],
) -> str:
    """
    Verify Clerk Bearer token and return the user id (sub claim).
    Raises 401 if missing or invalid.
    """
    if not CLERK_ISSUER_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CLERK_ISSUER_URL is not configured",
        )
    if not credentials or credentials.credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        jwks_client = _get_jwks_client()
        if not jwks_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Clerk JWKS not configured",
            )
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER_URL,
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = payload.get("sub")
    if not sub or not isinstance(sub, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return sub


def get_current_user_id_optional(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_security),
    ],
) -> str | None:
    """
    Verify Clerk Bearer token if present and return the user id (sub claim), else None.
    Does not raise when no token or invalid; returns None.
    """
    if not CLERK_ISSUER_URL or not credentials or not credentials.credentials:
        return None
    token = credentials.credentials
    try:
        jwks_client = _get_jwks_client()
        if not jwks_client:
            return None
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER_URL,
            options={"verify_aud": False},
        )
    except jwt.InvalidTokenError:
        return None
    sub = payload.get("sub")
    if not sub or not isinstance(sub, str):
        return None
    return sub
