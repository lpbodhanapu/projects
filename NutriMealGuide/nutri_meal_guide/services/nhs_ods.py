from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import requests


def fetch_all_nhs_gp_practices() -> Tuple[List[Dict[str, str]], Optional[str]]:
    """
    Fetch GP practices from NHS ODS API. Tries with Limit first, then pagination.
    Returns (list of practices, error_message or None).
    """
    url = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations"
    all_orgs: List[Dict[str, str]] = []

    def parse_orgs(data: dict) -> List[Dict[str, str]]:
        return [
            {
                "Name": org.get("Name", ""),
                "ODS Code": org.get("OrgId", ""),
                "Status": org.get("Status", ""),
                "Postcode": org.get("PostCode", ""),
                "Details link": org.get("OrgLink", ""),
            }
            for org in data.get("Organisations", [])
        ]

    try:
        resp = requests.get(
            url,
            params={"PrimaryRoleId": "RO177", "Limit": 1000},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        all_orgs.extend(parse_orgs(data))
    except Exception as e:
        return [], str(e)

    offset = 1000
    while len(all_orgs) % 1000 == 0 and len(all_orgs) > 0:
        try:
            resp = requests.get(
                url,
                params={"PrimaryRoleId": "RO177", "Limit": 1000, "Offset": offset},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            batch = parse_orgs(data)
            if not batch:
                break
            all_orgs.extend(batch)
            if len(batch) < 1000:
                break
            offset += 1000
        except Exception:
            break

    return all_orgs, None

