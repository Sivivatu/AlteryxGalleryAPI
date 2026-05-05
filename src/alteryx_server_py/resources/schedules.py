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
        """List schedules visible to the current caller.

        Args:
            workflow_id: Optional workflow ID filter.
            page: Optional 1-indexed page number.
            page_size: Optional page size.

        Returns:
            List[Schedule]: Matching schedule models.
        """
        params = {}
        if workflow_id is not None:
            params["workflowId"] = workflow_id
        if page is not None:
            params["page"] = page
        if page_size is not None:
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
        """Retrieve a schedule by identifier.

        Args:
            schedule_id: Schedule identifier.

        Returns:
            Schedule: Resolved schedule model.

        Raises:
            ScheduleNotFoundError: If the schedule does not exist.
        """
        logger.debug(f"Getting schedule: {schedule_id}")

        try:
            response = self._client._request(
                "GET",
                f"schedules/{schedule_id}",
            )
            return Schedule.model_validate(response)
        except NotFoundError as exc:
            raise ScheduleNotFoundError(schedule_id) from exc

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
        """Create a schedule for a workflow.

        Args:
            workflow_id: Workflow to schedule.
            name: Schedule display name.
            owner_id: Owner user identifier.
            frequency: Schedule frequency string.
            comment: Optional schedule description.
            start_date: Optional ISO-formatted start timestamp.
            end_date: Optional ISO-formatted end timestamp.
            iteration: Optional recurrence configuration.

        Returns:
            Schedule: Newly created schedule model.
        """
        logger.info(f"Creating schedule '{name}' for workflow: {workflow_id}")

        request = ScheduleCreateRequest(
            workflowId=workflow_id,
            name=name,
            ownerId=owner_id,
            frequency=ScheduleFrequency(frequency),
            comment=comment,
            startDate=start_date,
            endDate=end_date,
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
        """Update a schedule in place.

        Args:
            schedule_id: Schedule identifier.
            name: Updated schedule name.
            comment: Updated schedule description.
            frequency: Updated frequency value.
            start_date: Optional ISO-formatted start timestamp.
            end_date: Optional ISO-formatted end timestamp.
            iteration: Optional recurrence configuration.
            enabled: Optional enabled flag.

        Returns:
            Schedule: Updated schedule model.

        Raises:
            ScheduleNotFoundError: If the schedule does not exist.
        """
        logger.info(f"Updating schedule: {schedule_id}")

        freq = ScheduleFrequency(frequency) if frequency else None

        request = ScheduleUpdateRequest(
            name=name,
            comment=comment,
            frequency=freq,
            startDate=start_date,
            endDate=end_date,
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
        except NotFoundError as exc:
            raise ScheduleNotFoundError(schedule_id) from exc

    def delete(self, schedule_id: ScheduleId) -> None:
        """Delete a schedule.

        Args:
            schedule_id: Schedule identifier.

        Raises:
            ScheduleNotFoundError: If the schedule does not exist.
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
        """Enable a disabled schedule.

        Args:
            schedule_id: Schedule identifier.

        Returns:
            Schedule: Updated schedule model.

        Raises:
            ScheduleNotFoundError: If the schedule does not exist.
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
        """Disable an active schedule.

        Args:
            schedule_id: Schedule identifier.

        Returns:
            Schedule: Updated schedule model.

        Raises:
            ScheduleNotFoundError: If the schedule does not exist.
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
        """List schedules visible to the current caller.

        Args:
            workflow_id: Optional workflow ID filter.
            page: Optional 1-indexed page number.
            page_size: Optional page size.

        Returns:
            List[Schedule]: Matching schedule models.
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
        """Retrieve a schedule by identifier.

        Args:
            schedule_id: Schedule identifier.

        Returns:
            Schedule: Resolved schedule model.

        Raises:
            ScheduleNotFoundError: If the schedule does not exist.
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
        """Create a schedule for a workflow.

        Args:
            workflow_id: Workflow to schedule.
            name: Schedule display name.
            owner_id: Owner user identifier.
            frequency: Schedule frequency string.
            comment: Optional schedule description.
            start_date: Optional ISO-formatted start timestamp.
            end_date: Optional ISO-formatted end timestamp.
            iteration: Optional recurrence configuration.

        Returns:
            Schedule: Newly created schedule model.
        """
        logger.info(f"Creating schedule '{name}' for workflow: {workflow_id}")

        request = ScheduleCreateRequest(
            workflowId=workflow_id,
            name=name,
            ownerId=owner_id,
            frequency=ScheduleFrequency(frequency),
            comment=comment,
            startDate=start_date,
            endDate=end_date,
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
        """Update a schedule in place.

        Args:
            schedule_id: Schedule identifier.
            name: Updated schedule name.
            comment: Updated schedule description.
            frequency: Updated frequency value.
            start_date: Optional ISO-formatted start timestamp.
            end_date: Optional ISO-formatted end timestamp.
            iteration: Optional recurrence configuration.
            enabled: Optional enabled flag.

        Returns:
            Schedule: Updated schedule model.

        Raises:
            ScheduleNotFoundError: If the schedule does not exist.
        """
        logger.info(f"Updating schedule: {schedule_id}")

        freq = ScheduleFrequency(frequency) if frequency else None

        request = ScheduleUpdateRequest(
            name=name,
            comment=comment,
            frequency=freq,
            startDate=start_date,
            endDate=end_date,
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
        except NotFoundError as exc:
            raise ScheduleNotFoundError(schedule_id) from exc

    async def delete(self, schedule_id: ScheduleId) -> None:
        """Delete a schedule (async).

        Args:
            schedule_id: Schedule identifier.

        Raises:
            ScheduleNotFoundError: If the schedule does not exist.
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
        """Enable a disabled schedule.

        Args:
            schedule_id: Schedule identifier.

        Returns:
            Schedule: Updated schedule model.

        Raises:
            ScheduleNotFoundError: If the schedule does not exist.
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
        """Disable an active schedule.

        Args:
            schedule_id: Schedule identifier.

        Returns:
            Schedule: Updated schedule model.

        Raises:
            ScheduleNotFoundError: If the schedule does not exist.
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
