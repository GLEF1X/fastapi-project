#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.
import subprocess

from src.services.utils.other.api_installation import (
    Director,
    DevelopmentApplicationBuilder,
)

director = Director(DevelopmentApplicationBuilder())
app = director.configure()

if __name__ == "__main__":
    director.run()
    # subprocess.run(["gunicorn", "-w 4", "-k uvicorn.workers.UvicornWorker", "main:app"])
 