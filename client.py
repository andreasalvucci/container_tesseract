
import socket 
import tqdm


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1",1312))
print("Connesso col server")
file = open("image.jpg","rb")

image_data = file.read(2048)


while image_data:
    client.send(image_data)
    image_data = file.read(2048)

client.shutdown(socket.SHUT_WR)

print("Ora aspetto la risposta del server")

result_text = ""

temp = client.recv(1024).decode()
result_text+=temp

while temp:
    temp = client.recv(1024).decode()
    result_text+=temp

print(result_text)
client.close()
file.close()
