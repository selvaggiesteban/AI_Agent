"""Build Marketing API payloads from a campaign config file."""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .client import REPO_ROOT, GraphAPIError

WEEKDAYS = {"mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6, "sun": 0}
GENDERS = {"m": 1, "f": 2, "male": 1, "female": 2}
WHATSAPP_LINK = "https://api.whatsapp.com/send"


class ConfigError(ValueError):
    """Raised when a campaign config file is invalid."""


def load_config(path: str | Path) -> dict:
    config_path = Path(path)
    if not config_path.is_absolute():
        config_path = REPO_ROOT / config_path
    if not config_path.is_file():
        raise ConfigError(f"config file not found: {config_path}")
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {config_path}: {exc}") from exc
    if not isinstance(payload.get("meta_ads"), dict):
        raise ConfigError(f'{config_path}: top-level "meta_ads" object is required')
    payload["_path"] = str(config_path)
    return payload


def hhmm_to_minutes(value: str) -> int:
    """Convert HH:MM to minutes; '00:00' as an end time means midnight (1440)."""
    try:
        hours_str, _, minutes_str = value.strip().partition(":")
        hours, minutes = int(hours_str), int(minutes_str)
        if minutes > 59 or hours > 24 or (hours == 24 and minutes > 0):
            raise ValueError
    except ValueError:
        raise ConfigError(f"invalid time {value!r} (expected HH:MM)")
    if hours == 24 or (hours == 0 and minutes == 0):
        return 1440
    return hours * 60 + minutes


def resolve_asset(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def validate_config(config: dict) -> list[str]:
    """Local (offline) validation. Returns warnings; raises ConfigError on hard errors."""
    meta = config["meta_ads"]
    warnings: list[str] = []

    campaign = meta.get("campaign") or {}
    if not campaign.get("name"):
        raise ConfigError("meta_ads.campaign.name is required")

    adset = meta.get("adset") or {}
    if not adset.get("name"):
        raise ConfigError("meta_ads.adset.name is required")

    budget = adset.get("budget") or {}
    mode = budget.get("mode", "auto")
    if mode not in ("auto", "daily", "lifetime"):
        raise ConfigError('meta_ads.adset.budget.mode must be "auto", "daily" or "lifetime"')
    daily_amount = budget.get("daily_amount")
    if not isinstance(daily_amount, (int, float)) or daily_amount <= 0:
        raise ConfigError("meta_ads.adset.budget.daily_amount must be a positive number (major currency units)")
    if mode == "lifetime" and budget.get("lifetime_amount") is not None:
        if budget["lifetime_amount"] <= 0:
            raise ConfigError("meta_ads.adset.budget.lifetime_amount must be positive")

    schedule = adset.get("schedule") or {}
    schedule_days: list[int] = []
    if schedule.get("enabled"):
        day_names = schedule.get("days") or []
        if not day_names:
            raise ConfigError('meta_ads.adset.schedule.enabled=true requires a non-empty "days" list')
        for day in day_names:
            if day not in WEEKDAYS:
                raise ConfigError(f"unknown schedule day {day!r} (use mon..sun)")
            schedule_days.append(WEEKDAYS[day])
        start_minute = hhmm_to_minutes(schedule.get("start", ""))
        end_minute = hhmm_to_minutes(schedule.get("end", ""))
        if end_minute <= start_minute:
            raise ConfigError("schedule end must be after start (use 00:00 or 24:00 for midnight)")
        if start_minute % 60 or end_minute % 60:
            raise ConfigError("schedule start/end must fall on a whole hour")
        if end_minute - start_minute < 60:
            raise ConfigError("schedule window must be at least 1 hour")

    targeting = adset.get("targeting") or {}
    geo = targeting.get("geo") or {}
    geo_mode = geo.get("mode")
    if geo_mode not in ("coordinates", "address", "city_radius", "city"):
        raise ConfigError('meta_ads.adset.targeting.geo.mode must be "coordinates", "address", "city_radius" or "city"')
    if geo_mode == "coordinates":
        for field in ("latitude", "longitude"):
            if not isinstance(geo.get(field), (int, float)):
                raise ConfigError(f"geo.coordinates requires numeric {field}")
        radius = geo.get("radius_km")
        if not isinstance(radius, (int, float)) or not 1 <= radius <= 80:
            raise ConfigError("geo radius_km must be between 1 and 80 (Meta city radius minimum is 17 km)")
    if geo_mode == "address" and not geo.get("address_string"):
        raise ConfigError("geo.address mode requires address_string")
    if geo_mode in ("city_radius", "city"):
        if not geo.get("city") and not geo.get("key"):
            raise ConfigError(f"geo.{geo_mode} requires a city name (or a pre-resolved key)")
        if geo_mode == "city_radius":
            radius = geo.get("radius_km", 17)
            if radius < 17:
                raise ConfigError(
                    "Meta does not allow city radii below 17 km; use geo.mode=coordinates for a smaller radius"
                )

    age_min = targeting.get("age_min", 13)
    age_max = targeting.get("age_max", 65)
    if not (13 <= age_min <= age_max <= 65):
        raise ConfigError("targeting ages must satisfy 13 <= age_min <= age_max <= 65")
    for gender in targeting.get("genders") or []:
        if gender not in GENDERS:
            raise ConfigError(f"unknown gender {gender!r} (use m/f)")

    ads = meta.get("ads") or []
    if not ads:
        raise ConfigError("meta_ads.ads must contain at least one ad")
    for index, ad in enumerate(ads, start=1):
        label = ad.get("name") or f"ad #{index}"
        if not ad.get("image"):
            raise ConfigError(f'{label}: "image" is required')
        if not ad.get("primary_text"):
            raise ConfigError(f'{label}: "primary_text" is required')
        if not ad.get("headline"):
            raise ConfigError(f'{label}: "headline" is required')
        image_path = resolve_asset(ad["image"])
        if not image_path.is_file():
            raise ConfigError(f"{label}: image not found: {image_path}")
        if ad.get("crop") not in (None, "square"):
            raise ConfigError(f'{label}: crop must be "square" or omitted')
        if ad.get("crop_focus") not in (None, "center", "left", "right"):
            raise ConfigError(f'{label}: crop_focus must be center/left/right')

    if not meta.get("page_name") and not meta.get("page_id"):
        raise ConfigError('meta_ads.page_name (or page_id) is required')

    return warnings


def major_to_minor(amount: float, offset: int) -> int:
    """Convert major currency units to the API's minor denomination."""
    return int(round(float(amount) * (10 ** offset)))


def build_campaign_fields(config: dict, status: str) -> dict:
    meta = config["meta_ads"]
    campaign = meta.get("campaign") or {}
    return {
        "name": campaign["name"],
        "objective": campaign.get("objective", "OUTCOME_ENGAGEMENT"),
        "special_ad_categories": "[]",
        "status": status,
    }


def build_geo_locations(geo: dict, resolved_city: dict | None = None) -> dict:
    mode = geo["mode"]
    location_types = geo.get("location_types", ["home", "recent"])
    if mode == "coordinates":
        custom = {
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "radius": geo.get("radius_km", 5),
            "distance_unit": geo.get("distance_unit", "kilometer"),
        }
        if geo.get("name"):
            custom["name"] = geo["name"]
        return {"custom_locations": [custom], "location_types": location_types}
    if mode == "address":
        custom = {
            "address_string": geo["address_string"],
            "radius": geo.get("radius_km", 5),
            "distance_unit": geo.get("distance_unit", "kilometer"),
        }
        if geo.get("name"):
            custom["name"] = geo["name"]
        return {"custom_locations": [custom], "location_types": location_types}
    country = geo.get("country", "AR")
    if mode == "city":
        key = geo.get("key") or (resolved_city or {}).get("key")
        if not key:
            raise ConfigError(f"city {geo.get('city')!r} could not be resolved; run resolve-geo")
        return {"countries": [country], "cities": [{"key": key}], "location_types": location_types}
    key = geo.get("key") or (resolved_city or {}).get("key")
    if not key:
        raise ConfigError(f"city {geo.get('city')!r} could not be resolved; run resolve-geo")
    return {
        "countries": [country],
        "cities": [{"key": key, "radius": geo.get("radius_km", 17), "distance_unit": geo.get("distance_unit", "kilometer")}],
        "location_types": location_types,
    }


def build_targeting_fields(config: dict, resolved_city: dict | None = None) -> dict:
    targeting = config["meta_ads"]["adset"]["targeting"]
    fields: dict = {
        "age_min": targeting.get("age_min", 13),
        "age_max": targeting.get("age_max", 65),
        "geo_locations": build_geo_locations(targeting["geo"], resolved_city),
    }
    genders = targeting.get("genders")
    if genders:
        fields["genders"] = [GENDERS[g] for g in genders]
    platforms = targeting.get("device_platforms")
    if platforms:
        fields["device_platforms"] = platforms
    return fields


def build_schedule_fields(config: dict) -> dict:
    schedule = config["meta_ads"]["adset"].get("schedule") or {}
    if not schedule.get("enabled"):
        return {"pacing_type": '["standard"]'}
    days = sorted({WEEKDAYS[d] for d in schedule["days"]})
    start_minute = hhmm_to_minutes(schedule["start"])
    end_minute = hhmm_to_minutes(schedule["end"])
    entry = {
        "start_minute": start_minute,
        "end_minute": end_minute,
        "days": days,
        "timezone_type": schedule.get("timezone_type", "ADVERTISER"),
    }
    return {
        "pacing_type": '["day_parting"]',
        "adset_schedule": json.dumps([entry]),
    }


def budget_variants(config: dict, currency_offset: int) -> list[tuple[str, dict]]:
    """Return ordered (mode_name, fields) budget payloads to attempt."""
    adset = config["meta_ads"]["adset"]
    budget = adset.get("budget") or {}
    mode = budget.get("mode", "auto")
    daily_minor = major_to_minor(budget["daily_amount"], currency_offset)
    schedule = adset.get("schedule") or {}
    scheduled_days = len(schedule.get("days") or []) if schedule.get("enabled") else 0

    daily_fields = {"daily_budget": str(daily_minor), "end_time": "0"}

    flight_days = int(budget.get("flight_days", 28))
    weeks = max(1, math.ceil(flight_days / 7))
    days_in_flight = (scheduled_days or 7) * weeks
    lifetime_minor = daily_minor * days_in_flight
    end_time = datetime.now(timezone.utc) + timedelta(days=flight_days)
    lifetime_fields = {
        "lifetime_budget": str(lifetime_minor),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S+00:00"),
    }

    if mode == "daily":
        return [("daily", daily_fields)]
    if mode == "lifetime":
        return [("lifetime", lifetime_fields)]
    if schedule.get("enabled"):
        return [("daily", daily_fields), ("lifetime", lifetime_fields)]
    return [("daily", daily_fields)]


def build_adset_fields(
    config: dict,
    campaign_id: str,
    page_id: str,
    targeting: dict,
    budget_fields: dict,
    status: str,
    validate_only: bool = False,
) -> dict:
    adset = config["meta_ads"]["adset"]
    fields = {
        "name": adset["name"],
        "campaign_id": campaign_id,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": adset.get("optimization_goal", "CONVERSATIONS"),
        "destination_type": adset.get("destination_type", "WHATSAPP"),
        "promoted_object": {"page_id": page_id},
        "targeting": targeting,
        "status": status,
        **budget_fields,
        **build_schedule_fields(config),
    }
    if validate_only:
        fields["execution_options"] = ["validate_only"]
    return fields


def build_creative_fields(config: dict, page_id: str, ad: dict, image_hash: str) -> dict:
    link_data: dict = {
        "image_hash": image_hash,
        "message": ad["primary_text"],
        "name": ad["headline"],
        "link": WHATSAPP_LINK,
        "call_to_action": {"type": "WHATSAPP_MESSAGE", "value": {"app_destination": "WHATSAPP"}},
    }
    if ad.get("description"):
        link_data["description"] = ad["description"]
    if ad.get("welcome_message"):
        link_data["page_welcome_message"] = ad["welcome_message"]
    return {
        "name": f"{ad['name']} creative",
        "object_story_spec": {"page_id": page_id, "link_data": link_data},
    }


def build_ad_fields(ad: dict, adset_id: str, creative_id: str, status: str) -> dict:
    return {
        "name": ad["name"],
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": status,
    }
