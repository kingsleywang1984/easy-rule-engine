from dataclasses import dataclass

from easy_rule_engine import Rule, RuleEngine, attr_spec, attr_transform, dataclass_setter


@dataclass(frozen=True)
class Order:
    price: float
    status: str
    year: int


orders = [
    Order(price=50, status="NEW", year=2023),
    Order(price=200, status="PAID", year=2022),
    Order(price=500, status="NEW", year=2019),
]

get_price = lambda o: o.price
get_status = lambda o: o.status
get_year = lambda o: o.year

expensive = attr_spec(get_price, lambda p: p > 100)
is_new = attr_spec(get_status, lambda s: s == "NEW")
recent = attr_spec(get_year, lambda y: y >= 2020)

# Only handle orders that are expensive AND new
cond_order = expensive & is_new & recent

# Transformation: set status to "REVIEW"
set_status = attr_transform(
    getter=get_status,
    setter=dataclass_setter("status"),
    value_func=lambda _: "REVIEW",
)

rule_review = Rule(condition=cond_order, transform=set_status, name="review-rule")

engine = RuleEngine(
    rules=[rule_review],
    keep_unmatched=True,  # Keep unmatched orders unchanged
    match_mode="all",
)

new_orders = engine.process(orders)
print(new_orders)


