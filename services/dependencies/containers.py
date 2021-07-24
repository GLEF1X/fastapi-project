from dependency_injector import containers, providers
from glQiwiApi import QiwiWrapper

from . import redis, services
from ..database.models.base import DatabaseComponents
from ..database.repositories.product import ProductRepository
from ..database.repositories.user import UserRepository


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    redis_pool = providers.Resource(
        redis.init_redis_pool,
        host=config.REDIS_HOST,
        password=config.REDIS_PASSWORD,
    )

    redis_ = providers.Factory(
        services.RedisService,
        redis=redis_pool,
    )

    db = providers.Singleton(
        DatabaseComponents,
        drivername="postgresql+asyncpg",
        username=config.DB_USER,
        password=config.DB_PASS,
        host=config.DB_HOST,
        database=config.DB_NAME,
    )

    user_repository: providers.Provider[UserRepository] = providers.Factory(
        UserRepository, session_or_pool=db.provided.sessionmaker
    )

    product_repository: providers.Provider[ProductRepository] = providers.Factory(
        ProductRepository, session_or_pool=db.provided.sessionmaker
    )


class APIS(containers.DeclarativeContainer):
    config = providers.Configuration()

    qiwi: providers.Provider[QiwiWrapper] = providers.Factory(
        QiwiWrapper,
        api_access_token=config.QIWI_TOKEN,
        secret_p2p=config.QIWI_SECRET,
        phone_number=config.PHONE_NUMBER,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    apis = providers.Container(APIS, config=config.apis)
    services = providers.Container(Services, config=config.services)
