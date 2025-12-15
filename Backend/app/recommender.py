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

