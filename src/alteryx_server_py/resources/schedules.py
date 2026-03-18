"""
Schedule resource for API operations.
"""

import logging
from typing import TYPE_CHECKING, List, Optional

from ..exceptions import NotFoundError, ScheduleNotFoundError
from ..models.common import ScheduleFrequency, ScheduleId
from ..models.schedules import (
    Schedule,
    ScheduleCreateRequest,
    ScheduleUpdateRequest,
)
from ._base import _BaseResource

if TYPE_CHECKING:
    from ..async_client import AsyncAlteryxClient
    from ..client import AlteryxClient

logger = logging.getLogger(__name__)


class ScheduleResource(_BaseResource):
    """Resource for schedule operations.

    Provides methods for managing workflow schedules:
        - List schedules
        - Get schedule details
        - Create new schedules
        - Update schedules
        - Delete schedules
        - Enable/disable schedules
    """

    _client: "AlteryxClient"

    def list(
        self,
        workflow_id: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[Schedule]:
        """List all schedules.

        Args:
            workflow_id: Filter by workflow ID
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            List of Schedule objects
        """
        params = {}
        if workflow_id:
            params["workflowId"] = workflow_id
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size

        logger.debug(f"Listing schedules with params: {params}")

        response = self._client._request(
            "GET",
            "schedules/",
            params=params,
        )

        if isinstance(response, list):
            return [Schedule.model_validate(item) for item in response]
        elif isinstance(response, dict) and "schedules" in response:
            return [Schedule.model_validate(item) for item in response["schedules"]]
        elif isinstance(response, dict):
            return [Schedule.model_validate(response)]

        return []

    def get(self, schedule_id: ScheduleId) -> Schedule:
        """Get schedule details by ID.

        Args:
            schedule_id: Schedule identifier

        Returns:
            Schedule: Schedule details

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        logger.debug(f"Getting schedule: {schedule_id}")

        try:
            response = self._client._request(
                "GET",
                f"schedules/{schedule_id}",
            )
            return Schedule.model_validate(response)
        except NotFoundError:
            raise ScheduleNotFoundError(schedule_id)

    def create(
        self,
        workflow_id: str,
        name: str,
        owner_id: str,
        frequency: str = "Once",
        comment: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        iteration: Optional[str] = None,
    ) -> Schedule:
        """Create a new schedule.

        Args:
            workflow_id: Associated workflow ID
            name: Schedule name
            owner_id: Owner user ID
            frequency: Execution frequency (Once/Hourly/Daily/Weekly/Monthly/Custom)
            comment: Schedule description/comment
            start_date: Schedule start timestamp (ISO format)
            end_date: Schedule end timestamp (ISO format)
            iteration: Iteration details for recurring schedules

        Returns:
            Schedule: Created schedule details
        """
        logger.info(f"Creating schedule '{name}' for workflow: {workflow_id}")

        request = ScheduleCreateRequest(
            workflow_id=workflow_id,
            name=name,
            owner_id=owner_id,
            frequency=ScheduleFrequency(frequency),
            comment=comment,
            start_date=start_date,
            end_date=end_date,
            iteration=iteration,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        response = self._client._request(
            "POST",
            "schedules/",
            json_data=data,
        )

        schedule = Schedule.model_validate(response)
        logger.info(f"Schedule '{name}' created with ID: {schedule.id}")
        return schedule

    def update(
        self,
        schedule_id: ScheduleId,
        name: Optional[str] = None,
        comment: Optional[str] = None,
        frequency: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        iteration: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Schedule:
        """Update an existing schedule.

        Args:
            schedule_id: Schedule identifier
            name: Schedule name
            comment: Schedule description/comment
            frequency: Execution frequency
            start_date: Schedule start timestamp (ISO format)
            end_date: Schedule end timestamp (ISO format)
            iteration: Iteration details
            enabled: Whether schedule is enabled

        Returns:
            Schedule: Updated schedule details

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        logger.info(f"Updating schedule: {schedule_id}")

        freq = ScheduleFrequency(frequency) if frequency else None

        request = ScheduleUpdateRequest(
            name=name,
            comment=comment,
            frequency=freq,
            start_date=start_date,
            end_date=end_date,
            iteration=iteration,
            enabled=enabled,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        try:
            response = self._client._request(
                "PUT",
                f"schedules/{schedule_id}",
                json_data=data,
            )
            schedule = Schedule.model_validate(response)
            logger.info(f"Schedule {schedule_id} updated")
            return schedule
        except NotFoundError:
            raise ScheduleNotFoundError(schedule_id)

    def delete(self, schedule_id: ScheduleId) -> None:
        """Delete a schedule.

        Args:
            schedule_id: Schedule identifier

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        logger.info(f"Deleting schedule: {schedule_id}")

        try:
            self._client._request(
                "DELETE",
                f"schedules/{schedule_id}",
            )
            logger.info(f"Successfully deleted schedule: {schedule_id}")
        except NotFoundError:
            raise ScheduleNotFoundError(schedule_id)

    def enable(self, schedule_id: ScheduleId) -> Schedule:
        """Enable a schedule.

        Args:
            schedule_id: Schedule identifier

        Returns:
            Schedule: Updated schedule details

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        logger.info(f"Enabling schedule: {schedule_id}")

        try:
            response = self._client._request(
                "POST",
                f"schedules/{schedule_id}/enable",
            )
            return Schedule.model_validate(response)
        except NotFoundError:
            raise ScheduleNotFoundError(schedule_id)

    def disable(self, schedule_id: ScheduleId) -> Schedule:
        """Disable a schedule.

        Args:
            schedule_id: Schedule identifier

        Returns:
            Schedule: Updated schedule details

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        logger.info(f"Disabling schedule: {schedule_id}")

        try:
            response = self._client._request(
                "POST",
                f"schedules/{schedule_id}/disable",
            )
            return Schedule.model_validate(response)
        except NotFoundError:
            raise ScheduleNotFoundError(schedule_id)


class AsyncScheduleResource(_BaseResource):
    """Asynchronous schedule resource.

    Provides async versions of all ScheduleResource methods.
    """

    _client: "AsyncAlteryxClient"

    async def list(
        self,
        workflow_id: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[Schedule]:
        """List all schedules (async).

        Args:
            workflow_id: Filter by workflow ID
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            List of Schedule objects
        """
        params = {}
        if workflow_id:
            params["workflowId"] = workflow_id
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size

        logger.debug(f"Listing schedules with params: {params}")

        response = await self._client._request(
            "GET",
            "schedules/",
            params=params,
        )

        if isinstance(response, list):
            return [Schedule.model_validate(item) for item in response]
        elif isinstance(response, dict) and "schedules" in response:
            return [Schedule.model_validate(item) for item in response["schedules"]]
        elif isinstance(response, dict):
            return [Schedule.model_validate(response)]

        return []

    async def get(self, schedule_id: ScheduleId) -> Schedule:
        """Get schedule details by ID (async).

        Args:
            schedule_id: Schedule identifier

        Returns:
            Schedule: Schedule details

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        logger.debug(f"Getting schedule: {schedule_id}")

        try:
            response = await self._client._request(
                "GET",
                f"schedules/{schedule_id}",
            )
            return Schedule.model_validate(response)
        except NotFoundError:
            raise ScheduleNotFoundError(schedule_id)

    async def create(
        self,
        workflow_id: str,
        name: str,
        owner_id: str,
        frequency: str = "Once",
        comment: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        iteration: Optional[str] = None,
    ) -> Schedule:
        """Create a new schedule (async).

        Args:
            workflow_id: Associated workflow ID
            name: Schedule name
            owner_id: Owner user ID
            frequency: Execution frequency
            comment: Schedule description/comment
            start_date: Schedule start timestamp (ISO format)
            end_date: Schedule end timestamp (ISO format)
            iteration: Iteration details

        Returns:
            Schedule: Created schedule details
        """
        logger.info(f"Creating schedule '{name}' for workflow: {workflow_id}")

        request = ScheduleCreateRequest(
            workflow_id=workflow_id,
            name=name,
            owner_id=owner_id,
            frequency=ScheduleFrequency(frequency),
            comment=comment,
            start_date=start_date,
            end_date=end_date,
            iteration=iteration,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client._request(
            "POST",
            "schedules/",
            json_data=data,
        )

        schedule = Schedule.model_validate(response)
        logger.info(f"Schedule '{name}' created with ID: {schedule.id}")
        return schedule

    async def update(
        self,
        schedule_id: ScheduleId,
        name: Optional[str] = None,
        comment: Optional[str] = None,
        frequency: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        iteration: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Schedule:
        """Update an existing schedule (async).

        Args:
            schedule_id: Schedule identifier
            name: Schedule name
            comment: Schedule description/comment
            frequency: Execution frequency
            start_date: Schedule start timestamp (ISO format)
            end_date: Schedule end timestamp (ISO format)
            iteration: Iteration details
            enabled: Whether schedule is enabled

        Returns:
            Schedule: Updated schedule details

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        logger.info(f"Updating schedule: {schedule_id}")

        freq = ScheduleFrequency(frequency) if frequency else None

        request = ScheduleUpdateRequest(
            name=name,
            comment=comment,
            frequency=freq,
            start_date=start_date,
            end_date=end_date,
            iteration=iteration,
            enabled=enabled,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        try:
            response = await self._client._request(
                "PUT",
                f"schedules/{schedule_id}",
                json_data=data,
            )
            schedule = Schedule.model_validate(response)
            logger.info(f"Schedule {schedule_id} updated")
            return schedule
        except NotFoundError:
            raise ScheduleNotFoundError(schedule_id)

    async def delete(self, schedule_id: ScheduleId) -> None:
        """Delete a schedule (async).

        Args:
            schedule_id: Schedule identifier

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        logger.info(f"Deleting schedule: {schedule_id}")

        try:
            await self._client._request(
                "DELETE",
                f"schedules/{schedule_id}",
            )
            logger.info(f"Successfully deleted schedule: {schedule_id}")
        except NotFoundError:
            raise ScheduleNotFoundError(schedule_id)

    async def enable(self, schedule_id: ScheduleId) -> Schedule:
        """Enable a schedule (async).

        Args:
            schedule_id: Schedule identifier

        Returns:
            Schedule: Updated schedule details

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        logger.info(f"Enabling schedule: {schedule_id}")

        try:
            response = await self._client._request(
                "POST",
                f"schedules/{schedule_id}/enable",
            )
            return Schedule.model_validate(response)
        except NotFoundError:
            raise ScheduleNotFoundError(schedule_id)

    async def disable(self, schedule_id: ScheduleId) -> Schedule:
        """Disable a schedule (async).

        Args:
            schedule_id: Schedule identifier

        Returns:
            Schedule: Updated schedule details

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        logger.info(f"Disabling schedule: {schedule_id}")

        try:
            response = await self._client._request(
                "POST",
                f"schedules/{schedule_id}/disable",
            )
            return Schedule.model_validate(response)
        except NotFoundError:
            raise ScheduleNotFoundError(schedule_id)
