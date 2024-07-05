from http.server import SimpleHTTPRequestHandler, HTTPServer
import cgi
import os
import json

UPLOAD_DIR = 'uploads'

class MyHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/upload':
            content_type, pdict = cgi.parse_header(self.headers['content-type'])
            if content_type == 'multipart/form-data':
                form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
                uploaded_file = form['file']
                if uploaded_file.filename:
                    if not os.path.exists(UPLOAD_DIR):
                        os.makedirs(UPLOAD_DIR)
                    file_path = os.path.join(UPLOAD_DIR, uploaded_file.filename)
                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.file.read())
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        'success': True,
                        'imageUrl': '/' + file_path.replace('\\', '/')
                    }
                    self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                else:
                    self.send_response(400)
                    self.end_headers()
                    response = {
                        'success': False
                    }
                    self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path.startswith('/uploads/'):
            file_path = '.' + self.path
            if os.path.exists(file_path):
                self.send_response(200)
                if file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                    self.send_header('Content-type', 'image/jpeg')
                elif file_path.endswith('.png'):
                    self.send_header('Content-type', 'image/png')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            super().do_GET()

def run(server_class=HTTPServer, handler_class=MyHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    print('Starting server at http://localhost:8000')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
