from internal.server import flask_app


def start_server():
    flask_app.run(host='0.0.0.0', port = 5001, threaded = True)
    print("After run called")

start_server()