import asyncio
import functools
import logging
from asyncio import AbstractEventLoop, Task, TaskGroup
from contextvars import Context
from typing import Any, Awaitable, Callable, Dict, List, Optional


class Service:
    """A class representing a service to be managed by :class:`service.ServiceHandler`.

    | This class wraps a coroutine function, this function can then be managed through
    | :class:`service.ServiceHandler`. It supports running the coroutine as a
    | task either in the current event loop, optionally created inside a task group,
    | or inside a separate thread.

    | It support some optional named parameters to be passed to the coroutine: A custom
    | function name, a context to be passed to the task, and a boolean to
    | determine if the function runs in another thread.
    | It also has two properties:
    | A task property that returns the current task, and a running property that
    | returns the status of the coroutine task.

    :param func: The coroutine function.
    :param Optional[str] name: Custom name for the service (defaults to func.__name__).
    :param bool thread: Whether the service runs in a separate thread (default False).
    """

    name: str
    running: bool
    thread: bool
    task: Task[Awaitable[Any]] | None
    func: Callable[[], Awaitable[Any]]
    context: Context
    loops: List[AbstractEventLoop]

    def __init__(
        self,
        func: Callable[[], Awaitable[Any]],
        *,
        context: Optional[Context] = None,
        name: Optional[str] = None,
        thread: bool = False,
        loops: Optional[List[AbstractEventLoop]] = None,
    ):
        self.name = name or func.__name__
        self.running = False
        self.task = None
        self.func = func
        self.context = context or Context()
        self.thread = thread
        self.loops = loops or []

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
        """Add a service to the handler.

        :param Service service: The :class:`service.Service` instance to add.
        :return int: The id value of the service.
        """
        key = id(service)
        self.services[key] = service
        return key

    def add_services(self, services: List[Service]) -> List[int]:
        """Add multiple services to the handler.

        :param List[Service] service: The Service instance to add.
        :return List[int]: The id value of each service.
        """
        for service in services:
            key = id(service)
            self.services[key] = service

        return [id(service) for service in services]

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
                    self.__create_task(service, tg)
            logging.info("All services are now running.")
        del tg

    def add_and_run_service(self, service: Service) -> None:
        """Add a service to the handler and immediately run it."""
        self.add_service(service)
        self.run_service(id(service))

    def __create_task(
        self,
        service: Service,
        tg: Optional[TaskGroup] = None,
    ) -> Task[Any]:
        """Create an asyncio task for the service.

        | Create an asyncio task for the service, marks the service as started and
        | adds a callback to mark the service as stopped when the task is done.

        :param Service service: The service to create a task for.
        :param Optional[TaskGroup] tg: Optional task group to run the task.
        :return Task[Any]: The created asyncio Task.
        """
        task: Task[Any]
        if tg is None:
            task = asyncio.create_task(service())
        else:
            task = tg.create_task(service())

        logging.info("Service %s is now running.", service.name)
        self.__mark_service_started(service, task)
        task.add_done_callback(functools.partial(self.__handle_service_done, service))
        return task

    def __mark_service_started(self, service: Service, task: Task[Any]) -> None:
        """Mark a service as started."""
        service.running = True
        service.task = task
        self.running_count += 1

    async def __handle_service_done(self, service: Service, future: Task[Any]) -> None:
        """Mark a service as stopped.

        :param Service service: The service that has stopped.
        :param Task[Any] future: The Task of the service that is done.
        :return None:
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
