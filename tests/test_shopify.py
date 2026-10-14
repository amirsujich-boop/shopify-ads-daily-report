from adsreport.shopify import _next_link


def test_next_link_parsing():
    h = '<https://x.myshopify.com/admin/api/2024-10/orders.json?page_info=abc&limit=250>; rel="previous", ' \
        '<https://x.myshopify.com/admin/api/2024-10/orders.json?page_info=def&limit=250>; rel="next"'
    assert _next_link(h).endswith("page_info=def&limit=250")
    assert _next_link('<https://x/y>; rel="previous"') is None
    assert _next_link("") is None
