import durak_server

host = durak_server.CONFIG.get("server", "HOST")
port = int(durak_server.CONFIG.get("server", "PORT").strip() or "0")

server = durak_server.tcp_server.TcpServer(host, port)
server.start()
