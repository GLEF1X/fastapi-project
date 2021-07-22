from core.config import settings
from services.utils.api_installation import (
    Director,
    ApplicationConfiguratorBuilder
)

director = Director(
    ApplicationConfiguratorBuilder(),
    templates_dir=settings.TEMPLATES_DIR
)

app = director.configure()

if __name__ == '__main__':
    director.run()
