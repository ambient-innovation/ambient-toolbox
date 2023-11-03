SENTRY_EVENT = {
    "level": "error",
    "exception": {
        "values": [
            {
                "module": None,
                "type": "ZeroDivisionError",
                "value": "division by zero",
                "mechanism": {"type": "django", "handled": False},
                "stacktrace": {
                    "frames": [
                        {
                            "filename": "test/account/api/views.py",
                            "abs_path": "/opt/project/backend/test/account/api/views.py",
                            "function": "perform_update",
                            "module": "test.account.api.views",
                            "lineno": 123,
                            "pre_context": ["test = 1/0"],
                            "vars": {
                                "self": "<testapp.account.api.views.TestViewSet object>",
                                "serializer": "TestDetailSerializer(<User: Test AAAA>)",
                                "__class__": "<class 'test.account.api.views.TestViewSet'>",
                                "admin": "<EmailUser: Test User>",
                                "test_data": "123",
                            },
                            "in_app": True,
                        }
                    ]
                },
            }
        ]
    },
    "request": {
        "url": "http://localhost:8000/api/v2/test/17/",
        "query_string": "",
        "method": "PUT",
        "env": {"SERVER_NAME": "cdc3cb5b00af", "SERVER_PORT": "8000", "REMOTE_ADDR": "172.22.0.1"},
        "headers": {
            "Content-Length": "1202",
            "Content-Type": "application/json",
            "Host": "localhost:8000",
            "User-Agent": "Mozilla/5.0 (Macintosh;) Gecko/20100101 Firefox/112.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en",
            "Accept-Encoding": "gzip, deflate, br",
            "Authorization": "Token 123123123123123123123123123123123123abcd",
            "Origin": "http://127.0.0.1:3000",
            "Dnt": "1",
            "Connection": "keep-alive",
            "Referer": "http://127.0.0.1:3000/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        },
        "cookies": {},
        "data": "",
    },
    "user": {"email": "test@test.local", "id": "1337", "ip_address": "172.22.0.1", "username": "test@test.local"},
}

SCRUBBED_SENTRY_EVENT = {
    "level": "error",
    "exception": {
        "values": [
            {
                "module": None,
                "type": "ZeroDivisionError",
                "value": "division by zero",
                "mechanism": {"type": "django", "handled": False},
                "stacktrace": {
                    "frames": [
                        {
                            "filename": "test/account/api/views.py",
                            "abs_path": "/opt/project/backend/test/account/api/views.py",
                            "function": "perform_update",
                            "module": "test.account.api.views",
                            "lineno": 123,
                            "pre_context": ["test = 1/0"],
                            "vars": {
                                "self": "'<testapp.account.api.views.TestViewSet object>'",
                                "serializer": "[Filtered]",  # filtered due to standard filter
                                "__class__": "\"<class 'test.account.api.views.TestViewSet'>\"",
                                "admin": "[Filtered]",  # filtered due to standard filter
                                "test_data": "'123'",
                            },
                            "in_app": True,
                        }
                    ]
                },
            }
        ]
    },
    "request": {
        "url": "http://localhost:8000/api/v2/test/17/",
        "query_string": "",
        "method": "PUT",
        "env": {"SERVER_NAME": "cdc3cb5b00af", "SERVER_PORT": "8000", "REMOTE_ADDR": "172.22.0.1"},
        "headers": {
            "Content-Length": "1202",
            "Content-Type": "application/json",
            "Host": "localhost:8000",
            "User-Agent": "Mozilla/5.0 (Macintosh;) Gecko/20100101 Firefox/112.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en",
            "Accept-Encoding": "gzip, deflate, br",
            "Authorization": "[Filtered]",  # filtered due to default sentry filter
            "Origin": "http://127.0.0.1:3000",
            "Dnt": "1",
            "Connection": "keep-alive",
            "Referer": "http://127.0.0.1:3000/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        },
        "cookies": {},
        "data": "",
    },
    "user": {
        "email": "[Filtered]",  # filtered due to default sentry filter
        "id": "1337",
        "ip_address": "[Filtered]",  # filtered due to default sentry filter
        "username": "[Filtered]",  # filtered due to default sentry filter
    },
    "_meta": {
        "exception": {
            "values": {
                "0": {
                    "stacktrace": {
                        "frames": {
                            "0": {
                                "vars": {
                                    "serializer": {"": {"rem": [["!config", "s"]]}},
                                    "admin": {"": {"rem": [["!config", "s"]]}},
                                }
                            }
                        }
                    }
                }
            }
        },
        "request": {"headers": {"Authorization": {"": {"rem": [["!config", "s"]]}}}},
        "user": {
            "email": {"": {"rem": [["!config", "s"]]}},
            "ip_address": {"": {"rem": [["!config", "s"]]}},
            "username": {"": {"rem": [["!config", "s"]]}},
        },
    },
}
