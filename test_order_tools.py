

from order_tools import lookup_order


def test_existing_order():
    result = lookup_order("KE1001")

    assert isinstance(result, dict)
    assert result["order_id"] == "KE1001"
    assert result["status"] == "Delivered"


def test_non_existing_order():
    result = lookup_order("KE9999")

    assert isinstance(result, str)
    assert "No order found" in result


def test_order_id_case_insensitive():
    result = lookup_order("ke1001")

    assert isinstance(result, dict)
    assert result["order_id"] == "KE1001"
