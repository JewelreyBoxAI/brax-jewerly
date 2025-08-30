import json, httpx, os
from .redis_cache import cache_setex
from ..config.settings import settings

async def forward_lead_webhook(lead: dict) -> dict:
    """Primary path: post to GHL Inbound Webhook."""
    if not settings.ghl_webhook_url:
        return {"status": "skipped", "reason": "no_webhook"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(settings.ghl_webhook_url, json=lead)
        return {"status": "ok", "code": r.status_code}

async def upsert_contact_rest(lead: dict) -> dict:
    """Optional REST path if API key is provided."""
    if not settings.ghl_api_key:
        return {"status": "skipped", "reason": "no_api_key"}
    headers = {
        "Authorization": f"Bearer {settings.ghl_api_key}",
        "Version": settings.ghl_api_version,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "firstName": lead.get("name") or "",
        "email": lead.get("email"),
        "phone": lead.get("phone"),
        "source": "Brax Chatbot",
        "country": "US",
        "customField": [{"id":"intent","value": lead.get("intent","")}],
    }
    async with httpx.AsyncClient(timeout=10, base_url=settings.ghl_api_base, headers=headers) as client:
        res = await client.post("/contacts/", json=payload)
        if settings.ghl_location_id and settings.ghl_pipeline_id and settings.ghl_stage_id:
            try:
                data = res.json()
                contact_id = data.get("contact", {}).get("id")
                if contact_id:
                    opp = {
                        "name": f"Brax Lead - {lead.get('intent','general')}",
                        "contactId": contact_id,
                        "locationId": settings.ghl_location_id,
                        "pipelineId": settings.ghl_pipeline_id,
                        "pipelineStageId": settings.ghl_stage_id,
                        "status": "open",
                    }
                    await client.post("/opportunities/", json=opp)
            except Exception:
                pass
        return {"status": "ok", "code": res.status_code}