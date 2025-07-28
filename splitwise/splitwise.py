import os
import httpx
from typing import Dict, Any, List, Optional
import json
from loguru import logger
from .types import SplitwiseMember, SplitwiseGroup


class Splitwise:
    """
    A Data Access Object (DAO) for interacting with the Splitwise API.
    Uses a Bearer token for authentication.
    """
    BASE_URL = "https://secure.splitwise.com/api/v3.0"

    def __init__(self, access_token: Optional[str] = None):
        """
        Initializes the Splitwise DAO with an access token.

        Args:
            access_token (str | None): The Bearer token for authentication.
        """
        if not access_token:
            access_token = os.getenv("SPLITWISE_API_KEY")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        self.client = httpx.Client(base_url=self.BASE_URL, headers=headers)

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """
        Internal helper to make authenticated requests to the Splitwise API.

        Args:
            method: HTTP method (e.g., "GET", "POST").
            path: The API endpoint path (e.g., "/get_groups").
            **kwargs: Additional arguments to pass to httpx.request (e.g., json, params, data).

        Returns:
            The JSON response from the API.

        Raises:
            httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
            httpx.RequestError: For network-related errors.
            ValueError: If the API returns unparseable JSON for error details.
        """
        try:
            response = self.client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Splitwise API Error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Splitwise Network Error: Failed to connect or send request to {e.request.url!r}: {e}")
            raise
        except json.JSONDecodeError:
            # This handles cases where 200 OK might return non-JSON, but is less likely with raise_for_status
            logger.error(f"Splitwise API returned non-JSON response for successful request: {response.text}")
            raise ValueError("Invalid JSON response from Splitwise API for expected success.")


    def get_groups(self) -> List[SplitwiseGroup]:
        """
        Fetches a list of groups the authenticated user belongs to.
        API Doc: https://dev.splitwise.com/#tag/groups/paths/~1get_groups/get

        Returns:
            A list of dictionaries, where each dictionary represents a group.
        """
        logger.info("Fetching Splitwise groups...")
        response_data = self._request("GET", "/get_groups")
        return [SplitwiseGroup(**group) for group in response_data.get("groups", [])]

    def _get_group_id_by_name(self, group_name: str) -> Optional[int]:
        """
        Retrieves the ID of a group by its name.

        Args:
            group_name: The name of the group to search for.

        Returns:
            The ID of the group if found, otherwise None.
        """
        logger.info(f"Searching for Splitwise group: {group_name}")
        groups = self.get_groups()
        for group in groups:
            if group.name.strip() == group_name:
                return group.id
        logger.warning(f"Group '{group_name}' not found in Splitwise.")
        return None

    def _get_group(self, group_id: int) -> SplitwiseGroup:
        """
        Fetches the members of a specific group by its ID.
        API Doc: https://dev.splitwise.com/#tag/groups/paths/~1get_group_members/get

        Args:
            group_id: The ID of the group to fetch members for.

        Returns:
            A list of dictionaries, where each dictionary represents a member of the group.
        """
        logger.info(f"Fetching members for Splitwise group ID: {group_id}")
        response_data = self._request("GET", f"/get_group/{group_id}")
        return SplitwiseGroup(**response_data.get("group", {}))

    def get_group_by_name(self, group_name: str) -> SplitwiseGroup | None:
        """
        Retrieves the details of a group by its name.

        Args:
            group_name: The name of the group to search for.

        Returns:
            A dictionary representing the group details if found, otherwise None.
        """
        group_id = self._get_group_id_by_name(group_name)
        if group_id is not None:
            return self._get_group(group_id)
        return None

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        logger.info("Fetching current Splitwise user...")
        response_data = self._request("GET", "/get_current_user")
        return response_data.get("user")

    def create_expense(
        self,
        cost: float,
        description: str,
        split_equally: Optional[bool] = None,
        group_id: Optional[int] = None,
        currency_code: str = "PLN",
        date: Optional[str] = None,
        users: Optional[List[Dict[str, Any]]] = None,
        category_id: Optional[int] = None,
        details: Optional[str] = None,
        receipt_image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a new expense in Splitwise.
        """
        logger.info(f"Creating Splitwise expense: {description} (Cost: {cost} {currency_code})")

        payload = {
            "cost": f"{cost:.2f}",
            "description": description,
            "currency_code": currency_code,
        }

        if group_id is not None:
            payload["group_id"] = group_id
        if date is not None:
            payload["date"] = date
        if category_id is not None:
            payload["category_id"] = category_id
        if details is not None:
            payload["details"] = details
        if receipt_image_url is not None:
            payload["receipt_image"] = receipt_image_url

        if split_equally is not None:
            payload["split_equally"] = str(split_equally).lower()

        # Handle 'users' parameter for custom splits (already correctly implemented)
        if users:
            for i, user_data in enumerate(users):
                payload[f"users___{i}___user_id"] = user_data["user_id"]
                payload[f"users___{i}___paid_share"] = f"{user_data['paid_share']:.2f}"
                if "owed_share" in user_data:
                    payload[f"users___{i}___owed_share"] = f"{user_data['owed_share']:.2f}"
                # Add other user properties if needed, e.g., first_name, last_name, email for new users
                if "first_name" in user_data:
                    payload[f"users___{i}___first_name"] = user_data["first_name"]
                if "last_name" in user_data:
                    payload[f"users___{i}___last_name"] = user_data["last_name"]
                if "email" in user_data:
                    payload[f"users___{i}___email"] = user_data["email"]

        response_data = self._request("POST", "/create_expense", data=payload)
        return response_data.get("expenses", [])[0] if response_data.get("expenses") else response_data
