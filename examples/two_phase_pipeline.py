from easy_rule_engine import Rule, RuleEngine, Specification, Transformer, attr_spec, attr_transform, dict_setter

# -------------------------------------------
# Test Data
# -------------------------------------------

items = [
    {"id": 1, "score": 45, "category": "raw", "status": "new", "tags": []},
    {"id": 2, "score": 90, "category": "raw", "status": "new", "tags": []},
    {"id": 3, "score": 75, "category": "processed", "status": "new", "tags": []},
]

# -------------------------------------------
# Getter Functions
# -------------------------------------------


def get_score(i):
    return i["score"]


def get_status(i):
    return i["status"]


def get_category(i):
    return i["category"]


def get_tags(i):
    return i["tags"]


# -------------------------------------------
# Helper value functions
# -------------------------------------------


def mark_low_quality(old_tags):
    return list(old_tags) + ["low_quality"]


def mark_needs_processing(_old):
    return "needs_processing"


def mark_high_priority(_old):
    return "high_priority"


def add_finalized_tag(old_tags):
    return list(old_tags) + ["finalized"]


# -------------------------------------------
# Phase 1 Rules: Preprocessing
# -------------------------------------------

# Rule A: score < 50 -> tags += ["low_quality"]
score_lt_50 = attr_spec(get_score, lambda s: s < 50)
transform_low_quality = attr_transform(
    getter=get_tags,
    setter=dict_setter("tags"),
    value_func=mark_low_quality,
)
rule_low_quality = Rule(
    condition=score_lt_50,
    transform=transform_low_quality,
    name="low_quality_rule",
)

# Rule B: category == "raw" -> status = "needs_processing"
is_raw = attr_spec(get_category, lambda c: c == "raw")
transform_needs_processing = attr_transform(
    getter=get_status,
    setter=dict_setter("status"),
    value_func=mark_needs_processing,
)
rule_needs_processing = Rule(
    condition=is_raw,
    transform=transform_needs_processing,
    name="raw_to_processing",
)

engine_phase1 = RuleEngine(
    rules=[rule_low_quality, rule_needs_processing],
    keep_unmatched=True,
    match_mode="all",
)

stage1_items = engine_phase1.process(items)

# -------------------------------------------
# Phase 2 Rules: Final Processing
# -------------------------------------------

# Rule C: high priority if needs_processing AND score >= 80
needs_processing = attr_spec(get_status, lambda s: s == "needs_processing")
score_ge_80 = attr_spec(get_score, lambda s: s >= 80)
condition_high_priority = needs_processing & score_ge_80

transform_high_priority = attr_transform(
    getter=get_status,
    setter=dict_setter("status"),
    value_func=mark_high_priority,
)
rule_high_priority = Rule(
    condition=condition_high_priority,
    transform=transform_high_priority,
    name="high_priority_rule",
)

# Rule D: stop further processing for low_quality items
contains_low_quality = attr_spec(get_tags, lambda tags: "low_quality" in tags)
rule_stop_low_quality = Rule(
    condition=contains_low_quality,
    transform=Transformer.identity(),
    name="stop_low_quality",
    stop_on_match=True,
)

# Rule E: add tag 'finalized'
transform_finalized = attr_transform(
    getter=get_tags,
    setter=dict_setter("tags"),
    value_func=add_finalized_tag,
)

rule_finalize = Rule(
    condition=Specification.always_true(),
    transform=transform_finalized,
    name="finalize",
)

engine_phase2 = RuleEngine(
    rules=[rule_high_priority, rule_stop_low_quality, rule_finalize],
    keep_unmatched=True,
    match_mode="all",
)

final_items = engine_phase2.process(stage1_items)

# -------------------------------------------
# Print Results
# -------------------------------------------

print("=== Phase 1 Output ===")
for x in stage1_items:
    print(x)

print("\n=== Final Output ===")
for x in final_items:
    print(x)


