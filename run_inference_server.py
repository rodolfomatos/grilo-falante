#!/usr/bin/env python3
"""
BitNet Inference Server
Simple HTTP server for bitnet.cpp inference
"""

import argparse
import json
import subprocess
import threading
import queue
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs


class InferenceServer:
    def __init__(self, model_path: str, port: int = 8002, host: str = "0.0.0.0"):
        self.model_path = model_path
        self.port = port
        self.host = host
        self.process = None
        self.request_queue = queue.Queue()
        self.response_queue = queue.Queue()

    def start_process(self):
        cmd = [
            "./build/bin/bitnet-server",
            "-m", self.model_path,
            "-p", str(self.port - 1),
            "-t", "4"
        ]
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/build"
        )

    def stop_process(self):
        if self.process:
            self.process.terminate()
            self.process.wait()


class BitNetHandler(BaseHTTPRequestHandler):
    server: InferenceServer = None

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/v1/completions":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body)
                prompt = data.get("prompt", "")
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                
                response = {
                    "choices": [{"text": "[BitNet placeholder - implement bitnet.cpp integration]"}],
                    "model": "bitnet"
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[BitNet] {args[0]}")


def main():
    parser = argparse.ArgumentParser(description="BitNet Inference Server")
    parser.add_argument("-m", "--model", required=True, help="Path to model file")
    parser.add_argument("--port", type=int, default=8002, help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    server = InferenceServer(args.model, args.port, args.host)
    server.start_process()

    handler = BitNetHandler
    handler.server = server

    httpd = HTTPServer((args.host, args.port), handler)
    print(f"BitNet server starting on {args.host}:{args.port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        server.stop_process()


if __name__ == "__main__":
    main()
