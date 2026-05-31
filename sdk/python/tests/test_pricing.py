from costpilot.pricing import PRICING, calculate_cost


def test_known_model_cost():
    cost = calculate_cost("gpt-4o", 1_000_000, 1_000_000)
    assert cost == PRICING["gpt-4o"]["input"] + PRICING["gpt-4o"]["output"]


def test_partial_tokens():
    cost = calculate_cost("gpt-4o-mini", 500_000, 250_000)
    expected = 500_000 * 0.15 / 1_000_000 + 250_000 * 0.60 / 1_000_000
    assert cost == expected


def test_unknown_model_is_free():
    assert calculate_cost("some-random-model", 1000, 1000) == 0.0


def test_dated_suffix_matches_prefix():
    # OpenAI ships dated model ids; we should still price them.
    assert calculate_cost("gpt-4o-2024-08-06", 1_000_000, 0) == PRICING["gpt-4o"]["input"]


def test_longest_prefix_wins():
    cost = calculate_cost("gpt-4o-mini-2024-07-18", 1_000_000, 0)
    assert cost == PRICING["gpt-4o-mini"]["input"]


def test_zero_tokens():
    assert calculate_cost("gpt-4o", 0, 0) == 0.0
