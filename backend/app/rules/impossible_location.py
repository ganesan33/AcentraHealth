import math
import time
from typing import Any, Dict, Optional, Tuple
from app.rules.base import BaseFraudRule, RuleResult


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on the Earth in kilometers."""
    r = 6371.0  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


class ImpossibleLocationRule(BaseFraudRule):
    """
    Impossible Location / Geo-Velocity Rule:
    Detects impossible physical travel between successive transactions for the same user.
    Flags instances where the implied travel speed exceeds commercial flight limits (e.g. > 850 km/h)
    or where different countries are recorded within an impossible travel window.
    """
    rule_id: str = "LOCATION_IMPOSSIBLE_SPEED"
    rule_name: str = "Impossible Travel Velocity Rule"
    description: str = "Flags rapid geolocation hops indicating credential theft or impossible physical transit"
    weight: float = 50.0
    enabled: bool = True

    # Memory store: user_id -> (latitude, longitude, country, timestamp)
    _user_last_locations: Dict[str, Tuple[Optional[float], Optional[float], Optional[str], float]] = {}

    def __init__(self, max_speed_kmh: float = 850.0, weight: float = 50.0) -> None:
        self.max_speed_kmh = max_speed_kmh
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        user_id = str(transaction_data.get("user_id", ""))
        lat = transaction_data.get("latitude")
        lon = transaction_data.get("longitude")
        country = transaction_data.get("location_country")
        now = time.time()

        if not user_id or user_id == "unknown":
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                triggered=False,
                score_impact=0.0,
                reason="User ID not provided for geolocation check",
            )

        # Check if previous location exists for this user
        last_record = self._user_last_locations.get(user_id)
        # Record current position for next evaluation
        self._user_last_locations[user_id] = (lat, lon, country, now)

        if not last_record:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                triggered=False,
                score_impact=0.0,
                reason="First recorded geolocation for user; baseline established",
                metadata={"country": country, "lat": lat, "lon": lon},
            )

        last_lat, last_lon, last_country, last_time = last_record
        time_elapsed_hours = (now - last_time) / 3600.0

        # Scenario 1: Coordinate-based speed check
        if (
            lat is not None
            and lon is not None
            and last_lat is not None
            and last_lon is not None
            and time_elapsed_hours > 0
        ):
            dist_km = haversine_distance_km(last_lat, last_lon, lat, lon)
            speed_kmh = dist_km / time_elapsed_hours

            if speed_kmh > self.max_speed_kmh and dist_km > 50.0:
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    triggered=True,
                    score_impact=self.weight,
                    reason=(
                        f"Impossible travel speed: {dist_km:.1f} km traversed in "
                        f"{time_elapsed_hours * 60:.1f} minutes ({speed_kmh:.0f} km/h > {self.max_speed_kmh} km/h)"
                    ),
                    metadata={
                        "distance_km": round(dist_km, 2),
                        "time_elapsed_minutes": round(time_elapsed_hours * 60, 2),
                        "calculated_speed_kmh": round(speed_kmh, 2),
                    },
                )

        # Scenario 2: Different country within 1 hour
        if (
            country
            and last_country
            and country != last_country
            and time_elapsed_hours < 1.0
        ):
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                triggered=True,
                score_impact=self.weight,
                reason=(
                    f"Impossible cross-border jump: transaction in {country} recorded "
                    f"{time_elapsed_hours * 60:.1f} mins after transaction in {last_country}"
                ),
                metadata={
                    "previous_country": last_country,
                    "current_country": country,
                    "elapsed_minutes": round(time_elapsed_hours * 60, 2),
                },
            )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=False,
            score_impact=0.0,
            reason="Location velocity is physically plausible",
            metadata={"country": country},
        )
