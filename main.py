#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from services.utils.other.api_installation import (
    Director,
    ApplicationConfiguratorBuilder,
)

director = Director(ApplicationConfiguratorBuilder())
app = director.configure()

if __name__ == "__main__":
    director.run(debug=True, port=5000, log_level="info")
