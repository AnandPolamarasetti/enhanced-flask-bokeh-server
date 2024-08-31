import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

import flask
from flask import redirect, send_from_directory
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from bokeh.util.tornado import fixup_windows_event_loop_policy

# Configuration Constants
HOST = "localhost"
PORT = 5009
VISIT_URL = f"http://{HOST}:{PORT}/en/latest/index.html"
SPHINX_TOP = Path(__file__).resolve().parent

# Flask Application Setup
app = flask.Flask(__name__, static_folder="/unused")

@app.route("/")
def root() -> flask.Response:
    return redirect("en/latest/index.html")

@app.route("/en/switcher.json")
def switcher() -> flask.Response:
    return send_from_directory(SPHINX_TOP, "switcher.json")

@app.route("/en/latest/<path:filename>")
def docs(filename: str) -> flask.Response:
    return send_from_directory(SPHINX_TOP / "build" / "html", filename)

def open_browser() -> None:
    try:
        webbrowser.open(VISIT_URL, new=2)
    except Exception as e:
        print(f"Error opening browser: {e}")

def serve_http() -> None:
    global IOLOOP
    IOLOOP = IOLoop().current()
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(PORT)
    IOLOOP.start()

if __name__ == "__main__":
    fixup_windows_event_loop_policy()

    print(f"\nStarting server on port {PORT}...")
    print(f"Visit {VISIT_URL} to see documentation\n")

    try:
        # Start HTTP server
        server_thread = threading.Thread(target=serve_http)
        server_thread.start()

        # Allow server to initialize before opening the browser
        time.sleep(1)

        # Open browser
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.start()

        # Wait for user input to exit
        input("Press <ENTER> to exit...\n")  # lgtm [py/use-of-input]
    except KeyboardInterrupt:
        print("Server interrupted.")
    finally:
        if IOLOOP:
            IOLOOP.add_callback(IOLOOP.stop)  # type: ignore
        server_thread.join()
        browser_thread.join()
        print("Server shut down.")
