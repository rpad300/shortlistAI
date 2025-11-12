"""
Admin user database service.

Handles CRUD operations for admin_users table with authentication and security features.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
from database import get_supabase_client
import logging
import re
import bcrypt

logger = logging.getLogger(__name__)


class AdminService:
    """
    Service for managing admin users in the database.
    
    Key responsibilities:
    - Admin authentication and login
    - CRUD operations for admin users
    - Password security and hashing
    - Account lockout and security features
    - Role-based access control
    """
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "admin_users"
    
    async def authenticate(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate admin user with username/email and password.
        
        Args:
            username: Username or email address
            password: Plain text password
            ip_address: Optional IP address for audit logging
            
        Returns:
            Admin user dict if authenticated successfully, None otherwise
        """
        try:
            # Find admin by username or email
            result = self.client.table(self.table)\
                .select("*")\
                .or_(f"username.eq.{username},email.eq.{username}")\
                .eq("is_active", True)\
                .limit(1)\
                .execute()
            
            if not result.data:
                logger.warning(f"Admin authentication failed: user not found - {username} - IP: {ip_address}")
                return None
            
            admin = result.data[0]
            
            # Check if account is locked
            locked_until_value = admin.get("locked_until")
            if locked_until_value:
                if isinstance(locked_until_value, str):
                    locked_until_dt = datetime.fromisoformat(locked_until_value.replace("Z", "+00:00"))
                else:
                    locked_until_dt = locked_until_value
                if locked_until_dt and locked_until_dt > datetime.utcnow():
                    logger.warning(f"Admin authentication failed: account locked - {username} - IP: {ip_address}")
                    return None
            
            password_hash = admin.get("password_hash")
            if not password_hash:
                logger.error(f"Admin user {username} missing password hash")
                return None

            print(f"[Debug] Admin user {username} password hash: {password_hash}")
            print(f"[Debug] Hash length: {len(password_hash)}")

            try:
                password_match = bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
            except Exception as password_error:
                logger.error(f"Error verifying admin password: {password_error}")
                raise
            
            if not password_match:
                await self._increment_failed_attempts(admin["id"], username, ip_address)
                logger.warning(f"Admin authentication failed: invalid password - {username} - IP: {ip_address}")
                return None
            
            # Update last login
            await self.update_last_login(admin["id"])
            
            # Reset failed attempts on successful login
            await self.reset_failed_attempts(admin["id"])
            
            # Remove password hash from returned data
            admin_data = {k: v for k, v in admin.items() if k != "password_hash"}
            
            logger.info(f"Admin authentication successful - {username} - IP: {ip_address}")
            return admin_data
            
        except Exception as e:
            logger.error(f"Admin authentication error: {e}")
            return None
    
    async def create(
        self,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: str = "admin",
        created_by: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new admin user.
        
        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            first_name: Optional first name
            last_name: Optional last name
            role: Admin role (admin, super_admin)
            created_by: UUID of admin who created this account
            
        Returns:
            Created admin user dict (without password hash) or None if failed
        """
        try:
            # Validate inputs
            if not self._validate_username(username):
                raise ValueError("Invalid username format")
            
            if not self._validate_email(email):
                raise ValueError("Invalid email format")
            
            if not self._validate_password(password):
                raise ValueError("Password must be at least 8 characters long")
            
            # Check if username or email already exists
            existing = self.client.table(self.table)\
                .select("username, email")\
                .or_(f"username.eq.{username},email.eq.{email}")\
                .execute()
            
            if existing.data:
                field = "username" if existing.data[0]["username"] == username else "email"
                raise ValueError(f"Admin with this {field} already exists")
            
            # Generate bcrypt hash
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            # Create admin user
            admin_data = {
                "username": username.lower(),
                "email": email.lower(),
                "password_hash": hashed_password,
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "is_active": True,
                "created_by": str(created_by) if created_by else None,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table(self.table)\
                .insert(admin_data)\
                .execute()
            
            if result.data and len(result.data) > 0:
                admin = result.data[0]
                # Remove password hash from returned data
                admin_data = {k: v for k, v in admin.items() if k != "password_hash"}
                
                logger.info(f"Admin user created: {username}")
                return admin_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            raise
    
    async def get_by_id(self, admin_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get admin user by ID.
        
        Args:
            admin_id: Admin UUID
            
        Returns:
            Admin user dict or None
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("id", str(admin_id))\
                .eq("is_active", True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                admin = result.data[0]
                # Remove password hash from returned data
                admin_data = {k: v for k, v in admin.items() if k != "password_hash"}
                return admin_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting admin by ID: {e}")
            return None
    
    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get admin user by username.
        
        Args:
            username: Username
            
        Returns:
            Admin user dict or None
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("username", username.lower())\
                .eq("is_active", True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                admin = result.data[0]
                # Remove password hash from returned data
                admin_data = {k: v for k, v in admin.items() if k != "password_hash"}
                return admin_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting admin by username: {e}")
            return None
    
    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all admin users (for super admin use).
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            include_inactive: Whether to include inactive admin accounts
            
        Returns:
            List of admin user dicts (without password hashes)
        """
        try:
            query = self.client.table(self.table).select("*")
            
            if not include_inactive:
                query = query.eq("is_active", True)
            
            query = query.order("created_at", desc=True)\
                .range(offset, offset + limit - 1)
            
            result = query.execute()
            
            if result.data:
                # Remove password hashes from all records
                admins = []
                for admin in result.data:
                    admin_data = {k: v for k, v in admin.items() if k != "password_hash"}
                    admins.append(admin_data)
                return admins
            
            return []
            
        except Exception as e:
            logger.error(f"Error listing admin users: {e}")
            return []
    
    async def update(
        self,
        admin_id: UUID,
        updates: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update admin user.
        
        Args:
            admin_id: Admin UUID to update
            updates: Dict of fields to update
            updated_by: UUID of admin making the update
            
        Returns:
            Updated admin user dict or None if failed
        """
        try:
            # Filter allowed update fields
            allowed_fields = [
                "first_name", "last_name", "email", "role", "is_active"
            ]
            
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not filtered_updates:
                raise ValueError("No valid fields to update")
            
            # Add updated_by if provided
            if updated_by:
                filtered_updates["updated_by"] = str(updated_by)
            
            result = self.client.table(self.table)\
                .update(filtered_updates)\
                .eq("id", str(admin_id))\
                .execute()
            
            if result.data and len(result.data) > 0:
                admin = result.data[0]
                # Remove password hash from returned data
                admin_data = {k: v for k, v in admin.items() if k != "password_hash"}
                
                logger.info(f"Admin user updated: {admin_id}")
                return admin_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating admin user: {e}")
            raise
    
    async def change_password(
        self,
        admin_id: UUID,
        new_password: str,
        updated_by: Optional[UUID] = None
    ) -> bool:
        """
        Change admin user password.
        
        Args:
            admin_id: Admin UUID
            new_password: New plain text password
            updated_by: UUID of admin making the change
            
        Returns:
            True if password changed successfully
        """
        try:
            if not self._validate_password(new_password):
                raise ValueError("Password must be at least 8 characters long")
            
            # Generate new bcrypt hash
            updates = {
                "password_hash": bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                "failed_login_attempts": 0,
                "locked_until": None,
            }
            
            if updated_by:
                updates["updated_by"] = str(updated_by)
            
            result = self.client.table(self.table)\
                .update(updates)\
                .eq("id", str(admin_id))\
                .execute()
            
            if result.data:
                logger.info(f"Admin password changed: {admin_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error changing admin password: {e}")
            raise
    
    async def delete(self, admin_id: UUID, deleted_by: Optional[UUID] = None) -> bool:
        """
        Soft delete admin user (set is_active to false).
        
        Args:
            admin_id: Admin UUID to delete
            deleted_by: UUID of admin making the deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            updates = {
                "is_active": False,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if deleted_by:
                updates["updated_by"] = str(deleted_by)
            
            result = self.client.table(self.table)\
                .update(updates)\
                .eq("id", str(admin_id))\
                .execute()
            
            if result.data:
                logger.info(f"Admin user deleted: {admin_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting admin user: {e}")
            raise
    
    async def update_last_login(self, admin_id: UUID) -> bool:
        """
        Update last login timestamp.
        
        Args:
            admin_id: Admin UUID
            
        Returns:
            True if updated successfully
        """
        try:
            result = self.client.table(self.table)\
                .update({"last_login_at": datetime.utcnow().isoformat()})\
                .eq("id", str(admin_id))\
                .execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    async def _increment_failed_attempts(self, admin_id: UUID, username: str, ip_address: Optional[str]) -> None:
        """Increment failed login attempts and lock account if needed."""
        try:
            # Get current failed attempts
            result = self.client.table(self.table)\
                .select("failed_login_attempts")\
                .eq("id", str(admin_id))\
                .execute()
            
            if not result.data:
                return
            
            current_attempts = result.data[0]["failed_login_attempts"] + 1
            
            updates = {"failed_login_attempts": current_attempts}
            
            # Lock account after 5 failed attempts for 30 minutes
            if current_attempts >= 5:
                lock_until = datetime.utcnow() + timedelta(minutes=30)
                updates["locked_until"] = lock_until.isoformat()
                
                logger.warning(f"Admin account locked due to failed attempts: {username} - IP: {ip_address}")
            
            self.client.table(self.table)\
                .update(updates)\
                .eq("id", str(admin_id))\
                .execute()
                
        except Exception as e:
            logger.error(f"Error incrementing failed attempts: {e}")
    
    async def reset_failed_attempts(self, admin_id: UUID) -> None:
        """Reset failed login attempts counter."""
        try:
            self.client.table(self.table)\
                .update({"failed_login_attempts": 0})\
                .eq("id", str(admin_id))\
                .execute()
        except Exception as e:
            logger.error(f"Error resetting failed attempts: {e}")
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format."""
        if not username or len(username) < 3 or len(username) > 50:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', username))
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
    
    def _validate_password(self, password: str) -> bool:
        """Validate password strength."""
        if not password or len(password) < 8:
            return False
        return True


# Global service instance
_admin_service: Optional[AdminService] = None


def get_admin_service() -> AdminService:
    """
    Get global admin service instance.
    
    Returns:
        AdminService singleton
    """
    global _admin_service
    if _admin_service is None:
        _admin_service = AdminService()
    return _admin_service
