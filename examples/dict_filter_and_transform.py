from easy_rule_engine import Rule, RuleEngine, attr_spec, attr_transform, dict_setter

Item = dict  # Only for clearer type hints; you can omit this.

items = [
    {"a": 5, "b": "X", "c": 2024},
    {"a": 15, "b": "Y", "c": 2021},
    {"a": 30, "b": "Z", "c": 2023},
]


# 1) Define attribute getters
def get_a(item: dict) -> int:
    return item["a"]


def get_b(item: dict) -> str:
    return item["b"]


def get_c(item: dict) -> int:
    return item["c"]


# 2) Define conditions (Specification)
a_between_10_20 = attr_spec(get_a, lambda v: 10 <= v <= 20)
b_in_XY = attr_spec(get_b, lambda v: v in {"X", "Y"})
c_after_2020 = attr_spec(get_c, lambda v: v >= 2020)

# Combined condition: a in [10, 20] AND b in {X, Y} AND c >= 2020
cond_main = a_between_10_20 & b_in_XY & c_after_2020

# 3) Define transformation (increment `a` by 1)
inc_a = attr_transform(
    getter=get_a,
    setter=dict_setter("a"),
    value_func=lambda v: v + 1,
)

rule1 = Rule(
    condition=cond_main,
    transform=inc_a,
    name="rule_a_between_and_b_xy_and_c_after_2020",
)

# 4) Build engine and run
engine = RuleEngine(
    rules=[rule1],
    keep_unmatched=False,  # Drop items that match no rules
    match_mode="all",  # Apply all matching rules (only one here)
)

new_items = engine.process(items)

# new_items will contain only the second item (a: 15 -> 16); the rest are filtered out.
print(new_items)


