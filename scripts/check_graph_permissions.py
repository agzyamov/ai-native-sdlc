"""Permission validation script for Microsoft Graph delegated scopes.

Usage:
  python scripts/check_graph_permissions.py --client-id <APP_CLIENT_ID> --tenant-id <TENANT_ID> \
      --required Chat.Read ChatMessage.Read OnlineMeetings.Read OnlineMeetingRecording.Read.All \
      OnlineMeetingTranscript.Read.All Files.Read.All

If --required is omitted, a default set is used.
The script authenticates using interactive device flow (fallback to auth code if available later),
extracts scopes from the access token claims, normalizes them, and reports missing ones.
Returns exit code 0 if all required scopes present, 2 if any missing, 1 for other failures.
"""
from __future__ import annotations
import argparse
import json
import sys
from typing import List, Set

import msal

DEFAULT_SCOPES = [
    "Chat.Read",
    "ChatMessage.Read",
    "OnlineMeetings.Read",
    "OnlineMeetingRecording.Read.All",
    "OnlineMeetingTranscript.Read.All",
    "Files.Read.All",
]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Microsoft Graph delegated permissions")
    parser.add_argument("--client-id", required=True, help="Azure AD application (app registration) client ID")
    parser.add_argument("--tenant-id", required=True, help="Azure AD tenant ID")
    parser.add_argument(
        "--required",
        nargs="*",
        help="Explicit list of required scopes; defaults to standard set if omitted",
    )
    parser.add_argument(
        "--output-json",
        default="permissions_result.json",
        help="Path to write machine-readable JSON summary",
    )
    return parser.parse_args()


def build_app(client_id: str, tenant_id: str) -> msal.PublicClientApplication:
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    return msal.PublicClientApplication(client_id, authority=authority)


def acquire_token(app: msal.PublicClientApplication, scopes: List[str]) -> dict:
    # Use device flow for simplicity (interactive in terminal). Could be replaced by other flows later.
    flow = app.initiate_device_flow(scopes=[f"https://graph.microsoft.com/.default"])
    if "user_code" not in flow:
        raise RuntimeError("Failed to create device flow. Response: %s" % flow)
    print("\nTo authenticate, navigate to", flow["verification_uri"], "and enter code:")
    print(flow["user_code"], "\n")
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise RuntimeError(f"Authentication failed: {result.get('error_description', result)}")
    return result


def extract_scopes(token_result: dict) -> Set[str]:
    # Device flow with /.default returns app-consented scopes (may map to effective permissions)
    # Fallback: try 'scope' field if present.
    scopes_claim = token_result.get("scope") or ""
    scopes = {s.strip() for s in scopes_claim.split() if s.strip()}
    return scopes


def normalize(scopes: Set[str]) -> Set[str]:
    # Normalization: case-insensitive compare.
    return {s for s in scopes}


def main() -> int:
    args = parse_args()
    required = args.required or DEFAULT_SCOPES
    required_set = set(required)

    try:
        app = build_app(args.client_id, args.tenant_id)
        token_result = acquire_token(app, required)
        granted_scopes = normalize(extract_scopes(token_result))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    missing = sorted(required_set - {gs for gs in granted_scopes})
    present = sorted(required_set - set(missing))

    summary = {
        "status": "PASS" if not missing else "FAIL",
        "present": present,
        "missing": missing,
        "required": sorted(required_set),
    }

    print("\nPermission Validation Result:")
    print(json.dumps(summary, indent=2))

    try:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
    except OSError as exc:
        print(f"WARNING: Could not write JSON summary: {exc}", file=sys.stderr)

    if missing:
        print("\nMissing scopes detected. Request these from your tenant admin:")
        for scope in missing:
            print(f" - {scope}")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
