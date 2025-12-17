from typing import Dict, Optional


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(max(v, 0.0) for v in weights.values())
    if total == 0:
        return {k: 1.0 / len(weights) for k in weights} if weights else {}
    return {k: max(v, 0.0) / total for k, v in weights.items()}


# Winter driving

def winter_feature(drivetrain: str) -> float:
    d = drivetrain.upper()
    if d == "AWD":
        return 1.0
    if d == "FWD":
        return 0.7
    if d == "RWD":
        return 0.4
    return 0.5


def winter_score(drivetrain: str, weight: float) -> float:
    return winter_feature(drivetrain) * weight


# Fuel efficiency (ICE/Hybrid MPG for now)

def fuel_feature(mpg: Optional[float], min_mpg: float = 20.0, max_mpg: float = 40.0) -> float:
    if mpg is None:
        return 0.0
    if mpg <= min_mpg:
        return 0.0
    if mpg >= max_mpg:
        return 1.0
    return (mpg - min_mpg) / (max_mpg - min_mpg)


def fuel_score(mpg: Optional[float], weight: float) -> float:
    return fuel_feature(mpg) * weight


# Price fit vs budget

def price_fit_feature(price: Optional[float], budget: float, over_penalty: float = 0.5) -> float:
    if price is None:
        return 0.0
    if budget <= 0:
        return 0.0
    if price <= budget:
        return 1.0
    over_ratio = (price - budget) / budget
    return clamp(1.0 - over_ratio * over_penalty)


def price_fit_score(price: Optional[float], budget: float, weight: float) -> float:
    return price_fit_feature(price, budget) * weight


# Acceleration (0-60)

def acceleration_feature(zero_to_sixty: Optional[float], best: float = 4.0, worst: float = 10.0) -> float:
    if zero_to_sixty is None:
        return 0.0
    if zero_to_sixty <= best:
        return 1.0
    if zero_to_sixty >= worst:
        return 0.0
    return 1.0 - ((zero_to_sixty - best) / (worst - best))


def acceleration_score(zero_to_sixty: Optional[float], weight: float) -> float:
    return acceleration_feature(zero_to_sixty) * weight


# Ownership cost (lower is better)

def ownership_cost_feature(annual_cost: Optional[float], best: float = 1500.0, worst: float = 5000.0) -> float:
    if annual_cost is None:
        return 0.0
    if annual_cost <= best:
        return 1.0
    if annual_cost >= worst:
        return 0.0
    return (worst - annual_cost) / (worst - best)


def ownership_cost_score(annual_cost: Optional[float], weight: float) -> float:
    return ownership_cost_feature(annual_cost) * weight


# Reliability (placeholder: expects 0..1 score from data)

def reliability_feature(score: Optional[float]) -> float:
    if score is None:
        return 0.5
    return clamp(score)


def reliability_score(raw_score: Optional[float], weight: float) -> float:
    return reliability_feature(raw_score) * weight
