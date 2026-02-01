import bbc_server

host = bbc_server.CONFIG.get("server", "HOST")
port = int(bbc_server.CONFIG.get("server", "PORT").strip() or "0")

server = bbc_server.tcp_server.TcpServer(host, port)
server.start()
