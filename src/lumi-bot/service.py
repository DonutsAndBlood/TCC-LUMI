import asyncio
import functools
import logging
from asyncio import Task, TaskGroup
from typing import Any, Awaitable, Callable, Dict


class Service:
    """A class representing an asynchronous service that can be started and managed."""

    name: str
    running: bool
    task: Task[Awaitable[Any]] | None
    func: Callable[[], Awaitable[Any]]

    def __init__(self, func: Callable[[], Awaitable[Any]], name: str | None = None):
        """
        Initialize the Service with a function to run.

        :param func: A callable that returns an Awaitable (e.g., an async function).
        """
        self.name = name or func.__name__
        self.running = False
        self.task = None
        self.func = func

    async def __call__(self) -> Any:
        return await self.func()


class ServicesHandler:
    """A handler for managing multiple asynchronous services."""

    services: Dict[int, Service]
    running_count: int

    def __init__(self):
        """Initialize the async services handler."""
        self.running_count = 0
        self.services = {}

    def add_service(self, service: Service) -> int:
        """
        Add a service to the handler. \\
        Returns a unique key for the service.

        :param service: The Service instance to add.
        :return int: A unique key (id) for the service.
        """
        key = id(service)
        self.services[key] = service
        return key

    def run_service(self, service_id: int) -> Task[Any] | None:
        """Run a service from the handler."""
        service = self.services.get(service_id)

        if not service:
            print(f"Service with key {service_id} not found.")
            return None

        if service.running:
            print(f"Service {service} is already running.")
            return service.task

        task = self.__create_task(service)
        return task

    async def run_all_services(self) -> None:
        """Run all services in the handler."""
        async with asyncio.TaskGroup() as tg:
            for service in self.services.values():
                if not service.running:
                    self.__create_grouped_task(service, tg)
            logging.info("All services are now running.")
        del tg

    def add_and_run_service(self, service: Service) -> None:
        """Add a service to the handler and immediately run it."""
        self.add_service(service)
        self.run_service(id(service))

    def __create_task(self, service: Service) -> Task[Any]:
        """
        Create a asyncio task for the service.
        This function also marks the service as started and adds a done callback \\
        to mark it as stopped when the task is done.

        :param service: The service to create a task for.
        :return: The created asyncio Task.
        """
        task = asyncio.create_task(service())
        logging.info("Service %s is now running.", service.name)
        self.__mark_service_started(service, task)
        task.add_done_callback(functools.partial(self.__handle_service_done, service))
        return task

    def __create_grouped_task(self, service: Service, tg: TaskGroup) -> Task[Any]:
        task = tg.create_task(service())
        self.__mark_service_started(service, task)
        task.add_done_callback(functools.partial(self.__handle_service_done, service))
        return task

    def __mark_service_started(self, service: Service, task: Task[Any]) -> None:
        """Mark a service as started."""
        service.running = True
        service.task = task
        self.running_count += 1

    async def __handle_service_done(self, service: Service, future: Task[Any]) -> None:
        """
        Mark a service as stopped.

        :param service: The service that has stopped.
        :param future: The Task of the service that is done.
        :return: None
        """
        service.running = False
        self.running_count -= 1

        if future.cancelled():
            logging.warning("Service %s was cancelled", service.name)

        elif future.exception():
            logging.exception(
                "Service %s stopped because of an exception",
                service.name,
            )

        else:
            logging.info("Service %s has stopped", service.name)

    @property
    def active_services(self) -> int:
        """Return the number of active services."""
        return self.running_count
