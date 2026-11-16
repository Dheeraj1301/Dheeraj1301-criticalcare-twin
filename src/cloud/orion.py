"""FIWARE Orion-LD adapter for NGSI-LD digital-twin entities."""
from __future__ import annotations

from typing import Any

import httpx


class OrionDigitalTwinClient:
    def __init__(self, base_url: str = "http://127.0.0.1:1026", timeout: float = 3.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @staticmethod
    def entity_id(patient_key: str) -> str:
        return f"urn:ngsi-ld:CriticalCareTwin:{patient_key}"

    def entity(self, payload: dict[str, Any]) -> dict[str, Any]:
        patient_key = payload["patient_key"]
        properties: dict[str, Any] = {
            "twinId": {"type": "Property", "value": payload["twin_id"]},
            "twinVersion": {"type": "Property", "value": payload["twin_version"]},
            "siteId": {"type": "Property", "value": payload["site_id"]},
            "observedAt": {"type": "Property", "value": payload["timestamp"]},
            "risk": {"type": "Property", "value": payload["risk"]},
            "uncertainty": {"type": "Property", "value": payload["uncertainty"]},
        }
        for name, value in payload["state"].items():
            properties[name] = {
                "type": "Property",
                "value": value,
                "observedAt": payload["timestamp"],
            }
        return {"id": self.entity_id(patient_key), "type": "CriticalCareTwin", **properties}

    def upsert(self, payload: dict[str, Any]) -> str:
        entity = self.entity(payload)
        response = httpx.post(
            f"{self.base_url}/ngsi-ld/v1/entities",
            json=entity,
            headers={"Content-Type": "application/ld+json"},
            timeout=self.timeout,
        )
        if response.status_code == 409:
            attrs = {k: v for k, v in entity.items() if k not in {"id", "type"}}
            response = httpx.patch(
                f"{self.base_url}/ngsi-ld/v1/entities/{entity['id']}/attrs",
                json=attrs,
                headers={"Content-Type": "application/ld+json"},
                timeout=self.timeout,
            )
        response.raise_for_status()
        return entity["id"]

    def get(self, patient_key: str) -> dict[str, Any]:
        response = httpx.get(
            f"{self.base_url}/ngsi-ld/v1/entities/{self.entity_id(patient_key)}",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def online(self) -> bool:
        try:
            return httpx.get(f"{self.base_url}/version", timeout=0.8).is_success
        except httpx.HTTPError:
            return False
