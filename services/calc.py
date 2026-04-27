def calculate_bolus(
    carbs: float,
    icr: float,
    isf: float,
    target_bg: float,
    current_bg: float | None = None,
) -> dict:
    carb_dose = carbs / icr
    correction_dose = 0.0

    if current_bg is not None and current_bg > target_bg:
        correction_dose = (current_bg - target_bg) / isf

    return {
        "carb_dose": round(carb_dose, 1),
        "correction_dose": round(correction_dose, 1),
        "total_dose": round(carb_dose + correction_dose, 1),
    }
