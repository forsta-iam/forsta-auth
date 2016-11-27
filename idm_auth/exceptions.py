import http.client


class ServerError(Exception):
    pass


class ServiceUnavailable(ServerError):
    status_code = http.client.SERVICE_UNAVAILABLE
    template_name = '503.html'
