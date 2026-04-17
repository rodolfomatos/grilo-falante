#!/usr/bin/env python3
"""
BitNet Server Launcher

Starts the llama.cpp server with the BitNet model.
"""

import os
import subprocess
import sys

MODEL_PATH = "/app/models/BitNet-b1.58-2B-4T.gguf"
SERVER_BIN = "/app/llama.cpp/build/bin/llama-server"
PORT = 8002

def main():
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model not found at {MODEL_PATH}")
        sys.exit(1)

    if not os.path.exists(SERVER_BIN):
        print(f"[ERROR] Server binary not found at {SERVER_BIN}")
        sys.exit(1)

    cmd = [
        SERVER_BIN,
        "-m", MODEL_PATH,
        "-c", "2048",
        "-t", "4",
        "--host", "0.0.0.0",
        "--port", str(PORT),
        "--log-disable",
    ]

    print(f"[BitNet] Starting server with command:")
    print(f"[BitNet] {' '.join(cmd)}")
    print(f"[BitNet] Model: {MODEL_PATH}")
    print(f"[BitNet] Port: {PORT}")

    os.execv(cmd[0], cmd)

if __name__ == "__main__":
    main()