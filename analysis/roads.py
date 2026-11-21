"""First scenario in which a mapped road counts. A, B and C are nested."""

SCENARIOS = ("A", "B", "C")
SURFACE_ROADS = {
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link",
    "unclassified", "residential", "living_street", "service",
}
PICKUP_PASSABLE = {"excellent", "good", "intermediate", "bad", "very_bad"}
ROUGHER_THAN_PICKUP = {"horrible", "very_horrible", "impassable"}
YES = {"yes", "true", "1"}


def first_scenario(tags):
    """Return (scenario, reason). None means excluded from all three runs."""
    highway = tags.get("highway")
    if highway not in SURFACE_ROADS and highway != "track":
        return None, "outside road classes"
    if tags.get("tunnel") not in (None, "", "no", "false", "0") or tags.get("location") == "underground":
        return None, "underground"
    if any(tags.get(key) in YES for key in ("area", "abandoned", "disused", "impassable")):
        return None, "area, inactive or impassable"
    if tags.get("smoothness") in ROUGHER_THAN_PICKUP:
        return None, "beyond pickup threshold"
    if highway != "track":
        return "A", "ordinary surface road"
    if tags.get("smoothness") in PICKUP_PASSABLE:
        return "A", "pickup-passable smoothness"
    # Missing and nonstandard smoothness values both require the grade fallback.
    grade = tags.get("tracktype")
    if grade in {"grade1", "grade2", "grade3"}:
        return "A", "track grade 1-3"
    if grade in {"grade4", "grade5"}:
        return "C", "track grade 4-5"
    return "B", "missing or unrecognised grade"
