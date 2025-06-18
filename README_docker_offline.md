# 🐳 Docker & Docker Desktop Offline Installation Guide (Ubuntu 24.04)

This guide walks you through installing **Docker Engine** and **Docker Desktop** on an **offline Ubuntu 24.04 machine**, using an online machine to fetch necessary packages.

---

## ✅ Requirements

- Online Ubuntu (or Debian-based) machine with internet access
- Offline Ubuntu 24.04 machine (same architecture)
- USB or LAN for file transfer

---

## 🖥️ PART 1: Download on Online Machine

### 1. Download Docker Engine `.deb` Packages

First, set up the Docker repository:

```bash
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o docker.gpg
sudo install -m 644 docker.gpg /etc/apt/trusted.gpg.d/
echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu noble stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
```

Now, download Docker packages and dependencies **without installing**:

```bash
mkdir docker-debs
cd docker-debs
apt download docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2. Download Docker Desktop `.deb`

From the official Docker website:

```bash
wget https://desktop.docker.com/linux/main/amd64/docker-desktop-<version>-amd64.deb
```

Replace `<version>` with the latest version (e.g., `4.30.0`).

---

## 📦 PART 2: Transfer Files

Transfer the following to the offline machine using USB:

- Entire `docker-debs/` directory
- `docker-desktop-<version>-amd64.deb` file

---

## 💻 PART 3: Install on Offline Machine

### 1. Install Docker Engine

On the offline machine:

```bash
cd docker-debs
sudo dpkg -i *.deb
```

Fix missing dependencies if needed:

```bash
sudo apt install -f
```

### 2. Install Docker Desktop

```bash
sudo apt install ./docker-desktop-<version>-amd64.deb
```

After install:

```bash
systemctl --user start docker-desktop
```

You can also enable it to start on login:

```bash
systemctl --user enable docker-desktop
```

---

## 🧪 Verify Installation

```bash
docker --version
docker info
docker run hello-world
```

---

## 🧰 Common Troubleshooting

### ❌ `docker: command not found`

Make sure `/usr/bin/docker` exists and your shell recognizes it. Try:

```bash
export PATH=$PATH:/usr/bin
```

### ❌ `Cannot connect to the Docker daemon`

Ensure the Docker service is running:

```bash
sudo systemctl start docker
```

Add your user to the `docker` group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### ❌ Docker Desktop doesn't launch (GUI)

Check logs:

```bash
journalctl --user-unit docker-desktop
```

Ensure you have required dependencies like X11 and systemd for user services.

---

## 📦 Notes

- Docker packages may change with Ubuntu versions. Make sure to match `noble` (24.04) vs `jammy` (22.04) in your sources.
- Docker Desktop on Linux requires systemd, X11, and kernel >= 5.15.

---

## 🧠 Resources

- [Docker Engine Documentation](https://docs.docker.com/engine/)
- [Docker Desktop for Linux](https://docs.docker.com/desktop/install/linux-install/)
