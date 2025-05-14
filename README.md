# Ngrok-like-server
Built for devs who need self-hosted ngrok-like power with 🔒 no middlemen.  

# 🔥 Flask Tunnel System (Localhost to Public Port Forwarding)

This project allows you to expose a local Flask app (or any local service) running on a private machine to the public via a custom TCP tunnel.

## 🧱 Project Structure


├── client/

│ └── extended_client.py

├── server/

│ └── extended_server.py

├── utils/

│ └──  utils.py

├── app.py
 
├── requirements.txt

└── README.md


## 💡 How It Works

- The **server** listens on a public machine and waits for clients.
- The **client** connects to the server and creates a tunnel (e.g., public:8080 → local:5000).
- Flask runs on the client machine on port 5000.
- Anyone accessing the server’s `:8080` port gets forwarded to the client’s local Flask app.

## ⚙️ Setup Instructions



### 1. 🔧 Installation

```bash

git clone https://github.com/Slozzyondul/Ngrok-like-server.git

cd Ngrok-like-server

pip install -r requirements.txt

### 2. 🚀 Start Flask App (on the client machine)


FLASK_APP=app.py flask run --port=5000

- Make sure Flask is running before you start the tunnel client.

### 3. 🌐 Start Tunnel Server (on the public server)

cd server

python extended_server.py

- This will listen on port 9000 for clients and forward connections from port 8080.

### 4. 📡 Start Tunnel Client (on the local machine)

cd client

python extended_client.py

- The client registers with the server, and sets up a tunnel from public:8080 → local:5000.

###  ✅ Test the Tunnel

- On the public server or any device with access to it:

curl http://localhost:8080

- You should see the response from the Flask app ("🔥 Tunnel is working!").

### ✅ Notes

- This is for development or demo use, not production.

- Make sure firewall/ports (9000 and 8080) are open on the server.

Uses AES-256 in EAX mode for authenticated encryption

Each session generates unique encryption keys

For production use:

Add client authentication

Implement rate limiting

Use TLS for control channel

### 🙌 Credits
- Inspired by how Ngrok works — built from scratch with Python sockets and threads for devs who want full control.

### 🤝 Contributing
Pull requests welcome! Please:

Fork the repository

Create a feature branch

Submit a PR with clear documentation