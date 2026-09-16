"""Farmer AI Copilot (PRD §16/§28): LLM decides tool → backend executes → LLM explains.

The LLM is never the source of truth: structured tool results come from the
deterministic engines, then the LLM (if configured) phrases the explanation.
Without GROQ_API_KEY a rule-based responder uses the same verified data.
"""
import json
import re

import httpx
from sqlalchemy.orm import Session

from ..db import Listing, VendorProfile
from .data import CROPS
from .forecast import forecast_demand
from .pricing import recommend_price


def _normalize(q: str) -> str:
    return q.lower()


def _find_crop(q: str) -> str | None:
    for slug, meta in CROPS.items():
        if slug in q or meta["name"].lower() in q:
            return slug
    return None


def _tool_find_buyers(db: Session, vendor: VendorProfile, crop: str | None, quantity: float | None) -> list[dict]:
    from .matching import match_buyers
    listings = db.query(Listing).filter(Listing.vendor_id == vendor.id, Listing.status == "ACTIVE").all()
    if crop:
        listings = [l for l in listings if l.crop == crop]
    buyers: dict[str, dict] = {}
    for l in listings:
        for m in match_buyers(db, l):
            key = m["buyer_name"]
            if key not in buyers or m["match_pct"] > buyers[key]["match_pct"]:
                buyers[key] = m
    return list(buyers.values())[:6]


def _tool_earnings(db: Session, vendor: VendorProfile) -> dict:
    from ..db import Order
    orders = db.query(Order).filter(Order.vendor_id == vendor.id).all()
    gross = sum(o.gross_amount for o in orders)
    fees = sum(o.platform_fee for o in orders)
    logistics = sum(o.logistics_cost for o in orders)
    return {
        "gross": round(gross, 0),
        "platform_fee": round(fees, 0),
        "logistics": round(logistics, 0),
        "net": round(gross - fees - logistics, 0),
        "orders": len(orders),
        "delivered": len([o for o in orders if o.status == "DELIVERED"]),
    }


def _rule_answer(q: str, tool: str, data, vendor_name: str) -> str:
    """Deterministic explanation when no LLM provider is configured."""
    if tool == "find_buyers":
        if not data:
            return "No active buyer requests match your current listings right now. Consider creating a fresh listing or adjusting price — I'll re-check matching as soon as new requirements arrive."
        lines = [f"{b['buyer_name']} ({b['buyer_type']}): needs up to {b['quantity_kg']:.0f} kg at max ₹{b['max_price']:.0f}/kg, ~{b['distance_km']} km away — match score {b['match_pct']}%." for b in data]
        return "Here are the strongest current buyer matches for your produce:\n" + "\n".join(f"• {l}" for l in lines)
    if tool == "price":
        d = data
        return (
            f"Estimated market range for {d['crop'].replace('_', ' ')}: ₹{d['recommended_min']}–₹{d['recommended_max']}/kg "
            f"(confidence: {d['confidence']}).\n" + "\n".join(f"• {r}" for r in d["reasons"])
        )
    if tool == "earnings":
        d = data
        return (
            f"Across {d['orders']} orders ({d['delivered']} delivered): gross ₹{d['gross']:,.0f}, "
            f"platform fees ₹{d['platform_fee']:,.0f}, logistics ₹{d['logistics']:,.0f} — net earnings ₹{d['net']:,.0f}."
        )
    if tool == "demand":
        d = data
        direction = "up" if d["next_7d_pct"] >= 0 else "down"
        return (
            f"Demand for {d['crop'].replace('_', ' ')} is trending {direction} ~{abs(d['next_7d_pct'])}% over the next 7 days "
            f"(confidence: {d['confidence']}). 30-day outlook: {d['next_30d_pct']:+.0f}%."
        )
    if tool == "amie":
        d = data
        cf = d.get("counterfactual") or {}
        first = d.get("first_failure") or {}
        if d.get("system_status") == "GREEN":
            return (
                f"AMIE checked the next {d['horizon_days']} days day-by-day: the market stays feasible. "
                f"Peak capacity utilization {d.get('peak_utilization_pct', 0):.0f}%. "
                "Run a disturbance scenario in Market Intel → Feasibility Lab to stress-test it."
            )
        return (
            f"AMIE's cascade simulation flags {d.get('system_status')} — day-by-day, total unabsorbed produce "
            f"{d['totals']['unabsorbed_kg']:,.0f} kg"
            + (f", first failure day {first.get('day')}: {first.get('node_name')} deficit "
               f"{first.get('deficit_kg'):,.0f} kg ({first.get('why')})" if first else "")
            + (f". Best fix: {cf.get('label')} — rescues {cf.get('rescued_kg', 0):,.0f} kg for ₹{cf.get('cost', 0):,.0f}." if cf else ".")
        )
    if tool == "listings":
        if not data:
            return "You have no active listings. Head to Sell → photograph your harvest to create one in under a minute."
        lines = [f"{l['title']}: {l['quantity_available_kg']:.0f} kg left at ₹{l['price_per_kg']:.0f}/kg" for l in data]
        return "Your active listings:\n" + "\n".join(f"• {l}" for l in lines)
    return "I can help with prices, buyers, demand outlook, your listings and earnings. Try: \"Who is buying chilli near me?\""


# Tool spec for LLM providers (Groq / OpenAI-compatible function calling)
TOOLS = [
    {"type": "function", "function": {
        "name": "find_buyers",
        "description": "Find active buyer requests matching the vendor's listings",
        "parameters": {"type": "object", "properties": {
            "crop": {"type": "string"}, "quantity_kg": {"type": "number"}}, "required": []},
    }},
    {"type": "function", "function": {
        "name": "get_price_recommendation",
        "description": "Recommended price range for a crop with reasons",
        "parameters": {"type": "object", "properties": {
            "crop": {"type": "string"}, "quantity_kg": {"type": "number"}}, "required": ["crop"]},
    }},
    {"type": "function", "function": {
        "name": "get_earnings",
        "description": "Vendor gross/fees/logistics/net earnings summary",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }},
    {"type": "function", "function": {
        "name": "get_feasibility_check",
        "description": "AMIE day-by-day feasibility cascade for a crop: detects future market infeasibility and suggests interventions",
        "parameters": {"type": "object", "properties": {
            "crop": {"type": "string"}, "scenario": {"type": "string"}}, "required": ["crop"]},
    }},
    {"type": "function", "function": {
        "name": "get_demand_forecast",
        "description": "7/30-day demand outlook for a crop",
        "parameters": {"type": "object", "properties": {"crop": {"type": "string"}}, "required": ["crop"]},
    }},
    {"type": "function", "function": {
        "name": "get_listings",
        "description": "Vendor's current active listings",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }},
]


async def answer(db: Session, vendor: VendorProfile, user, question: str) -> dict:
    """Main copilot entry: classify intent → run tool → explain."""
    q = _normalize(question)
    crop = _find_crop(q)

    # 1) intent classification (deterministic pre-filter; LLM refines when available)
    if any(w in q for w in ("who is buying", "buyer", "buy my", "find buyer", "selling to", "demand for my")):
        intent = "find_buyers"
    elif any(w in q for w in ("price", "worth", "rate", "₹")):
        intent = "price"
    elif any(w in q for w in ("earn", "income", "revenue", "payout", "paid me")):
        intent = "earnings"
    elif any(w in q for w in ("feasib", "infeasib", "bottleneck", "overload", "capacity", "what happens if", "simulate the market", "spoiled", "go to waste", "unsold")):
        intent = "amie"
    elif any(w in q for w in ("demand", "outlook", "forecast", "trend", "next week", "grow next")):
        intent = "demand"
    elif any(w in q for w in ("listing", "inventory", "stock", "have left", "unsold")):
        intent = "listings"
    else:
        intent = "listings"

    # 2) execute the deterministic tool
    data = None
    if intent == "find_buyers":
        data = _tool_find_buyers(db, vendor, crop, None)
    elif intent == "price":
        if not crop:
            crop = "tomato"
        data = recommend_price(db, crop, 30, "A", vendor.district)
    elif intent == "earnings":
        data = _tool_earnings(db, vendor)
    elif intent == "amie":
        from .feasibility import extract_market_stats, run_amie
        stats = extract_market_stats(db, crop or "tomato", vendor.district or "Ernakulam")
        data = run_amie(stats, horizon_days=7, scenario_name="synchronized_harvest", seed=42, with_interventions=False)
    elif intent == "demand":
        data = forecast_demand(db, crop or "tomato")
    elif intent == "listings":
        ls = db.query(Listing).filter(Listing.vendor_id == vendor.id, Listing.status == "ACTIVE").all()
        data = [{"title": l.title, "quantity_available_kg": l.quantity_available_kg, "price_per_kg": copilot_price(l)} for l in ls]

    rule_reply = _rule_answer(question, intent, data, vendor.user.name)

    # 3) LLM explanation layer (provider-abstracted; skipped without API key)
    provider = "engine"
    from ..config import settings
    if settings.GROQ_API_KEY:
        try:
            system = (
                "You are FarmMesh AI's copilot for a farmer/vendor on an agricultural marketplace. "
                "Explain the following verified JSON tool result conversationally in at most 4 short lines. "
                "Never invent numbers, buyers, prices or orders not present in the data. "
                "Use ₹ for currency. Data: " + json.dumps({"tool": intent, "result": data, "question": question}, default=str)
            )
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                    json={"model": settings.GROQ_MODEL, "messages": [{"role": "system", "content": system}]},
                )
            if r.status_code == 200:
                reply = r.json()["choices"][0]["message"]["content"]
                provider = f"groq:{settings.GROQ_MODEL}"
                return {"reply": reply, "tool": intent, "data": data, "provider": provider}
        except Exception:
            pass  # graceful fallback to engine reply

    return {"reply": rule_reply, "tool": intent, "data": data, "provider": provider}
