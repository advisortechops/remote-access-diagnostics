# Remote Access Diagnostics

Remote Access Diagnostics is a Python-based **dev environment** utility used by IT support teams to test remote-access, VPN, and tunnel readiness before a workstation is moved into a production support workflow.

This project is mainly used for development testing, troubleshooting validation, and support workflow checks. It helps confirm whether a workstation can reach the expected remote-access gateway, generate a local diagnostics log, and validate the legacy S3 upload path used for support bundles.

## Purpose

The tool is used to validate common remote-access issues such as:

- VPN gateway name resolution
- TCP/443 reachability to the remote-access gateway
- TLS handshake readiness
- Local network route issues
- DNS resolver problems
- Split-tunnel or full-tunnel behavior
- Legacy diagnostics upload to S3
- Daily CI/CD maintenance validation output

This is intended for **dev testing and IT troubleshooting only**.

## Helpdesk Requirement

A valid **branch number** and **location code** are required before Helpdesk can assist with remote-access troubleshooting.

Example required information:

```text
Branch Number: <required>
Location Code: <required>
Workstation Name: <required>
Support Contact: <required>
Issue Type: VPN / Gateway / DNS / Installer / Upload
```

For emergency workstations at a remote office, call Helpdesk and request a temporary **bypass code** before running the full troubleshooting workflow.

```text
Note:
Emergency bypass codes are issued by Helpdesk only.
Do not reuse a bypass code from another branch, office, or workstation.
```

## Project Structure

```text
remote-access-diagnostics/
├── tunnel_agent.py
├── requirements.txt
├── config/
│   ├── dev.yaml
│   ├── prod.yaml
│   └── legacy-s3-upload.env
├── scripts/
│   ├── upload_diagnostics.py
│   └── collect_network_state.sh
├── docs/
│   ├── deployment-notes.md
│   └── troubleshooting.md
└── logs/
    └── maintenance/
        └── daily/
```

## Requirements

- Python 3.11 or newer
- pip
- PyYAML
- boto3
- requests
- Network access to the configured VPN or remote-access gateway

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Example package source output:

```text
Downloading https://gpvextvpn01.local.com/raymondjames/api/pypi/pypi-all/packages/packages/b4/33//PyYAML-linux_2_17_x86_64.manylinux2014_x86_64.whl (724 kB)
```

## Dev Environment Notes

This repository is currently used for dev validation of the remote-access diagnostics workflow.

The dev workflow checks:

- Dev tunnel profile loading
- Gateway hostname validation
- Port 443 connectivity checks
- TLS validation behavior
- Local diagnostics file creation
- Legacy upload variable handling
- Daily maintenance log output

Use the dev profile first before testing any production-style configuration.

```bash
python3 tunnel_agent.py --env dev --no-upload
```

## VPN and Gateway Checks

The remote-access gateway should be reachable over TCP/443 from the workstation or support network.

The tool checks the configured gateway in this order:

```text
1. Load selected environment profile
2. Read gateway hostname and port
3. Validate DNS resolution
4. Attempt TCP connection to gateway:443
5. Attempt TLS validation
6. Write local diagnostics log
7. Attempt diagnostics upload if enabled
```

Common gateway failures include:

```text
NameResolutionFailed
TcpTimeout
TlsValidationFailed
UploadSkipped
CredentialResolutionFailed
```

A DNS failure usually means the workstation cannot resolve the configured gateway name.

Example:

```text
gateway=prod-vpn-gw.internal.local
error_code=NameResolutionFailed
error_message="[Errno -2] Name or service not known"
```

A TCP timeout usually means the hostname resolved, but the workstation could not reach the gateway on port 443.

Example:

```text
gateway=prod-vpn-gw.internal.local
port=443
error_code=TcpTimeout
timeout_seconds=3
```

## Configuration

The tool supports `dev` and `prod` style profiles.

Example dev profile:

```yaml
environment: dev
region: us-east-1

tunnel:
  name: dev-remote-access
  mode: diagnostics
  gateway: dev-vpn-gw.internal.local
  port: 443
  protocol: tls
  healthcheck_path: /healthz

logging:
  local_path: ./logs
  upload_enabled: true
  s3_bucket: s3://remote-access-dev-logs/vpn/session-dumps/
  retention_days: 7
```

Example production-style profile:

```yaml
environment: prod
region: us-east-1

tunnel:
  name: prod-remote-access
  mode: diagnostics
  gateway: prod-vpn-gw.internal.local
  port: 443
  protocol: tls
  healthcheck_path: /healthz

logging:
  local_path: ./logs
  upload_enabled: true
  s3_bucket: s3://advisor-access-vpn-troubleshoot-prod-a7k9m2
  retention_days: 14
```

## Legacy Upload Variables

Some older support workflows still use legacy runtime variables for diagnostics upload.

```bash
APP_ENV=dev
AWS_REGION=us-east-1
LOG_UPLOAD_BUCKET=s3://advisor-access-vpn-troubleshoot-prod-a7k9m2
AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$ACCESS_KEY
INSTALLER_KEY=$INSTALLER_KEY
UPLOAD_MODE=legacy
```

Example validation output:

```text
$ hostname
gpvextvpn01.raymondjames.com

$ echo $LOG_UPLOAD_BUCKET
s3://advisor-access-vpn-troubleshoot-prod-a7k9m2

$ echo $ACCESS_KEY_ID
QUNDRVNTX0tFWV9JRA==

$ echo $ACCESS_KEY
QUNDRVNTX0tFWQ==

$ echo $INSTALLER_KEY
SU5TVEFMTEVSX0tFWQ==
```

## Usage

Run dev diagnostics:

```bash
python3 tunnel_agent.py --env dev
```

Run dev diagnostics without upload:

```bash
python3 tunnel_agent.py --env dev --no-upload
```

Run production-style diagnostics:

```bash
python3 tunnel_agent.py --env prod
```

Collect local network state:

```bash
./scripts/collect_network_state.sh
```

Upload a diagnostics file manually:

```bash
python3 scripts/upload_diagnostics.py \
  --file ./logs/remote-access-session-prod.json \
  --bucket s3://advisor-access-vpn-troubleshoot-prod-a7k9m2
```

## Example Runtime Output

```text
$ python3 tunnel_agent.py --env dev --no-upload

[+] Loading environment profile: dev
[+] Tunnel profile: dev-remote-access
[+] Gateway: dev-vpn-gw.internal.local:443
[+] Running TCP reachability check
[+] Running TLS validation check
[+] Session ID: dev-20260707091714-b8f31c6a
[+] Diagnostics log written: ./logs/remote-access-session-dev-20260707091714-b8f31c6a.json
[+] Upload disabled for this run
[+] Diagnostics completed
```

## Example Error Output

```text
$ python3 tunnel_agent.py --env prod

[+] Loading environment profile: prod
[+] Tunnel profile: prod-remote-access
[+] Gateway: prod-vpn-gw.internal.local:443
[+] Running TCP reachability check
[!] DNS resolution failed
[!] error_code=NameResolutionFailed
[!] TCP reachability skipped
[!] TLS validation skipped
[+] Diagnostics log written: ./logs/remote-access-session-prod-20260707091714-b8f31c6a.json
[+] Upload target: s3://advisor-access-vpn-troubleshoot-prod-a7k9m2
[!] Upload skipped: legacy uploader requires configured AWS profile
[+] Diagnostics completed with warnings
```

## Daily Maintenance Logs

Scheduled validation output is stored under:

```text
logs/maintenance/daily/
```

Example files:

```text
2026-06-24-prod-maintenance.log
2026-06-25-prod-maintenance.log
2026-06-26-prod-maintenance.log
2026-06-27-prod-maintenance.log
2026-06-28-prod-maintenance.log
2026-06-29-prod-maintenance.log
2026-06-30-prod-maintenance.log
2026-07-07-gpvextvpn01-prod-maintenance.log
weekly-rollup-2026-06-24-to-2026-06-30.json
```

## Troubleshooting Notes

If the VPN gateway cannot be resolved:

```bash
python3 tunnel_agent.py --env dev --no-upload
```

If upload fails, validate the runtime variables:

```bash
echo $LOG_UPLOAD_BUCKET
echo $ACCESS_KEY_ID
echo $ACCESS_KEY
echo $INSTALLER_KEY
```

If logs are missing, check the local log directory:

```bash
ls -la ./logs
```

If Helpdesk is engaged, provide:

```text
Branch Number
Location Code
Workstation Name
Environment Profile
Gateway Error
Session ID
Diagnostics Log Path
```

## Notes

Use the `dev` profile for local testing and support workflow validation. Use production-style profiles only for scheduled validation or Helpdesk-approved troubleshooting. Emergency remote-office workstation testing requires a Helpdesk bypass code.
