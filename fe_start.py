from sanic import Sanic
from sanic.response import file


fe_app = Sanic('Frontend')


@fe_app.route('/')
async def index(request):
    return await file("./SystemCode/server/frontend/templates/login.html")


@fe_app.route('/chat')
async def manage(request):
    return await file("./SystemCode/server/frontend/templates/index.html")

fe_app.static('/static', './SystemCode/server/frontend/static')


if __name__ == '__main__':
    fe_app.run(
        host="0.0.0.0",
        port=18776,
        access_log=False,
        workers=3
    )





