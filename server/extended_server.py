

import socket
import threading
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

def encrypt_message(message, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return b64encode(cipher.nonce + tag + ciphertext)


def decrypt_message(ciphertext, key):
    try:
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode()
            
        # Base64 requires length % 4 == 0
        pad_len = len(ciphertext) % 4
        if pad_len:
            ciphertext += b'=' * (4 - pad_len)
            
        raw = b64decode(ciphertext)
        if len(raw) < 32:
            raise ValueError("Invalid ciphertext")
            
        nonce = raw[:16]
        tag = raw[16:32]
        message = raw[32:]
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(message, tag)
    except Exception as e:
        print(f"[!] Decryption failed: {str(e)[:50]}")
        return b'{}'  # Prevent JSON parsing errors

class TunnelServer:
    def __init__(self, host='0.0.0.0', port=9000):
        self.server_host = host
        self.server_port = port
        self.clients = {}        # client_id -> socket
        self.tunnels = {}        # public_port -> (client_id, local_port)
        self.keys = {}           # client_id -> AES key

    def start(self):
        print(f"[+] Tunnel Server listening on {self.server_port}")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.server_host, self.server_port))
        server.listen(5)

        while True:
            client_sock, addr = server.accept()
            threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()

    
    def handle_client(self, client_socket):
        try:
            key = get_random_bytes(16)
            client_socket.sendall(key)
            data = client_socket.recv(4096)
            if not data:
                return  # Client disconnected
            client_id = data.decode().strip()
            self.clients[client_id] = client_socket
            self.keys[client_id] = key
            print(f"[+] Client registered: {client_id}")

            while True:
                enc_data = client_socket.recv(4096)
                if not enc_data:
                    break  # Client disconnected
                try:
                    data = decrypt_message(enc_data, key)
                    if not data:  # Decryption failed
                        continue
                    command = json.loads(data)
                    if command["command"] == "register_tunnel":
                        public_port = command["public_port"]
                        local_port = command["local_port"]
                        self.tunnels[public_port] = (client_id, local_port)
                        threading.Thread(target=self.start_forwarding, args=(public_port, client_id, local_port), daemon=True).start()
                        print(f"[+] Tunnel registered: :{public_port} → {client_id}:{local_port}")
                except Exception as e:
                    print(f"[!] Error handling command: {e}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
            client_socket.close()

    def start_forwarding(self, public_port, client_id, local_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(('0.0.0.0', public_port))
            listener.listen(5)
            print(f"[+] Listening on public port {public_port} for {client_id}:{local_port}")

            while True:
                public_sock, addr = listener.accept()
                print(f"[>] Connection on port {public_port} from {addr}")
                threading.Thread(target=self.handle_forward_connection, args=(public_sock, client_id, local_port), daemon=True).start()

   
    def handle_forward_connection(self, public_socket, client_id, local_port):
        if client_id not in self.clients:
            print(f"[!] Client {client_id} not available")
            public_socket.close()
            return

        try:
            client_sock = self.clients[client_id]
            key = self.keys[client_id]
            
            # Verify socket is still connected
            try:
                client_sock.getpeername()
            except socket.error:
                print(f"[!] Client socket {client_id} is closed")
                del self.clients[client_id]
                public_socket.close()
                return

            command = json.dumps({
                "command": "forward",
                "local_port": local_port
            }).encode()

            encrypted_cmd = encrypt_message(command, key)
            client_sock.sendall(encrypted_cmd)

            # Create new socket for forwarding
            forward_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            forward_sock.connect(('localhost', local_port))

            def forward(src, dst):
                try:
                    while True:
                        data = src.recv(4096)
                        if not data:
                            break
                        dst.sendall(data)
                except Exception as e:
                    print(f"[>] Forwarding error: {e}")
                finally:
                    src.close()
                    dst.close()

            threading.Thread(target=forward, args=(public_socket, forward_sock)).start()
            threading.Thread(target=forward, args=(forward_sock, public_socket)).start()

        except Exception as e:
            print(f"[!] Forwarding setup failed: {e}")
            public_socket.close()
            # Pipe data bidirectionally
        def forward(src, dst):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.sendall(data)
            except Exception as e:
                print(f"[!] Forward error: {e}")
            finally:
                src.close()
                dst.close()

        threading.Thread(target=forward, args=(public_socket, client_sock), daemon=True).start()
        threading.Thread(target=forward, args=(client_sock, public_socket), daemon=True).start()


if __name__ == "__main__":
    TunnelServer().start()
