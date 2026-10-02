"""Small local static server that mirrors a GitHub Pages project prefix."""
import functools
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import threading


def start_server(root,base_url='/'):
    prefix='/' + base_url.strip('/') if base_url.strip('/') else ''
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if prefix and self.path.startswith(prefix+'/'):
                self.path=self.path[len(prefix):]
            super().do_GET()
        def log_message(self,*args):
            pass
    server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(Path(root).resolve())))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    return server,f'http://127.0.0.1:{server.server_port}{prefix}'
