from services.utils.api_installation import (
    Configurator,
    APIApplicationBuilder
)

builder = APIApplicationBuilder()
configurator = Configurator(builder)
app = configurator.configure()

if __name__ == '__main__':
    configurator.run_application()
