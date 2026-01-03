"""
Authentication service using Supabase

This module provides:
- JWT token verification
- User authentication middleware
- Subscription limit checking
- Database operations for projects and usage tracking
"""
from supabase import create_client, Client
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import jwt, JWTError
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
from logger import logger

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Initialize Supabase client (only if credentials are provided)
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase client initialized")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize Supabase: {e}")
else:
    logger.warning("⚠️ Supabase credentials not configured - authentication disabled")

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify JWT token and return current user

    Usage in endpoints:
        @app.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"user_id": user["sub"]}

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        Dict containing user payload from JWT

    Raises:
        HTTPException: If token is invalid or missing
    """
    if not supabase or not SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )

    token = credentials.credentials

    try:
        # Verify JWT token
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"✅ User authenticated: {user_id}")
        return payload

    except JWTError as e:
        logger.error(f"❌ JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class SubscriptionChecker:
    """Check user subscription limits and track usage"""

    @staticmethod
    async def check_video_generation_allowed(user_id: str) -> bool:
        """
        Check if user can generate videos based on subscription limits

        Args:
            user_id: User's UUID

        Returns:
            True if allowed

        Raises:
            HTTPException: If no subscription or limit reached
        """
        if not supabase:
            logger.warning("⚠️ Supabase not configured - skipping limit check")
            return True

        try:
            # Get user subscription
            result = supabase.table("subscriptions") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("status", "active") \
                .single() \
                .execute()

            if not result.data:
                logger.error(f"❌ No active subscription for user {user_id}")
                raise HTTPException(
                    status_code=403,
                    detail="No active subscription found. Please subscribe to continue."
                )

            subscription = result.data

            # Check limits
            current_usage = subscription.get("current_month_usage", 0)
            monthly_limit = subscription.get("monthly_video_limit", 0)

            if current_usage >= monthly_limit:
                logger.warning(f"⚠️ User {user_id} reached limit: {current_usage}/{monthly_limit}")
                raise HTTPException(
                    status_code=403,
                    detail=f"Monthly limit reached ({monthly_limit} videos). Please upgrade your plan."
                )

            logger.info(f"✅ Video generation allowed for user {user_id}: {current_usage}/{monthly_limit}")
            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error checking subscription: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to check subscription status"
            )

    @staticmethod
    async def increment_usage(user_id: str):
        """
        Increment user's monthly video generation count

        Args:
            user_id: User's UUID
        """
        if not supabase:
            logger.warning("⚠️ Supabase not configured - skipping usage increment")
            return

        try:
            # Get current subscription
            result = supabase.table("subscriptions") \
                .select("current_month_usage") \
                .eq("user_id", user_id) \
                .eq("status", "active") \
                .single() \
                .execute()

            if result.data:
                new_count = result.data.get("current_month_usage", 0) + 1

                # Update usage count
                supabase.table("subscriptions") \
                    .update({"current_month_usage": new_count}) \
                    .eq("user_id", user_id) \
                    .execute()

                logger.info(f"✅ Incremented usage for user {user_id}: {new_count}")

        except Exception as e:
            logger.error(f"❌ Error incrementing usage: {e}")
            # Don't raise exception - usage tracking shouldn't block video generation

    @staticmethod
    async def get_subscription_info(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's subscription information

        Args:
            user_id: User's UUID

        Returns:
            Subscription data or None
        """
        if not supabase:
            return None

        try:
            result = supabase.table("subscriptions") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("status", "active") \
                .single() \
                .execute()

            return result.data

        except Exception as e:
            logger.error(f"❌ Error getting subscription: {e}")
            return None


class Database:
    """Database operations for projects and usage tracking"""

    @staticmethod
    async def create_project(user_id: str, project_data: dict) -> Dict[str, Any]:
        """
        Create a new project for a user

        Args:
            user_id: User's UUID
            project_data: Project details

        Returns:
            Created project data
        """
        if not supabase:
            raise HTTPException(
                status_code=503,
                detail="Database not configured"
            )

        try:
            result = supabase.table("projects").insert({
                "user_id": user_id,
                **project_data
            }).execute()

            logger.info(f"✅ Created project for user {user_id}")
            return result.data[0]

        except Exception as e:
            logger.error(f"❌ Error creating project: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create project: {str(e)}"
            )

    @staticmethod
    async def get_user_projects(user_id: str) -> List[Dict[str, Any]]:
        """
        Get all projects for a user

        Args:
            user_id: User's UUID

        Returns:
            List of projects
        """
        if not supabase:
            return []

        try:
            result = supabase.table("projects") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .execute()

            return result.data

        except Exception as e:
            logger.error(f"❌ Error fetching projects: {e}")
            return []

    @staticmethod
    async def get_project(project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific project

        Args:
            project_id: Project UUID
            user_id: User's UUID (for authorization)

        Returns:
            Project data or None
        """
        if not supabase:
            return None

        try:
            result = supabase.table("projects") \
                .select("*") \
                .eq("id", project_id) \
                .eq("user_id", user_id) \
                .single() \
                .execute()

            return result.data

        except Exception as e:
            logger.error(f"❌ Error fetching project: {e}")
            return None

    @staticmethod
    async def update_project(project_id: str, user_id: str, updates: dict) -> Optional[Dict[str, Any]]:
        """
        Update a project

        Args:
            project_id: Project UUID
            user_id: User's UUID (for authorization)
            updates: Fields to update

        Returns:
            Updated project data or None
        """
        if not supabase:
            return None

        try:
            result = supabase.table("projects") \
                .update(updates) \
                .eq("id", project_id) \
                .eq("user_id", user_id) \
                .execute()

            logger.info(f"✅ Updated project {project_id}")
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"❌ Error updating project: {e}")
            return None

    @staticmethod
    async def delete_project(project_id: str, user_id: str):
        """
        Delete a project

        Args:
            project_id: Project UUID
            user_id: User's UUID (for authorization)
        """
        if not supabase:
            return

        try:
            supabase.table("projects") \
                .delete() \
                .eq("id", project_id) \
                .eq("user_id", user_id) \
                .execute()

            logger.info(f"✅ Deleted project {project_id}")

        except Exception as e:
            logger.error(f"❌ Error deleting project: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete project: {str(e)}"
            )

    @staticmethod
    async def track_api_usage(
        user_id: str,
        project_id: str,
        service: str,
        operation: str,
        units: float,
        cost: float,
        metadata: dict = None
    ):
        """
        Track API usage for billing and analytics

        Args:
            user_id: User's UUID
            project_id: Project UUID
            service: Service name (e.g., 'runway_ml', 'elevenlabs')
            operation: Operation type (e.g., 'video_generation', 'audio_generation')
            units: Units consumed (seconds, characters, etc.)
            cost: Cost in USD
            metadata: Additional metadata (optional)
        """
        if not supabase:
            logger.warning("⚠️ Supabase not configured - skipping usage tracking")
            return

        try:
            supabase.table("api_usage").insert({
                "user_id": user_id,
                "project_id": project_id,
                "service": service,
                "operation": operation,
                "units_consumed": units,
                "cost_usd": cost,
                "metadata": metadata or {}
            }).execute()

            logger.info(f"✅ Tracked usage: {service}/{operation} - ${cost:.4f}")

        except Exception as e:
            logger.error(f"❌ Error tracking usage: {e}")
            # Don't raise exception - usage tracking shouldn't block operations

    @staticmethod
    async def get_user_usage(user_id: str, start_date: datetime = None) -> Dict[str, Any]:
        """
        Get user's API usage statistics

        Args:
            user_id: User's UUID
            start_date: Start date for filtering (defaults to current month)

        Returns:
            Usage statistics
        """
        if not supabase:
            return {"total_cost": 0, "usage": []}

        try:
            # Default to current month
            if not start_date:
                start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Get usage records
            result = supabase.table("api_usage") \
                .select("*") \
                .eq("user_id", user_id) \
                .gte("created_at", start_date.isoformat()) \
                .execute()

            usage_data = result.data
            total_cost = sum(float(u.get("cost_usd", 0)) for u in usage_data)

            return {
                "total_cost": total_cost,
                "usage": usage_data
            }

        except Exception as e:
            logger.error(f"❌ Error getting usage: {e}")
            return {"total_cost": 0, "usage": []}
