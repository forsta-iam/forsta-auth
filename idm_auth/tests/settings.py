from ..settings import *

BROKER_TRANSPORT = 'memory'

AUTHENTICATION_BACKENDS += ('idm_auth.tests.social_backend.DummyBackend',)

SOCIAL_AUTH_SAML_SP_PRIVATE_KEY = """\
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCkR4S26dW8j+yO
fxLFjdeUQbzL+QerKXkmQUiF8U9kvxAudt/aqvHFJ+gIo7/N5QuG/C1ptmT9NhB8
jLS6qyRiQzS0MHtPjmXO3m+ukR/VHxuoowxbqBYCjnytUg2BUX91hWTKqzKXKV31
Yfds7uGE9oQ3E3wGCCTOs9/1fnRVAmzq4gMCLAGH3b0Wjg3/Nijl4MaXwYqLElcb
zbo30RkdY2xdH2ZeTGEKotHx60ZCJF3ypYy2LNYBXMqIudMPA5v0VO5lhKGjJI0Y
fgQq06vrABlM866UCn6qxMvIoFjav0D+GRdEsSa2PDibjukA2fJFvC71XS9cz/Il
K6FyXnS/AgMBAAECggEACWZmO6kpp758hLLUuiUhnsQcL3eybqLS4dN+eNuT9WnR
XTdEG9kIOIXOCyCDix5+CF1Jo/Dh2nNLgjTy6nN8g3rg+yaDB8xYGvwzW8PGFIXR
KVcbD+uQRtksXSaCy1GEf48Ac3BUVr3xOGdApyUMFnWcnyIoSJgSsxkryXpQ4cRI
QcuJY3iz19I2aobseUjik6HKM7qhJIt1H1UAQqVp0KieMrBVqJd0BjmLcf/YlZRH
UPw8sgW6R1BNsZWLJHd2ZzpVkPiX6Op/kHtsY6QvJmTQcG2enuqJr1l9Oc0PGS+r
+zrmiCSVMAT5eea9WJbbER/9jxtcLpIVNwM6SPfXEQKBgQDY14UbvvrYbDMRoWpZ
UJHwKgBluXCZQYA1Rol+mu4njzUn3JO/gLm4+fqCQazQ+p9fBAM75b9hwD24XPTq
jqgcBLlhPLJEzDCDLvvAYpLIJM8KHlgk1uH31lYY32raHWt/2sYtcOsFQE2IQWlC
bS6hpgFbCBl6ToIup9N36QDOfQKBgQDB8hAXQN1gO1avgMo1SEkG3SpkCqH721jy
ieRHGxDJi9SBt2VDIglmAUI09YPG9y3TkJfTDJwgwuzCCJh8OtIWfC/Fu0+j3tgn
Mytevj9Vd40GodZy5rjNJvR2VrBzQQd9OCc9LYlrSLqRTJ2UDdpOTd/IHCtQ+067
589nX3EI6wKBgAjfuQjLpgRZWTWtf2asT2yeq2l+T0dWUOLdQh82Q+zGhYxeEIXT
xMX3JPNTsLjUqNUAmwlGe7CKZ3w2Aaffsq2C2/tIuprqKEoWECNtZUhfiUGGwGCx
konL8bYO3paSgaW31EhjyJpsaT/cPWyEf1YKLyAEktZYhCdYouTTWj8ZAoGBAJ+q
KQcLtnQfxbiMPWvqC3ykHN7pRfty0+IwFQdYx9Q00ojLs4i1/6jDRn8U1By7pzVx
5xuvWOU7s+/1ZZt4TTaHnEibcPAGaEq1PHIuCzPQTQB1wXcsbF0wQbcenPr1QTYc
QWmDEIuK/1TZDy0wzlUClUVHs31itqnJKB0BHKxrAoGADuM2aR0DTMu95qyObKhM
tuP1OmHX/9AYD/Pqs3iA2cfbqB28XmqXBIW73d+NTrQtWWH9jaghyqYIH9Y1Gfv4
sgGX3Be+bUNvcOjMGe43S+p/0aUNP4lw2W99PXZBV0rCXEf/ToyyqHLkb/lAXiv8
vzMKXId6qCc6Xd5ccVGFpvw=
-----END PRIVATE KEY-----
"""


SOCIAL_AUTH_SAML_SP_PUBLIC_CERT = """\
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJALZeoXvHPXTjMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkdCMQ8wDQYDVQQHDAZPeGZvcmQxETAPBgNVBAoMCEFjbWUgT3JnMRIwEAYD
VQQDDAlsb2NhbGhvc3QwHhcNMTcwNDE2MTUwNTAzWhcNMjcwNDE2MTUwNTAzWjBF
MQswCQYDVQQGEwJHQjEPMA0GA1UEBwwGT3hmb3JkMREwDwYDVQQKDAhBY21lIE9y
ZzESMBAGA1UEAwwJbG9jYWxob3N0MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEApEeEtunVvI/sjn8SxY3XlEG8y/kHqyl5JkFIhfFPZL8QLnbf2qrxxSfo
CKO/zeULhvwtabZk/TYQfIy0uqskYkM0tDB7T45lzt5vrpEf1R8bqKMMW6gWAo58
rVINgVF/dYVkyqsylyld9WH3bO7hhPaENxN8BggkzrPf9X50VQJs6uIDAiwBh929
Fo4N/zYo5eDGl8GKixJXG826N9EZHWNsXR9mXkxhCqLR8etGQiRd8qWMtizWAVzK
iLnTDwOb9FTuZYShoySNGH4EKtOr6wAZTPOulAp+qsTLyKBY2r9A/hkXRLEmtjw4
m47pANnyRbwu9V0vXM/yJSuhcl50vwIDAQABo1AwTjAdBgNVHQ4EFgQU+x0bDoRy
JapiI34OxCoIxv3Lt+0wHwYDVR0jBBgwFoAU+x0bDoRyJapiI34OxCoIxv3Lt+0w
DAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEADc+DT1jprMWBmuyatGhd
ZMAMc1oJGz/ZAZUkguNXaAufUf0hY8POlv7g8Mi13IY+au5Gv8UWGBd98dTXR0vr
QAe3v9qVzSsUhW5N0mhenI9Int3y8J+6d3dXKkrZ4Ihk/KqCqzXdoy3bs7bjDvvE
kHtVVoCgKJLZRqRye2xL7isvPG+kIP3alNRXz7gglq6Frn+rw8to3raa8vRPFQS7
HFWfKkrflAfLvoU9s9CePth4W7zFNF8IF/jOFvw45gzWUCx5UyhuMV3P5JLpQv1T
6IKyICbfpvICiyBx61o6KvvTsbcuPOKFGh/Lkku48cJKp4BaClKB8MMZKQXtoU5y
Gw==
-----END CERTIFICATE-----
"""

SOCIAL_AUTH_SAML_SP_ENTITY_ID = 'http://localhost/'
