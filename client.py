import socket
import sys

# 플랫폼별 단일 키 입력 처리
if sys.platform == 'win32':
    import msvcrt
    def get_char():
        return msvcrt.getwch()  # Windows: 엔터 없이 즉시 키 읽기
else:
    import tty, termios
    def get_char():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)  
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '10.150.149.249'
port = 12343

client_socket.connect((host, port))
print("Connected to server")
print("(키를 누르면 즉시 전송됩니다. 'q'를 누르면 종료)")

while True:
    ch = get_char()          # 엔터 없이 즉시 키 캡처
    print(f"Sent: {ch}")     # 어떤 키를 눌렀는지 표시

    client_socket.send(ch.encode())

    response = client_socket.recv(1024)
    respData = response.decode()
    print('Echo:: ', respData)

    if ch == 'q':
        break

client_socket.sendall('q'.encode())
client_socket.close()
print("Disconnected from server")