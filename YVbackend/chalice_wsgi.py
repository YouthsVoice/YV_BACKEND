# chalice_deploy/chalice_wsgi.py

from io import BytesIO

class ChaliceWSGIHandler:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, request):
        environ = self.create_environ(request)
        body = BytesIO()
        headers_set = []
        headers_sent = []

        def write(data):
            body.write(data)
            return

        def start_response(status, response_headers, exc_info=None):
            headers_set[:] = [status, response_headers]
            return write

        result = self.wsgi_app(environ, start_response)

        try:
            for data in result:
                if data:
                    write(data)
        finally:
            if hasattr(result, "close"):
                result.close()

        status, response_headers = headers_set
        body.seek(0)
        return {
            "statusCode": int(status.split(" ")[0]),
            "headers": dict(response_headers),
            "body": body.read().decode("utf-8"),
        }

    def create_environ(self, request):
        environ = {
            "REQUEST_METHOD": request.method,
            "SCRIPT_NAME": "",
            "PATH_INFO": "/" + request.context["resourcePath"].lstrip("/"),
            "QUERY_STRING": request.query_params or "",
            "SERVER_NAME": "lambda",
            "SERVER_PORT": "80",
            "SERVER_PROTOCOL": "HTTP/1.1",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "https",
            "wsgi.input": BytesIO(request.raw_body or b""),
            "wsgi.errors": BytesIO(),
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
            "wsgi.run_once": True,
        }

        for header, value in request.headers.items():
            environ[f"HTTP_{header.upper().replace('-', '_')}"] = value

        return environ
