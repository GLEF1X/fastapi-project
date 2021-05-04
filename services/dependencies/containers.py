from glQiwiApi import QiwiWrapper
from dependency_injector import containers, providers

from . import redis, services
from ..db.base import Database
from ..db.crud import UserRepository, ProductRepository


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
        Database
    )

    user_repository = providers.Factory(
        UserRepository,
        session_factory=db.provided.session
    )

    product_repository = providers.Factory(
        ProductRepository,
        session_factory=db.provided.session
    )


class APIS(containers.DeclarativeContainer):
    config = providers.Configuration()

    qiwi = providers.Factory(
        QiwiWrapper,
        api_access_token=config.QIWI_TOKEN,
        secret_p2p=config.QIWI_SECRET
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    apis = providers.Container(
        APIS,
        config=config.apis
    )
    services = providers.Container(
        Services,
        config=config.services
    )
