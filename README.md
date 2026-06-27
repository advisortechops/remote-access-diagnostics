# Remote Access Diagnostics

Remote Access Diagnostics is a lightweight utility for validating remote-access tunnel readiness across dev and production environments.

The tool performs basic tunnel health checks, collects local network state, writes a session diagnostics bundle, and supports uploading diagnostic artifacts to S3 for later review.

## Supported environments

- dev
- prod

## Usage

Install dependencies:

```bash
pip install -r requirements.txt

