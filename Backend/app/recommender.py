def winter_feature(drivetrain: str) -> float: #score metric drivtrain 
    d = drivetrain.upper()
    if d == "AWD":
        return 1.0 
    if d == "FWD":
        return 0.7 
    if d == "RWD":
        return 0.4
    return 0.5

def winter_score(drivetrain: str, w_winter: float) -> float: #feature x weight 
    return winter_feature(drivetrain) * w_winter

# NOTE:
# Fuel efficiency is currently modeled using MPG and applies to ICE and hybrid vehicles only.
# EV efficiency (kWh/100km or MPGe) is intentionally excluded in v1 and will be handled
# as a separate feature with its own normalization logic in a future iteration.


def fuel_feature(mpg: float, min_mpg: float = 20.0, max_mpg: float = 40.0) -> float:
    if mpg <= min_mpg:
        return 0 
    if mpg >= max_mpg:
        return 1.0
    return (mpg - min_mpg) / (max_mpg - min_mpg)

def fuel_score(mpg: float, w_fuel: float) -> float:
    return fuel_feature(mpg) * w_fuel