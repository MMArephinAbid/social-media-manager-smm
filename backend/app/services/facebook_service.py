"""
Facebook Graph API Service.
Created by: Sadia (Backend Lead)

Handles all Facebook API interactions:
- OAuth flow
- Page management
- Comment fetching
- Reply posting
"""
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode
import httpx

from ..config import settings
from ..core.exceptions import (
    FacebookException,
    FacebookTokenExpiredException,
    FacebookRateLimitException,
)
from ..core.security import encrypt_string, decrypt_string


class FacebookService:
    """Service for Facebook Graph API interactions."""

    def __init__(self):
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
        self.api_version = settings.FACEBOOK_API_VERSION
        self.base_url = settings.facebook_graph_api_url

    def get_oauth_url(self, redirect_uri: str, state: str) -> str:
        """
        Generate Facebook OAuth authorization URL.

        Args:
            redirect_uri: Callback URL after authorization
            state: State parameter for CSRF protection

        Returns:
            Facebook OAuth URL
        """
        params = {
            "client_id": self.app_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": ",".join([
                "pages_show_list",
                "pages_read_engagement",
                "pages_manage_metadata",
                "pages_read_user_content",
                "pages_manage_posts",
                "pages_manage_engagement",
                "public_profile",
            ]),
            "response_type": "code",
        }
        return f"https://www.facebook.com/{self.api_version}/dialog/oauth?{urlencode(params)}"

    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Same redirect URI used in authorization

        Returns:
            Dict with access_token, token_type, expires_in
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/oauth/access_token",
                params={
                    "client_id": self.app_id,
                    "client_secret": self.app_secret,
                    "redirect_uri": redirect_uri,
                    "code": code,
                }
            )

            if response.status_code != 200:
                raise FacebookException(
                    message="Failed to exchange code for token",
                    details=response.json()
                )

            return response.json()

    async def get_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """
        Exchange short-lived token for long-lived token (60 days).

        Args:
            short_lived_token: Short-lived access token

        Returns:
            Dict with access_token, token_type, expires_in
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": self.app_id,
                    "client_secret": self.app_secret,
                    "fb_exchange_token": short_lived_token,
                }
            )

            if response.status_code != 200:
                raise FacebookException(
                    message="Failed to get long-lived token",
                    details=response.json()
                )

            return response.json()

    async def get_user_pages(self, user_access_token: str) -> List[Dict[str, Any]]:
        """
        Get list of Facebook pages the user manages.

        Args:
            user_access_token: User's access token

        Returns:
            List of pages with id, name, access_token, etc.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/me/accounts",
                params={
                    "access_token": user_access_token,
                    "fields": "id,name,category,picture,access_token,followers_count",
                }
            )

            data = response.json()

            if "error" in data:
                self._handle_error(data["error"])

            return data.get("data", [])

    async def get_page_info(
        self,
        page_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a Facebook page.

        Args:
            page_id: Facebook page ID
            access_token: Page access token

        Returns:
            Page information dict
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{page_id}",
                params={
                    "access_token": access_token,
                    "fields": "id,name,category,picture,link,followers_count,fan_count",
                }
            )

            data = response.json()

            if "error" in data:
                self._handle_error(data["error"])

            return data

    async def subscribe_to_webhooks(
        self,
        page_id: str,
        access_token: str
    ) -> bool:
        """
        Subscribe page to webhook notifications.

        Args:
            page_id: Facebook page ID
            access_token: Page access token

        Returns:
            True if successful
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{page_id}/subscribed_apps",
                params={
                    "access_token": access_token,
                    "subscribed_fields": "feed,mention,comments",
                }
            )

            data = response.json()

            if "error" in data:
                self._handle_error(data["error"])

            return data.get("success", False)

    async def unsubscribe_from_webhooks(
        self,
        page_id: str,
        access_token: str
    ) -> bool:
        """
        Unsubscribe page from webhook notifications.

        Args:
            page_id: Facebook page ID
            access_token: Page access token

        Returns:
            True if successful
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/{page_id}/subscribed_apps",
                params={"access_token": access_token}
            )

            data = response.json()

            if "error" in data:
                self._handle_error(data["error"])

            return data.get("success", False)

    async def get_post_comments(
        self,
        post_id: str,
        access_token: str,
        limit: int = 100,
        after: str = None
    ) -> Dict[str, Any]:
        """
        Get comments on a post.

        Args:
            post_id: Facebook post ID
            access_token: Page access token
            limit: Number of comments to fetch
            after: Pagination cursor

        Returns:
            Dict with data (comments) and paging info
        """
        params = {
            "access_token": access_token,
            "fields": "id,message,from,created_time,attachment,parent",
            "limit": limit,
        }
        if after:
            params["after"] = after

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{post_id}/comments",
                params=params
            )

            data = response.json()

            if "error" in data:
                self._handle_error(data["error"])

            return data

    async def get_comment(
        self,
        comment_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get a single comment by ID.

        Args:
            comment_id: Facebook comment ID
            access_token: Page access token

        Returns:
            Comment data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{comment_id}",
                params={
                    "access_token": access_token,
                    "fields": "id,message,from,created_time,attachment,parent,object",
                }
            )

            data = response.json()

            if "error" in data:
                self._handle_error(data["error"])

            return data

    async def reply_to_comment(
        self,
        comment_id: str,
        message: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Reply to a comment.

        Args:
            comment_id: Facebook comment ID to reply to
            message: Reply message text
            access_token: Page access token

        Returns:
            Dict with id of the reply
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{comment_id}/comments",
                params={"access_token": access_token},
                data={"message": message}
            )

            data = response.json()

            if "error" in data:
                self._handle_error(data["error"])

            return data

    async def get_post(
        self,
        post_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get post details.

        Args:
            post_id: Facebook post ID
            access_token: Page access token

        Returns:
            Post data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{post_id}",
                params={
                    "access_token": access_token,
                    "fields": "id,message,type,created_time,permalink_url",
                }
            )

            data = response.json()

            if "error" in data:
                self._handle_error(data["error"])

            return data

    def _handle_error(self, error: Dict[str, Any]) -> None:
        """Handle Facebook API error response."""
        error_code = error.get("code")
        error_message = error.get("message", "Unknown Facebook error")

        # Token expired
        if error_code in [190, 102]:
            raise FacebookTokenExpiredException()

        # Rate limit
        if error_code in [4, 17, 32, 613]:
            raise FacebookRateLimitException()

        # Generic error
        raise FacebookException(
            message=error_message,
            fb_error_code=error_code,
            details=error
        )


# Singleton instance
facebook_service = FacebookService()
