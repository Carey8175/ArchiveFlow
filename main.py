from SystemCode.server.backends.sanic_api import app


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=18777,
        access_log=False,
        single_process=True
    )
