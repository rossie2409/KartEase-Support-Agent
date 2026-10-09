

from search_policies import search_policies


def test_return_policy_search():
    result = search_policies("What is the return window for electronics?")

    assert isinstance(result, str)
    assert len(result) > 0
    assert "10 days" in result.lower()


def test_shipping_policy_search():
    result = search_policies("How long does standard shipping take?")

    assert isinstance(result, str)
    assert len(result) > 0
    assert "working days" in result.lower()
