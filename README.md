## Table of Contents

- [🔥 Flask Tunnel System (Localhost to Public Port Forwarding)](#-flask-tunnel-system-localhost-to-public-port-forwarding)
- [🧱 Project Structure](#project-structure)
- [💡 How It Works](#️-how-it-works)
- [⚙️ Setup Instructions](#️-setup-instructions)
  - [1. 🔧 Installation](#1-%EF%A3%A9-installation)
  - [2. 🚀 Start Flask App (on the client machine)](#2-%F0%9F%9A%80-start-flask-app-on-the-client-machine)
  - [3. 🌐 Start Tunnel Server (on the public server)](#3-%F0%9F%8C%90-start-tunnel-server-on-the-public-server)
  - [4. 📡 Start Tunnel Client (on the local machine)](#4-%F0%9F%93%9E-start-tunnel-client-on-the-local-machine)
- [✅ Test the Tunnel](#-test-the-tunnel)
- [✅ Notes](#-notes)
- [🙌 Credits](#-credits)
- [🤝 Contributing](#-contributing)

---

# 🔥 Flask Tunnel System (Localhost to Public Port Forwarding)

This project allows you to expose a local **Flask** app (or any local service) running on a private machine to the public via a custom TCP tunnel.

---

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

---

## 💡 How It Works

- The **server** listens on a public machine and waits for clients.
- The **client** connects to the server and creates a tunnel (e.g., public:8080 → local:5000).
- **Flask** runs on the client machine on port 5000.
- Anyone accessing the server’s `:8080` port gets forwarded to the client’s local Flask app.

---

## ⚙️ Setup Instructions

### 1. 🔧 Installation

```bash
git clone [https://github.com/Slozzyondul/Ngrok-like-server.git](https://github.com/Slozzyondul/Ngrok-like-server.git)
cd Ngrok-like-server
pip install -r requirements.txt

