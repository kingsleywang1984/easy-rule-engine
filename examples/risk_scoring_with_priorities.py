from easy_rule_engine import Rule, RuleEngine, Specification, attr_spec, attr_transform, dict_setter

# ---------- 1. Sample transaction data ----------

transactions = [
    {
        "id": 1,
        "user_id": "U1",
        "amount": 2000,
        "country": "NG",
        "is_vip": False,
        "has_recent_chargeback": True,
        "is_blacklisted": False,
        "status": "PENDING",
    },
    {
        "id": 2,
        "user_id": "U2",
        "amount": 80,
        "country": "US",
        "is_vip": True,
        "has_recent_chargeback": False,
        "is_blacklisted": False,
        "status": "PENDING",
    },
    {
        "id": 3,
        "user_id": "U3",
        "amount": 700,
        "country": "DE",
        "is_vip": False,
        "has_recent_chargeback": False,
        "is_blacklisted": False,
        "status": "PENDING",
    },
    {
        "id": 4,
        "user_id": "U4",
        "amount": 3000,
        "country": "RU",
        "is_vip": True,
        "has_recent_chargeback": True,
        "is_blacklisted": False,
        "status": "PENDING",
    },
    {
        "id": 5,
        "user_id": "U5",
        "amount": 50,
        "country": "CN",
        "is_vip": False,
        "has_recent_chargeback": False,
        "is_blacklisted": True,  # Blacklist
        "status": "PENDING",
    },
    {
        "id": 6,
        "user_id": "U6",
        "amount": 1500,
        "country": "US",
        "is_vip": False,
        "has_recent_chargeback": True,
        "is_blacklisted": False,
        "status": "PENDING",
    },
]

# ---------- 2. Common getters ----------

get_amount = lambda t: t["amount"]
get_country = lambda t: t["country"]
get_is_vip = lambda t: t["is_vip"]
get_has_recent_chargeback = lambda t: t["has_recent_chargeback"]
get_is_blacklisted = lambda t: t["is_blacklisted"]
get_status = lambda t: t["status"]

# ---------- 3. Build Specifications (conditions) ----------

# Base conditions
high_amount = attr_spec(get_amount, lambda v: v > 1000)
mid_amount = attr_spec(get_amount, lambda v: v > 500)
risky_country = attr_spec(get_country, lambda c: c in {"NG", "RU"})
has_recent_chargeback = attr_spec(get_has_recent_chargeback, bool)
is_vip = attr_spec(get_is_vip, bool)
is_blacklisted = attr_spec(get_is_blacklisted, bool)

# NOT example: not VIP
not_vip = ~is_vip  # Uses the __invert__ operator

# Complex combination 1: HIGH_RISK
# HIGH_RISK = high_amount AND (risky_country OR has_recent_chargeback) AND NOT is_vip
high_risk_condition: Specification[dict] = high_amount & (risky_country | has_recent_chargeback) & not_vip

# Complex combination 2: MID_RISK
# MID_RISK = mid_amount AND NOT is_vip AND NOT HIGH_RISK
# Note the nested NOT(HIGH_RISK):
mid_risk_condition: Specification[dict] = mid_amount & not_vip & ~high_risk_condition

# Complex combination 3: VIP auto-approve
# VIP_APPROVE = is_vip AND NOT is_blacklisted
vip_approve_condition: Specification[dict] = is_vip & ~is_blacklisted

# ---------- 4. Define transformations (set different statuses) ----------

set_blocked = attr_transform(
    getter=get_status,
    setter=dict_setter("status"),
    value_func=lambda _: "BLOCKED",
)

set_high_risk_review = attr_transform(
    getter=get_status,
    setter=dict_setter("status"),
    value_func=lambda _: "REVIEW_HIGH_RISK",
)

set_mid_risk_review = attr_transform(
    getter=get_status,
    setter=dict_setter("status"),
    value_func=lambda _: "MANUAL_REVIEW",
)

set_approved = attr_transform(
    getter=get_status,
    setter=dict_setter("status"),
    value_func=lambda _: "APPROVED",
)

# ---------- 5. Define rules + priority ----------
# Convention: smaller number = higher priority

rules_with_priority = [
    # P0: blacklist (highest priority)
    (
        0,
        Rule(
            condition=is_blacklisted,
            transform=set_blocked,
            name="blacklist-block",
            stop_on_match=True,  # Stop after match
        ),
    ),
    # P1: high risk
    (
        1,
        Rule(
            condition=high_risk_condition,
            transform=set_high_risk_review,
            name="high-risk-review",
            stop_on_match=True,
        ),
    ),
    # P2: medium risk
    (
        2,
        Rule(
            condition=mid_risk_condition,
            transform=set_mid_risk_review,
            name="mid-risk-review",
            stop_on_match=True,
        ),
    ),
    # P3: VIP auto-approve
    (
        3,
        Rule(
            condition=vip_approve_condition,
            transform=set_approved,
            name="vip-approve",
            stop_on_match=True,
        ),
    ),
]

# Sort by priority and pass to RuleEngine
rules_sorted = [r for (_, r) in sorted(rules_with_priority, key=lambda x: x[0])]

engine = RuleEngine(
    rules=rules_sorted,
    keep_unmatched=False,  # Drop transactions that match no rules
    match_mode="first",  # Stop after the first matching rule (plus stop_on_match for safety)
)

# ---------- 6. Execute and print results ----------

new_transactions = engine.process(transactions)
for t in new_transactions:
    print(
        f"id={t['id']}, user={t['user_id']}, amount={t['amount']}, "
        f"country={t['country']}, vip={t['is_vip']}, "
        f"chargeback={t['has_recent_chargeback']}, "
        f"blacklisted={t['is_blacklisted']}, status={t['status']}"
    )


