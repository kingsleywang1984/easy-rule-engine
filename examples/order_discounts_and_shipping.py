from easy_rule_engine import Rule, RuleEngine, Specification, attr_spec, attr_transform, dict_setter

# ---------- 1. Sample data: list of orders ----------

orders = [
    {
        "id": 1,
        "user_id": "U1",
        "is_vip": True,
        "total_amount": 250,
        "country": "US",
        "discount_rate": 0.0,
        "shipping_fee": 0.0,
        "tags": [],
    },
    {
        "id": 2,
        "user_id": "U2",
        "is_vip": False,
        "total_amount": 350,
        "country": "US",
        "discount_rate": 0.0,
        "shipping_fee": 0.0,
        "tags": [],
    },
    {
        "id": 3,
        "user_id": "U3",
        "is_vip": False,
        "total_amount": 40,
        "country": "CA",
        "discount_rate": 0.0,
        "shipping_fee": 0.0,
        "tags": [],
    },
    {
        "id": 4,
        "user_id": "U4",
        "is_vip": True,
        "total_amount": 120,
        "country": "FR",
        "discount_rate": 0.0,
        "shipping_fee": 0.0,
        "tags": [],
    },
]


# ---------- 2. Getter functions (avoid Ruff warnings) ----------

def get_is_vip(order: dict) -> bool:
    return order["is_vip"]


def get_total_amount(order: dict) -> float:
    return order["total_amount"]


def get_country(order: dict) -> str:
    return order["country"]


def get_discount_rate(order: dict) -> float:
    return order["discount_rate"]


def get_shipping_fee(order: dict) -> float:
    return order["shipping_fee"]


def get_tags(order: dict) -> list:
    return order["tags"]


# ---------- 3. value_func helpers used by transformations ----------

def set_vip_discount_20(_old: float) -> float:
    return 0.2


def set_normal_discount_10(_old: float) -> float:
    return 0.1


def set_shipping_25(_old: float) -> float:
    return 25.0


def append_low_value_tag(old_tags: list) -> list:
    # Return a new list to avoid mutating the original list
    new_tags = list(old_tags)
    if "low_value" not in new_tags:
        new_tags.append("low_value")
    return new_tags


# ---------- 4. Define Specifications (conditions) ----------

# VIP user
is_vip_spec: Specification[dict] = attr_spec(
    getter=get_is_vip,
    value_predicate=bool,
)

# Non-VIP
not_vip_spec: Specification[dict] = ~is_vip_spec

# Big order (>= 200)
amount_ge_200_spec: Specification[dict] = attr_spec(
    getter=get_total_amount,
    value_predicate=lambda v: v >= 200,
)

# Huge order (>= 300)
amount_ge_300_spec: Specification[dict] = attr_spec(
    getter=get_total_amount,
    value_predicate=lambda v: v >= 300,
)

# Small order (< 50)
amount_lt_50_spec: Specification[dict] = attr_spec(
    getter=get_total_amount,
    value_predicate=lambda v: v < 50,
)

# Overseas order (country != US)
oversea_spec: Specification[dict] = attr_spec(
    getter=get_country,
    value_predicate=lambda c: c != "US",
)

# Combined conditions:
# 1) VIP big order: is_vip AND amount >= 200
vip_big_order_spec = is_vip_spec & amount_ge_200_spec

# 2) Normal huge order: not_vip AND amount >= 300
normal_huge_order_spec = not_vip_spec & amount_ge_300_spec


# ---------- 5. Define Transformers (transformations) ----------

# Set 20% discount
set_discount_20 = attr_transform(
    getter=get_discount_rate,
    setter=dict_setter("discount_rate"),
    value_func=set_vip_discount_20,
)

# Set 10% discount
set_discount_10 = attr_transform(
    getter=get_discount_rate,
    setter=dict_setter("discount_rate"),
    value_func=set_normal_discount_10,
)

# Set shipping fee to 25
set_shipping_25_t = attr_transform(
    getter=get_shipping_fee,
    setter=dict_setter("shipping_fee"),
    value_func=set_shipping_25,
)

# Add "low_value" tag
append_low_value = attr_transform(
    getter=get_tags,
    setter=dict_setter("tags"),
    value_func=append_low_value_tag,
)


# ---------- 6. Define multiple Rules ----------

# Rule 1: VIP big order -> 20% discount
rule_vip_big_discount = Rule(
    condition=vip_big_order_spec,
    transform=set_discount_20,
    name="vip_big_discount",
)

# Rule 2: normal huge order -> 10% discount
rule_normal_huge_discount = Rule(
    condition=normal_huge_order_spec,
    transform=set_discount_10,
    name="normal_huge_discount",
)

# Rule 3: overseas order -> shipping fee 25
rule_oversea_shipping = Rule(
    condition=oversea_spec,
    transform=set_shipping_25_t,
    name="oversea_shipping",
)

# Rule 4: small order -> tags += ['low_value']
rule_low_value_tag = Rule(
    condition=amount_lt_50_spec,
    transform=append_low_value,
    name="low_value_tag",
)

rules = [
    rule_vip_big_discount,
    rule_normal_huge_discount,
    rule_oversea_shipping,
    rule_low_value_tag,
]


# ---------- 7. Build RuleEngine and execute ----------

engine = RuleEngine(
    rules=rules,
    keep_unmatched=True,  # Keep all orders; some may be modified
    match_mode="all",  # Apply all matching rules sequentially
)

new_orders = engine.process(orders)

# ---------- 8. Print results ----------
for o in new_orders:
    print(
        f"id={o['id']}, vip={o['is_vip']}, amount={o['total_amount']}, "
        f"country={o['country']}, discount={o['discount_rate']}, "
        f"shipping={o['shipping_fee']}, tags={o['tags']}"
    )


