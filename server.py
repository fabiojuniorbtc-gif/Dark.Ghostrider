import http.server
import socketserver
import os
import sys

# Force UTF-8 stdout on Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == '__main__':
    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print("====================================================")
        print("[MOTO] DARK GHOSTRIDER STORE - SERVIDOR LOCAL ATIVO")
        print("====================================================")
        print(f"-> Loja:      http://localhost:{PORT}/index.html")
        print(f"-> Admin:     http://localhost:{PORT}/admin.html")
        print(f"-> Rastreio:  http://localhost:{PORT}/rastreio.html")
        print("====================================================")
        print("Pressione Ctrl+C para encerrar o servidor.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
