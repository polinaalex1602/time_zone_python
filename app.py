from wsgiref import simple_server
from datetime import datetime
from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError
import json
import sys
import os


def timezones_app(environ, start_response):
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    status = '200 OK'
    if environ['REQUEST_METHOD'] == 'GET':
        try:
            tz = timezone(environ['PATH_INFO'][1:]) if environ['PATH_INFO'][1:] else timezone('GMT')
            dt = datetime.now(tz)
            start_response(status, headers)
            return [dt.strftime('%m.%d.%Y %H:%M:%S').encode('utf-8')]
        except UnknownTimeZoneError as e:
            status = '400 Bad request'
            start_response(status, headers)
            return [b'UnknownTimeZoneError']
    elif environ['REQUEST_METHOD'] == 'POST':
        request_body_size = int(environ['CONTENT_LENGTH'])
        request_body = environ['wsgi.input'].read(request_body_size)
        json_body = json.loads(request_body.decode("utf-8"))
        if environ['PATH_INFO'] == '/api/v1/convert':
            try:
                status = '200 OK'
                input_dt = datetime.strptime(json_body['date'], '%m.%d.%Y %H:%M:%S')
                input_dt_tz = input_dt.replace(tzinfo=timezone(json_body['tz']))
                output_dt = input_dt_tz.astimezone(timezone(json_body['target_tz']))
                start_response(status, headers)
                return [output_dt.strftime('%m.%d.%Y %H:%M:%S').encode('utf-8')]
            except UnknownTimeZoneError as e:
                status = '400 Bad request'
                start_response(status, headers)
                return [b'UnknownTimeZoneError']
        if environ['PATH_INFO'] == '/api/v1/datediff':
            try:
                status = '200 OK'
                fisrt_dt = datetime.strptime(json_body['first_date'], '%m.%d.%Y %H:%M:%S')
                first_dt = fisrt_dt.replace(tzinfo=timezone(json_body['first_tz']))
                second_dt = datetime.strptime(json_body['second_date'], '%m.%d.%Y %H:%M:%S')
                second_dt = second_dt.replace(tzinfo=timezone(json_body['second_tz']))
                diff = first_dt - second_dt
                response = diff.total_seconds()
                start_response(status, headers)
                return [str(response).encode('utf-8')]
            except UnknownTimeZoneError as e:
                status = '400 Bad request'
                start_response(status, headers)
                return [b'UnknownTimeZoneError']

def start_server(port):
    httpd = simple_server.make_server('', port, timezones_app)
    print("Serving on port 8000...")
    return httpd

if __name__ == '__main__':
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    try:
        httpd = start_server(port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down.")
        httpd.server_close()
