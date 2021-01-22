import unittest
import request
from app import timezones_app
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
import threading
from datetime import datetime
from pytz import timezone


class TimezoneTest(unittest.TestCase):
    def setUp(self):
        self.port = 8000
        self.url = 'localhost'
        self.server = WSGIServer((self.url, self.port), WSGIRequestHandler)
        self.server.set_app(timezones_app)
        self.t = threading.Thread(target=self.server.serve_forever)
        self.t.start()

    def test_api(self):
        tz_list = ('GMT', 'Europe/Moscow', 'EST')
        for tz in tz_list:
            response = requests.get(f'http://localhost:{self.port}/{tz}')
            dt = datetime.now(timezone(tz))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode('utf-8'), dt.strftime('%m.%d.%Y %H:%M:%S'))
        payload = {
            "first_date": "12.20.2021 22:21:05",
            "first_tz": "GMT",
            "second_date": "12.20.2021 22:21:05",
            "second_tz": "Europe/Moscow"
        }
        response = requests.post(f'http://localhost:{self.port}/api/v1/datediff', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), '9000.0')
        payload = {
            "date": "12.20.2021 22:21:05",
            "tz": "Europe/Moscow",
            "target_tz": "Asia/Tomsk"
            }
        response = requests.post(f'http://localhost:{self.port}/api/v1/convert', json=payload)
        input_dt = datetime.strptime(payload['date'], '%m.%d.%Y %H:%M:%S')
        input_dt_tz = input_dt.replace(tzinfo=timezone(payload['tz']))
        output_dt = input_dt_tz.astimezone(timezone(payload['target_tz']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), output_dt.strftime('%m.%d.%Y %H:%M:%S'))

    def tearDown(self):
        self.server.shutdown()
        self.t.join()


if __name__ == "__main__":
    unittest.main()
