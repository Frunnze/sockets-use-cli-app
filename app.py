import socket, ssl


def check_command_validity():
    pass


def parse_url():
    pass


host =  "www.example.com"
path = "/"
port = 80

#context = ssl.create_default_context()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client = context.wrap_socket(client, server_hostname=host)
client.connect((host, port))

request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"
client.send(request.encode())
response = client.recv(4096)
client.close()

headers, content = response.split(b"\r\n\r\n", 1)

print(response.decode())

# la img arata linkul