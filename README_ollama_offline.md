# 🧠 Ollama Offline Installation Guide (Linux)

This guide helps you install and run Ollama **completely offline** on a Linux system (e.g., Ubuntu 22.04/24.04). It includes steps to:

- Download the Ollama binary
- Download models (e.g., Mistral)
- Transfer everything to an offline machine
- Run Ollama fully offline

---

## ✅ Requirements

- An online Linux machine
- An offline Linux machine (same architecture, e.g., x86_64)
- USB drive or local network to transfer files

---

## 🖥️ Part 1: Prepare on an Online Machine

### 1. Download Ollama Binary

```bash
wget https://ollama.com/download/Ollama-linux-amd64 -O ollama
chmod +x ollama
```

### 2. (Optional) Download a Model (e.g., Mistral)

Run the model once to ensure it's downloaded:

```bash
./ollama run mistral
```

This will download the Mistral model to `~/.ollama/models`.

### 3. Package Ollama and Models

```bash
mkdir ollama-offline
mv ollama ollama-offline/
cp -r ~/.ollama/models ollama-offline/
```

Transfer the `ollama-offline` folder to the offline machine using a USB drive or any file transfer method.

---

## 💻 Part 2: Install on the Offline Machine

### 4. Move Files into Place

```bash
mkdir -p ~/.ollama
cp -r ollama-offline/models ~/.ollama/
sudo cp ollama-offline/ollama /usr/local/bin/
chmod +x /usr/local/bin/ollama
```

### 5. Start Ollama

Start the Ollama server in the background:

```bash
ollama serve &
```

### 6. Run the Model Offline

```bash
ollama run mistral
```

If the model was downloaded correctly, it will run offline with no internet access.

---

## ✅ Verify Installation

```bash
ollama list         # Should show mistral or your chosen model
ollama run mistral  # Should open a prompt
```

---

## 📦 Notes

- All models are stored in `~/.ollama/models`
- You can preload other models (e.g., llama2, gemma) using the same steps on the online machine.
- Works on any modern Linux distro (Ubuntu 22.04, 24.04, etc.)

---

## 🧰 Troubleshooting

- **Model not found?** Ensure you copied the full `~/.ollama/models` directory from the online machine.
- **Permission denied?** Ensure the `ollama` binary is executable and installed in your `PATH`.

---

## 🧠 Credits

- [Ollama Documentation](https://ollama.com)
