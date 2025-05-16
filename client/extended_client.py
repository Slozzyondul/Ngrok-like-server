import socket
import threading
import json
from base64 import b64decode, b64encode
from Crypto.Cipher import AES

class TunnelClient:
    def __init__(self, server_ip, server_port, client_id):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_id = client_id
        self.key = None
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_ip, self.server_port))

        self.key = self.socket.recv(1024)
        self.socket.sendall(self.client_id.encode())
        print(f"[+] Connected to server as '{self.client_id}'")

        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            try:
                enc_data = self.socket.recv(4096)
                if not enc_data:
                    print("[!] Server closed connection")
                    break
                    
                data = self.decrypt(enc_data)
                if data is None:
                    continue
                    
                try:
                    command = json.loads(data.decode('utf-8'))
                    if command.get("command") == "forward":
                        self.handle_forward(command["local_port"])
                except json.JSONDecodeError:
                    # Handle raw HTTP traffic
                    self.handle_raw_data(data)
                    
            except ConnectionResetError:
                print("[!] Connection reset by server")
                break
            except Exception as e:
                print(f"[!] Listen error: {e}")
                time.sleep(1)  # Prevent tight loop on errors
    def handle_raw_data(self, data):
        """Handle non-JSON data (like HTTP requests)"""
        try:
            local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            local_sock.connect(('localhost', 5000))
            local_sock.sendall(data)
            
            response = local_sock.recv(4096)
            if response:
                self.socket.sendall(self.encrypt(response))
        except Exception as e:
            print(f"[!] Raw data handling error: {e}")
        finally:
            local_sock.close()

   
    def handle_forward(self, local_port):
        try:
            # Create a new socket for each forwarding connection
            forward_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            forward_sock.connect(('localhost', local_port))
            print(f"[>] Connected to local service on port {local_port}")

            # Create new socket for server communication
            server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_conn.connect((self.server_ip, self.server_port))
            server_conn.sendall(self.client_id.encode())

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
                    try:
                        src.close()
                    except:
                        pass
                    try:
                        dst.close()
                    except:
                        pass

            threading.Thread(target=forward, args=(server_conn, forward_sock), daemon=True).start()
            threading.Thread(target=forward, args=(forward_sock, server_conn), daemon=True).start()

        except Exception as e:
            print(f"[!] Local connect failed: {e}")

    def pipe(self, src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except:
            pass
        finally:
            src.close()
            dst.close()

    def register_tunnel(self, public_port, local_port):
        message = json.dumps({
            "command": "register_tunnel",
            "public_port": public_port,
            "local_port": local_port
        }).encode()
        self.socket.sendall(self.encrypt(message))
        print(f"[+] Requested tunnel: public :{public_port} → local :{local_port}")

    def encrypt(self, message):
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(message)
        return b64encode(cipher.nonce + tag + ciphertext)

  
    def decrypt(self, ciphertext):
        try:
            # Ensure we have bytes
            if isinstance(ciphertext, str):
                ciphertext = ciphertext.encode('utf-8')
            
            # Validate minimum length
            if len(ciphertext) < 24:  # Minimum viable length
                raise ValueError("Ciphertext too short")
            
            # Add padding if needed
            pad_len = len(ciphertext) % 4
            if pad_len:
                ciphertext += b'=' * (4 - pad_len)
            
            try:
                raw = b64decode(ciphertext, validate=True)
            except Exception as e:
                raise ValueError(f"Base64 decode failed: {e}")
            
            if len(raw) < 32:
                raise ValueError("Invalid ciphertext length")
            
            nonce = raw[:16]
            tag = raw[16:32]
            data = raw[32:]
            cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
            return cipher.decrypt_and_verify(data, tag)
        except Exception as e:
            print(f"[!] Decryption warning: {str(e)[:100]}")
            return None

if __name__ == "__main__":
    client = TunnelClient("127.0.0.1", 9000, "client-001")
    client.connect()

    # Create tunnel from server:8080 → client:5000
    client.register_tunnel(8080, 5000)
    
    #flutter testing
    client.register_tunnel(8081, 5001)

    # Keep the main thread alive
    import time
    while True:
        time.sleep(1)
