import httpx
from typing import Dict, Any, List, Optional
import json
from loguru import logger
from .types import SplitwiseMember, SplitwiseGroup, SplitwiseExpense, RequestMethod, SplitwiseApiPaths, \
    SplitwiseExpenseParticipant
from tools.secrets import SecretsManager


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
            sm = SecretsManager()
            access_token = sm.get_secret("splitwise_api_key")
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
        response_data = self._request(RequestMethod.GET, SplitwiseApiPaths.GET_GROUPS)
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
        response_data = self._request(RequestMethod.GET, SplitwiseApiPaths.GET_GROUP.format(group_id=group_id))
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

    def get_current_user(self) -> SplitwiseMember:
        logger.info("Fetching current Splitwise user...")
        response_data = self._request(RequestMethod.GET, SplitwiseApiPaths.GET_CURRENT_USER)
        return SplitwiseMember(**response_data.get("user"))

    def get_friends(self) -> List[SplitwiseMember]:
        """
        Fetches a list of friends of the authenticated user.
        API Doc: https://dev.splitwise.com/#tag/friends/paths/~1get_friends/get

        Returns:
            A list of SplitwiseMember objects representing the user's friends.
        """
        logger.info("Fetching Splitwise friends...")
        response_data = self._request(RequestMethod.GET, SplitwiseApiPaths.GET_FRIENDS)
        return [SplitwiseMember(**friend) for friend in response_data.get("friends", [])]

    def _handle_direct_expense_participants(
        self,
        friend_id: int,
        friend_paid_share: float,
        friend_owed_share: float,
        cost: float,
        split_equally: bool
    ) -> List[SplitwiseExpenseParticipant]:
        """
        Handles the participants for a direct expense, ensuring the shares are calculated correctly.
        This method calculates the paid and owed shares for both the user and their friend based on whether the expense is split equally or not.

        Args:
            friend_id: The ID of the friend who paid.
            friend_paid_share: The amount the friend paid.
            friend_owed_share: The amount the friend owes, in total, if not splitting equally.
                This is the amount of their expense on their receipt, even if they paid
            cost: The total cost of the expense.
            split_equally: Whether to split the expense equally among participants.

        Returns:
            A list of SplitwiseExpenseParticipant objects.
        """
        my_user_id = self.get_current_user().id
        if split_equally:
            cost_per_person = cost / 2
            friend_owed_share = cost_per_person
            my_owed_share = cost_per_person
            my_paid_share = cost - friend_paid_share
        else:
            my_paid_share = cost - friend_paid_share
            my_owed_share = cost - friend_owed_share
        return [
            SplitwiseExpenseParticipant(user_id=friend_id, paid_share=friend_paid_share, owed_share=friend_owed_share),
            SplitwiseExpenseParticipant(user_id=my_user_id, paid_share=my_paid_share, owed_share=my_owed_share),
        ]

    def create_direct_expense_by_name(self, name: str, cost: float, description: str,
                                      friend_paid_share: Optional[float] = 0.0,
                                      friend_owed_share: Optional[float] = 0.0,
                                      currency_code: str = "PLN", split_equally: bool = True) -> Dict[str, Any]:
        """
        Creates a direct expense in Splitwise for a specific friend by their name.
        This method searches for the friend by name, constructs the expense details, and calls the Splitwise API to create the expense.
        Args:
            name (str): The name of the friend to whom the expense is attributed.
            cost (float): The total cost of the expense.
            description (str): A brief description of the expense.
            friend_paid_share (float, optional): The amount the friend paid for the expense. Defaults to 0.0.
                Should be either set to 0, in case I paid, or the total cost, in case the friend paid.
            friend_owed_share (float, optional): The amount the friend owes for the expense. Defaults to 0.0.
                Only needed in case the expense is not split equally.
            currency_code (str, optional): The currency code for the expense. Defaults to "PLN".
            split_equally (bool, optional): Whether to split the expense equally among participants. Defaults to True.
        """
        friends = self.get_friends()
        friend_id = None
        for friend in friends:
            if name.lower() == f"{friend.first_name} {friend.last_name}".lower():
                logger.debug(f"Found friend with name '{name}' in Splitwise.")
                friend_id = friend.id
                break
        if friend_id is None:
            raise ValueError(f"Friend '{name}' not found in Splitwise.")
        expense = SplitwiseExpense(
            cost=cost,
            description=description,
            currency_code=currency_code,
            participants=self._handle_direct_expense_participants(friend_id, friend_paid_share, friend_owed_share, cost, split_equally),
            split_equally=False # dont use split_equally for direct expenses
        )
        logger.debug(f"Creating direct expense with {name} for receipt: {expense}")
        return self._create_expense(expense)

    def _create_expense(
        self,
        expense: SplitwiseExpense
    ) -> Dict[str, Any]:
        """
        Creates a new expense in Splitwise.
        """

        payload = expense.to_api_payload()
        logger.debug(f"Creating expense with payload: {json.dumps(payload, indent=2)}")
        response_data = self._request(RequestMethod.POST, SplitwiseApiPaths.CREATE_EXPENSE, data=payload)
        return response_data.get("expenses", [])[0] if response_data.get("expenses") else response_data
