from SystemCode.server.backends.sanic_api import app
from sanic import Sanic
from sanic.response import file
import multiprocessing


fe_app = Sanic('Frontend')


@fe_app.route('/')
async def index(request):
    return await file("./SystemCode/server/frontend/templates/login.html")


@fe_app.route('/chat')
async def manage(request):
    return await file("./SystemCode/server/frontend/templates/index.html")

fe_app.static('/static', './SystemCode/server/frontend/static')


def run_be():
    app.run(
        host="0.0.0.0",
        port=18777,
        access_log=False,
        single_process=True
    )


def run_fe():
    fe_app.run(
        host="0.0.0.0",
        port=18776,
        access_log=False,
        single_process=True
    )


if __name__ == '__main__':
    process1 = multiprocessing.Process(target=run_fe)
    process2 = multiprocessing.Process(target=run_be)

    process1.start()
    process2.start()

    process1.join()
    process2.join()





