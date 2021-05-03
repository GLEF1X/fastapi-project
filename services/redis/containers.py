import glQiwiApi
from dependency_injector import containers, providers

from . import redis, services


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


class APIS(containers.DeclarativeContainer):
    config = providers.Configuration()

    qiwi = providers.Factory(
        glQiwiApi.QiwiWrapper,
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
