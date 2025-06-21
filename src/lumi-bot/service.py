import asyncio
import functools
import logging
from asyncio import Task, TaskGroup
from contextvars import Context
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set


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
    :param Optional[Context] context: Context object to pass to the task. If None,
        a new empty context is created.
    :param bool thread: Whether the service runs in a separate thread (default False).
    """

    name: str
    thread: bool
    func: Callable[[], Awaitable[Any]]
    context: Context

    __task: Task[Awaitable[Any]] | None

    def __init__(
        self,
        func: Callable[[], Awaitable[Any]],
        *,
        context: Optional[Context] = None,
        name: Optional[str] = None,
        thread: bool = False,
    ):
        self.name = name or func.__name__
        self.func = func
        self.context = context or Context()
        self.thread = thread

        self.__task = None

    def __call__(self) -> Task[Awaitable[Any]]:
        """Executes the service by calling self.run().

        This allows the service instance to be used as a callable,
        providing a convenient shortcut for run().

        :return Task[Awaitable[Any]]: The result of the run() method.
        """
        return self.run()

    def run(
        self,
        *,
        tg: Optional[TaskGroup] = None,
        done_callback: Callable[[Task[Any]], Any] | None = None,
    ) -> Task[Awaitable[Any]]:
        """Execute the service's coroutine function and return the created task.

        | This method creates and starts an asyncio task for the service coroutine
        | function, the task can be created directly or within a provided TaskGroup.

        :param Optional[TaskGroup] tg: TaskGroup to create the task within. If None,
            creates the task using asyncio.create_task.
        :param done_callback: Callback function to be executed when the task completes.
        :type done_callback: Callable[[Task[Any]], Any] | None
        :return Task[Awaitable[Any]]: The created asyncio task.
        """
        create_task = asyncio.create_task if tg is None else tg.create_task
        self.__task = task = create_task(
            self.__await_func(),
            name=self.name,
            context=self.context,
        )

        if done_callback is not None:
            task.add_done_callback(done_callback)
        return task

    async def __await_func(self) -> Any:
        """Internal method that awaits and returns the result of the service's function.

        This is the actual coroutine that gets wrapped in a task by run().

        :return: The result of the service's coroutine function.
        :rtype: Any
        """
        return await self.func()

    @property
    def task(self) -> Task[Awaitable[Any]] | None:
        """Get the current task associated with this service.

        :return: The asyncio task if running, None otherwise.
        :rtype: Task[Awaitable[Any]] | None
        """
        return self.__task

    @property
    def running(self) -> bool:
        """Check if the service task is currently running.

        :return bool: True if task exists and is not done, False otherwise.
        """
        if self.task is None:
            return False
        return not self.task.done()

    @property
    def id(self) -> int:
        """Get the unique identifier for this service instance.

        :return int: The service memory address identifier.
        """
        return id(self)


class ServicesHandler:
    """A handler for managing multiple asynchronous services."""

    services: Dict[int, Service]
    running_set: Set[int]

    def __init__(self):
        """Initialize the async services handler."""
        self.running_set = Set()
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

        :param List[Service] service: The list of :class:`service.Service` instances
            to add.
        :return List[int]: The id value of each service.
        """
        for service in services:
            key = id(service)
            self.services[key] = service

        return [id(service) for service in services]

    def run_service(self, value: int | Service) -> Task[Any] | None:
        """Starts a service from the handler.

        :param value: The instance :class:`service.Service` or `id()`.
        :type value: int | Service
        :return None:
        """
        service_id = value if isinstance(value, int) else id(value)
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
        """Run all services that were added to the handler using a TaskGroup.

        | This function only executes the services added to the handler that are
        | currently not running.

        :return None:
        """
        async with asyncio.TaskGroup() as tg:
            for service in self.services.values():
                if not service.running:
                    self.__create_task(service, tg)
            logging.info("All services are now running.")
        del tg

    def add_and_run_service(self, service: Service) -> None:
        """Add a service to the handler and immediately run it.

        :param Service service: The :class:`service.Service` instance to add and run.
        :return None:
        """
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
        task = service.run(
            tg=tg,
            done_callback=functools.partial(self.__handle_service_done, service),
        )

        logging.info("Service %s is now running.", service.name)
        self.__mark_service_started(service)
        return task

    def __mark_service_started(self, service: Service) -> None:
        """Mark a service as started.

        :param Service service: The service that has started.
        :return None:
        """
        self.running_set.add(service.id)

    def __handle_service_done(self, service: Service, future: Task[Any]) -> None:
        """Mark a service as stopped.

        :param Service service: The service that has stopped.
        :param Task[Any] future: The Task of the service that is done.
        :return None:
        """
        self.running_set.remove(service.id)

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
        return len(self.running_set)
