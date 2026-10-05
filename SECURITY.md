# Responsible use

AgentSec is intended for defensive security work on systems you own or are explicitly authorized to assess.

The default mode is safe demo mode. It uses deterministic fixture evidence and does not execute network probes. Any future collector adapter must enforce an explicit authorization boundary, validate targets, apply timeouts, redact secrets from logs, and preserve an audit trail.

For a production deployment, add authentication and authorization, request rate limits, queue isolation, secret management, network egress controls, and a review gate before enabling active scanners.
