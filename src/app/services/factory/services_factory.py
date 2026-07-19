from app.services.category.category_service import CategoryService
from app.services.health.health_check_service import HealthCheckService
from app.storage.rds.clients.database_manager import DATA_BASE_MANAGER
from app.storage.rds.datastore.category.category_store import CategoryStore
from app.storage.rds.datastore.health.health_check_provider import HealthCheckProvider


class WikiManagerServices:
    def __init__(
        self,
        health_check_service: HealthCheckService,
        category_service: CategoryService,
    ):
        self._health_check_service = health_check_service
        self._category_service = category_service

    @property
    def health_check_service(self) -> HealthCheckService:
        return self._health_check_service

    @property
    def category_service(self) -> CategoryService:
        return self._category_service


class ServicesFactory:
    def __init__(self, provider: WikiManagerServices):
        self._provider = provider

    def __call__(self) -> WikiManagerServices:
        return self._provider


HEALTH_CHECK_PROVIDER = HealthCheckProvider(DATA_BASE_MANAGER)
CATEGORY_STORE = CategoryStore(DATA_BASE_MANAGER)

HEALTH_CHECK_SERVICE = HealthCheckService(HEALTH_CHECK_PROVIDER)
CATEGORY_SERVICE = CategoryService(CATEGORY_STORE)

WIKI_MANAGER_SERVICES = WikiManagerServices(
    health_check_service=HEALTH_CHECK_SERVICE,
    category_service=CATEGORY_SERVICE,
)

WIKI_MANAGER_FACTORY = ServicesFactory(WIKI_MANAGER_SERVICES)
