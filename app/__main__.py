import argparse

import uvicorn

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost", help="The host to bind to.")
parser.add_argument("--port", default="8000", type=int, help="The port to run the server on.")
parser.add_argument("--reload", action="store_true", default=False, help="Reload on file changes")
args = parser.parse_args()
uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)
