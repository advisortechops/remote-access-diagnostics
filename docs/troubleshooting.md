# Troubleshooting

## Gateway is unreachable

Confirm the endpoint can resolve and that outbound TCP/443 is allowed.

Run the diagnostics without upload:

    python3 tunnel_agent.py --env dev --no-upload

## Prod upload failures

Check that the configured upload target matches the expected environment.

    s3://remote-access-prod-logs/vpn/session-dumps/

The legacy uploader may still require static credentials on older support systems.

## Missing diagnostics logs

Logs are written to:

    ./logs

The generated JSON file contains the session ID, gateway, environment, and upload target.
