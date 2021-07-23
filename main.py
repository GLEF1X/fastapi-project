from services.utils.other.api_installation import Director, ApplicationConfiguratorBuilder

director = Director(ApplicationConfiguratorBuilder())

if __name__ == '__main__':
    director.configure()
    director.run(debug=True, port=5000, log_level="info")
