#!/usr/bin/env python3

import argparse
import json
import socket
import ssl
import uuid
from datetime import datetime
from pathlib import Path

import yaml


def load_config(env_name):
    config_path = Path("config") / f"{env_name}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Missing config profile: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def tcp_check(host, port, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "reachable"
    except Exception as e:
        return False, str(e)


def tls_check(host, port, timeout=3):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as tls_sock:
                cert = tls_sock.getpeercert()
                return True, cert.get("subject", "certificate ok")
    except Exception as e:
        return False, str(e)


def write_session_log(config, tcp_result, tls_result):
    log_dir = Path(config["logging"]["local_path"])
    log_dir.mkdir(parents=True, exist_ok=True)

    session_id = (
        f"{config['environment']}-"
        f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-"
        f"{uuid.uuid4().hex[:8]}"
    )

    log_file = log_dir / f"remote-access-session-{session_id}.json"

    payload = {
        "session_id": session_id,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "environment": config["environment"],
        "tunnel_name": config["tunnel"]["name"],
        "gateway": config["tunnel"]["gateway"],
        "port": config["tunnel"]["port"],
        "protocol": config["tunnel"]["protocol"],
        "tcp_check": {
            "ok": tcp_result[0],
            "message": tcp_result[1],
        },
        "tls_check": {
            "ok": tls_result[0],
            "message": str(tls_result[1]),
        },
        "upload_target": config["logging"]["s3_bucket"],
    }

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return log_file, session_id


def main():
    parser = argparse.ArgumentParser(
        description="Remote access tunnel diagnostics agent"
    )
    parser.add_argument("--env", choices=["dev", "prod"], default="dev")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()

    config = load_config(args.env)

    gateway = config["tunnel"]["gateway"]
    port = int(config["tunnel"]["port"])

    print(f"[+] Loading environment profile: {args.env}")
    print(f"[+] Tunnel profile: {config['tunnel']['name']}")
    print(f"[+] Gateway: {gateway}:{port}")
    print("[+] Running TCP reachability check")

    tcp_result = tcp_check(gateway, port)

    print("[+] Running TLS validation check")
    tls_result = tls_check(gateway, port)

    log_file, session_id = write_session_log(config, tcp_result, tls_result)

    print(f"[+] Session ID: {session_id}")
    print(f"[+] Diagnostics log written: {log_file}")

    if config["logging"].get("upload_enabled") and not args.no_upload:
        print(f"[+] Upload target: {config['logging']['s3_bucket']}")
        print("[!] Upload skipped: legacy uploader requires configured AWS profile")
    else:
        print("[+] Upload disabled for this run")

    print("[+] Diagnostics completed")


if __name__ == "__main__":
    main()
