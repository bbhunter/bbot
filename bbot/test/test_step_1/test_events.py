import json
import random
import ipaddress

from ..bbot_fixtures import *
from bbot.scanner import Scanner
from bbot.core.helpers.regexes import event_uuid_regex


@pytest.mark.asyncio
async def test_events(events, helpers):
    scan = Scanner()
    await scan._prep()

    assert events.ipv4.type == "IP_ADDRESS"
    assert events.ipv4.netloc == "8.8.8.8"
    assert events.ipv4.port is None
    assert events.ipv6.type == "IP_ADDRESS"
    assert events.ipv6.netloc == "[2001:4860:4860::8888]"
    assert events.ipv6.port is None
    assert events.ipv6_open_port.netloc == "[2001:4860:4860::8888]:443"
    assert events.netv4.type == "IP_RANGE"
    assert events.netv4.netloc is None
    assert "netloc" not in events.netv4.json()
    assert events.netv6.type == "IP_RANGE"
    assert events.domain.type == "DNS_NAME"
    assert events.domain.netloc == "publicapis.org"
    assert events.domain.port is None
    assert "domain" in events.domain.tags
    assert events.subdomain.type == "DNS_NAME"
    assert "subdomain" in events.subdomain.tags
    assert events.open_port.type == "OPEN_TCP_PORT"
    assert events.url_unverified.type == "URL_UNVERIFIED"
    assert events.ipv4_url_unverified.type == "URL_UNVERIFIED"
    assert events.ipv6_url_unverified.type == "URL_UNVERIFIED"
    assert "" not in events.ipv4
    assert None not in events.ipv4
    assert 1 not in events.ipv4
    assert False not in events.ipv4

    # ip tests
    assert events.ipv4 == scan.make_event("8.8.8.8", dummy=True)
    assert "8.8.8.8" in events.ipv4
    assert events.ipv4.host_filterable == "8.8.8.8"
    assert "8.8.8.8" == events.ipv4
    assert "8.8.8.8" in events.netv4
    assert "8.8.8.9" not in events.ipv4
    assert "8.8.9.8" not in events.netv4
    assert "8.8.8.8/31" in events.netv4
    assert "8.8.8.8/30" in events.netv4
    assert "8.8.8.8/29" not in events.netv4
    assert "2001:4860:4860::8888" in events.ipv6
    assert "2001:4860:4860::8888" in events.netv6
    assert "2001:4860:4860::8889" not in events.ipv6
    assert "2002:4860:4860::8888" not in events.netv6
    assert "2001:4860:4860::8888/127" in events.netv6
    assert "2001:4860:4860::8888/126" in events.netv6
    assert "2001:4860:4860::8888/125" not in events.netv6
    assert events.emoji not in events.ipv4
    assert events.emoji not in events.netv6
    assert events.netv6 not in events.emoji
    ipv6_event = scan.make_event(" [DEaD::c0De]:88", "DNS_NAME", dummy=True)
    assert "dead::c0de" == ipv6_event
    assert ipv6_event.host_filterable == "dead::c0de"
    range_to_ip = scan.make_event("1.2.3.4/32", dummy=True)
    assert range_to_ip.type == "IP_ADDRESS"
    range_to_ip = scan.make_event("dead::beef/128", dummy=True)
    assert range_to_ip.type == "IP_ADDRESS"

    # hostname tests
    assert events.domain.host == "publicapis.org"
    assert events.domain.host_filterable == "publicapis.org"
    assert events.subdomain.host == "api.publicapis.org"
    assert events.subdomain.host_filterable == "api.publicapis.org"
    assert events.domain.host_stem == "publicapis"
    assert events.subdomain.host_stem == "api.publicapis"
    assert "api.publicapis.org" in events.domain
    assert "api.publicapis.org" in events.subdomain
    assert "fsocie.ty" not in events.domain
    assert "fsocie.ty" not in events.subdomain
    assert events.subdomain in events.domain
    assert events.domain not in events.subdomain
    assert events.ipv4 not in events.domain
    assert events.netv6 not in events.domain
    assert events.emoji not in events.domain
    assert events.domain not in events.emoji
    open_port_event = scan.make_event(" eViLcorp.COM.:88", "DNS_NAME", dummy=True)
    dns_event = scan.make_event("evilcorp.com.", "DNS_NAME", dummy=True)
    for e in (open_port_event, dns_event):
        assert "evilcorp.com" == e
        assert e.netloc == "evilcorp.com"
        assert e.json()["netloc"] == "evilcorp.com"
        assert e.port is None
        assert "port" not in e.json()

    # url tests
    url_no_trailing_slash = scan.make_event("http://evilcorp.com", dummy=True)
    url_trailing_slash = scan.make_event("http://evilcorp.com/", dummy=True)
    assert url_no_trailing_slash == url_trailing_slash
    assert url_no_trailing_slash.host_filterable == "http://evilcorp.com/"
    assert url_trailing_slash.host_filterable == "http://evilcorp.com/"
    assert events.url_unverified.host == "api.publicapis.org"
    assert events.url_unverified in events.domain
    assert events.url_unverified in events.subdomain
    assert "api.publicapis.org:443" in events.url_unverified
    assert "publicapis.org" not in events.url_unverified
    assert events.ipv4_url_unverified in events.ipv4
    assert events.ipv4_url_unverified.netloc == "8.8.8.8:443"
    assert events.ipv4_url_unverified.port == 443
    assert events.ipv4_url_unverified.json()["port"] == 443
    assert events.ipv4_url_unverified in events.netv4
    assert events.ipv6_url_unverified in events.ipv6
    assert events.ipv6_url_unverified.netloc == "[2001:4860:4860::8888]:443"
    assert events.ipv6_url_unverified.port == 443
    assert events.ipv6_url_unverified.json()["port"] == 443
    assert events.ipv6_url_unverified in events.netv6
    assert events.emoji not in events.url_unverified
    assert events.emoji not in events.ipv6_url_unverified
    assert events.url_unverified not in events.emoji
    assert "https://evilcorp.com" == scan.make_event("https://evilcorp.com:443", dummy=True)
    assert "http://evilcorp.com" == scan.make_event("http://evilcorp.com:80", dummy=True)
    assert "http://evilcorp.com:80/asdf.js" in scan.make_event("http://evilcorp.com/asdf.js", dummy=True)
    assert "http://evilcorp.com/asdf.js" in scan.make_event("http://evilcorp.com:80/asdf.js", dummy=True)
    assert "https://evilcorp.com:443" == scan.make_event("https://evilcorp.com", dummy=True)
    assert "http://evilcorp.com:80" == scan.make_event("http://evilcorp.com", dummy=True)
    assert "https://evilcorp.com:80" == scan.make_event("https://evilcorp.com:80", dummy=True)
    assert "http://evilcorp.com:443" == scan.make_event("http://evilcorp.com:443", dummy=True)
    assert scan.make_event("https://evilcorp.com", dummy=True).with_port().geturl() == "https://evilcorp.com:443/"
    assert scan.make_event("https://evilcorp.com:666", dummy=True).with_port().geturl() == "https://evilcorp.com:666/"
    assert scan.make_event("https://evilcorp.com.:666", dummy=True) == "https://evilcorp.com:666/"
    assert scan.make_event("https://[bad::c0de]", dummy=True).with_port().geturl() == "https://[bad::c0de]:443/"
    assert scan.make_event("https://[bad::c0de]:666", dummy=True).with_port().geturl() == "https://[bad::c0de]:666/"
    url_event = scan.make_event("https://evilcorp.com", "URL", events.ipv4_url, tags=["status-200"])
    assert "status-200" in url_event.tags
    assert url_event.http_status == 200
    with pytest.raises(ValidationError, match=".*status tag.*"):
        scan.make_event("https://evilcorp.com", "URL", events.ipv4_url)

    # http response
    assert events.http_response.host == "example.com"
    assert events.http_response.port == 80
    assert events.http_response.parsed_url.scheme == "http"
    assert events.http_response.with_port().geturl() == "http://example.com:80/"
    assert events.http_response.host_filterable == "http://example.com/"

    http_response = scan.make_event(
        {
            "port": "80",
            "title": "HTTP%20RESPONSE",
            "url": "http://www.evilcorp.com:80",
            "input": "http://www.evilcorp.com:80",
            "raw_header": "HTTP/1.1 301 Moved Permanently\r\nLocation: http://www.evilcorp.com/asdf\r\n\r\n",
            "location": "/asdf",
            "status_code": 301,
        },
        "HTTP_RESPONSE",
        dummy=True,
    )
    assert http_response.http_status == 301
    assert http_response.http_title == "HTTP RESPONSE"
    assert http_response.redirect_location == "http://www.evilcorp.com/asdf"

    # http response url validation
    http_response_2 = scan.make_event(
        {
            "port": "80",
            "url": "http://evilcorp.com:80/asdf",
            "raw_header": "HTTP/1.1 301 Moved Permanently\r\nLocation: http://www.evilcorp.com/asdf\r\n\r\n",
        },
        "HTTP_RESPONSE",
        dummy=True,
    )
    assert http_response_2.data["url"] == "http://evilcorp.com/asdf"

    # open port tests
    assert events.open_port in events.domain
    assert "api.publicapis.org:443" in events.open_port
    assert "bad.publicapis.org:443" not in events.open_port
    assert "publicapis.org:443" not in events.open_port
    assert events.ipv4_open_port in events.ipv4
    assert events.ipv4_open_port in events.netv4
    assert "8.8.8.9" not in events.ipv4_open_port
    assert events.ipv6_open_port in events.ipv6
    assert events.ipv6_open_port in events.netv6
    assert "2002:4860:4860::8888" not in events.ipv6_open_port
    assert events.emoji not in events.ipv6_open_port
    assert events.ipv6_open_port not in events.emoji

    # attribute tests
    assert events.ipv4.host == ipaddress.ip_address("8.8.8.8")
    assert events.ipv4.port is None
    assert events.ipv6.host == ipaddress.ip_address("2001:4860:4860::8888")
    assert events.ipv6.port is None
    assert events.domain.port is None
    assert events.subdomain.port is None
    assert events.open_port.host == "api.publicapis.org"
    assert events.open_port.port == 443
    assert events.ipv4_open_port.host == ipaddress.ip_address("8.8.8.8")
    assert events.ipv4_open_port.port == 443
    assert events.ipv6_open_port.host == ipaddress.ip_address("2001:4860:4860::8888")
    assert events.ipv6_open_port.port == 443
    assert events.url_unverified.host == "api.publicapis.org"
    assert events.url_unverified.port == 443
    assert events.ipv4_url_unverified.host == ipaddress.ip_address("8.8.8.8")
    assert events.ipv4_url_unverified.port == 443
    assert events.ipv6_url_unverified.host == ipaddress.ip_address("2001:4860:4860::8888")
    assert events.ipv6_url_unverified.port == 443

    javascript_event = scan.make_event("http://evilcorp.com/asdf/a.js?b=c#d", "URL_UNVERIFIED", parent=scan.root_event)
    assert "extension-js" in javascript_event.tags
    await scan.ingress_module.handle_event(javascript_event)
    assert "httpx-only" in javascript_event.tags

    # scope distance
    event1 = scan.make_event("1.2.3.4", dummy=True)
    assert event1._scope_distance is None
    event1.scope_distance = 0
    assert event1._scope_distance == 0
    event2 = scan.make_event("2.3.4.5", parent=event1)
    assert event2._scope_distance == 1
    event3 = scan.make_event("3.4.5.6", parent=event2)
    assert event3._scope_distance == 2
    event4 = scan.make_event("3.4.5.6", parent=event3)
    assert event4._scope_distance == 2
    event5 = scan.make_event("4.5.6.7", parent=event4)
    assert event5._scope_distance == 3

    url_1 = scan.make_event("https://127.0.0.1/asdf", "URL_UNVERIFIED", parent=scan.root_event)
    assert url_1.scope_distance == 1
    url_2 = scan.make_event("https://127.0.0.1/test", "URL_UNVERIFIED", parent=url_1)
    assert url_2.scope_distance == 1
    url_3 = scan.make_event("https://127.0.0.2/asdf", "URL_UNVERIFIED", parent=url_1)
    assert url_3.scope_distance == 2

    org_stub_1 = scan.make_event("STUB1", "ORG_STUB", parent=scan.root_event)
    org_stub_1.scope_distance == 1
    assert org_stub_1.netloc is None
    assert "netloc" not in org_stub_1.json()
    org_stub_2 = scan.make_event("STUB2", "ORG_STUB", parent=org_stub_1)
    org_stub_2.scope_distance == 2

    # internal event tracking
    root_event = scan.make_event("0.0.0.0", dummy=True)
    root_event.scope_distance = 0
    internal_event1 = scan.make_event("1.2.3.4", parent=root_event, internal=True)
    assert internal_event1._internal is True
    assert "internal" in internal_event1.tags

    # tag inheritance
    for tag in ("affiliate", "mutation-1"):
        affiliate_event = scan.make_event("1.2.3.4", parent=root_event, tags=tag)
        assert tag in affiliate_event.tags
        affiliate_event2 = scan.make_event("1.2.3.4:88", parent=affiliate_event)
        affiliate_event3 = scan.make_event("4.3.2.1:88", parent=affiliate_event)
        assert tag in affiliate_event2.tags
        assert tag not in affiliate_event3.tags

    # discovery context
    event = scan.make_event(
        "127.0.0.1", parent=scan.root_event, context="something discovered {event.type}: {event.data}"
    )
    assert event.discovery_context == "something discovered IP_ADDRESS: 127.0.0.1"

    # updating an already-created event with make_event()
    # updating tags
    event1 = scan.make_event("127.0.0.1", parent=scan.root_event)
    updated_event = scan.make_event(event1, tags="asdf")
    assert "asdf" not in event1.tags
    assert "asdf" in updated_event.tags
    # updating parent
    event2 = scan.make_event("127.0.0.1", parent=scan.root_event)
    updated_event = scan.make_event(event2, parent=event1)
    assert event2.parent == scan.root_event
    assert updated_event.parent == event1
    # updating module
    event3 = scan.make_event("127.0.0.1", parent=scan.root_event)
    updated_event = scan.make_event(event3, internal=True)
    assert event3.internal is False
    assert updated_event.internal is True

    # event sorting
    parent1 = scan.make_event("127.0.0.1", parent=scan.root_event)
    parent2 = scan.make_event("127.0.0.1", parent=scan.root_event)
    parent2_child1 = scan.make_event("127.0.0.1", parent=parent2)
    parent1_child1 = scan.make_event("127.0.0.1", parent=parent1)
    parent1_child2 = scan.make_event("127.0.0.1", parent=parent1)
    parent1_child2_child1 = scan.make_event("127.0.0.1", parent=parent1_child2)
    parent1_child2_child2 = scan.make_event("127.0.0.1", parent=parent1_child2)
    parent1_child1_child1 = scan.make_event("127.0.0.1", parent=parent1_child1)
    parent2_child2 = scan.make_event("127.0.0.1", parent=parent2)
    parent1_child2_child1_child1 = scan.make_event("127.0.0.1", parent=parent1_child2_child1)

    sortable_events = {
        "parent1": parent1,
        "parent2": parent2,
        "parent2_child1": parent2_child1,
        "parent1_child1": parent1_child1,
        "parent1_child2": parent1_child2,
        "parent1_child2_child1": parent1_child2_child1,
        "parent1_child2_child2": parent1_child2_child2,
        "parent1_child1_child1": parent1_child1_child1,
        "parent2_child2": parent2_child2,
        "parent1_child2_child1_child1": parent1_child2_child1_child1,
    }

    ordered_list = [
        parent1,
        parent1_child1,
        parent1_child1_child1,
        parent1_child2,
        parent1_child2_child1,
        parent1_child2_child1_child1,
        parent1_child2_child2,
        parent2,
        parent2_child1,
        parent2_child2,
    ]

    shuffled_list = list(sortable_events.values())
    random.shuffle(shuffled_list)

    sorted_events = sorted(shuffled_list)
    assert sorted_events == ordered_list

    # test validation
    corrected_event1 = scan.make_event("asdf@asdf.com", "DNS_NAME", dummy=True)
    assert corrected_event1.type == "EMAIL_ADDRESS"
    corrected_event2 = scan.make_event("127.0.0.1", "DNS_NAME", dummy=True)
    assert corrected_event2.type == "IP_ADDRESS"
    corrected_event3 = scan.make_event("wat.asdf.com", "IP_ADDRESS", dummy=True)
    assert corrected_event3.type == "DNS_NAME"

    corrected_event4 = scan.make_event("bob@evilcorp.com", "USERNAME", dummy=True)
    assert corrected_event4.type == "EMAIL_ADDRESS"
    assert "affiliate" in corrected_event4.tags

    test_vuln = scan.make_event(
        {"host": "EVILcorp.com", "severity": "iNfo ", "description": "asdf"}, "VULNERABILITY", dummy=True
    )
    assert test_vuln.data["host"] == "evilcorp.com"
    assert test_vuln.data["severity"] == "INFO"
    test_vuln2 = scan.make_event(
        {"host": "192.168.1.1", "severity": "iNfo ", "description": "asdf"}, "VULNERABILITY", dummy=True
    )
    assert json.loads(test_vuln2.data_human)["severity"] == "INFO"
    assert test_vuln2.host.is_private
    with pytest.raises(ValidationError, match=".*validation error.*\nseverity\n.*Field required.*"):
        test_vuln = scan.make_event({"host": "evilcorp.com", "description": "asdf"}, "VULNERABILITY", dummy=True)
    with pytest.raises(ValidationError, match=".*host.*\n.*Invalid host.*"):
        test_vuln = scan.make_event(
            {"host": "!@#$", "severity": "INFO", "description": "asdf"}, "VULNERABILITY", dummy=True
        )
    with pytest.raises(ValidationError, match=".*severity.*\n.*Invalid severity.*"):
        test_vuln = scan.make_event(
            {"host": "evilcorp.com", "severity": "WACK", "description": "asdf"}, "VULNERABILITY", dummy=True
        )

    # test tagging
    ip_event_1 = scan.make_event("8.8.8.8", dummy=True)
    assert "private-ip" not in ip_event_1.tags
    ip_event_2 = scan.make_event("192.168.0.1", dummy=True)
    assert "private-ip" in ip_event_2.tags
    dns_event_1 = scan.make_event("evilcorp.com", dummy=True)
    assert "domain" in dns_event_1.tags
    dns_event_2 = scan.make_event("www.evilcorp.com", dummy=True)
    assert "subdomain" in dns_event_2.tags

    # punycode - event type detection

    # japanese
    assert scan.make_event("ドメイン.テスト", dummy=True).type == "DNS_NAME"
    assert scan.make_event("bob@ドメイン.テスト", dummy=True).type == "EMAIL_ADDRESS"
    assert scan.make_event("テスト@ドメイン.テスト", dummy=True).type == "EMAIL_ADDRESS"
    assert scan.make_event("ドメイン.テスト:80", dummy=True).type == "OPEN_TCP_PORT"
    assert scan.make_event("http://ドメイン.テスト:80", dummy=True).type == "URL_UNVERIFIED"
    assert scan.make_event("http://ドメイン.テスト:80/テスト", dummy=True).type == "URL_UNVERIFIED"

    assert scan.make_event("xn--eckwd4c7c.xn--zckzah", dummy=True).type == "DNS_NAME"
    assert scan.make_event("bob@xn--eckwd4c7c.xn--zckzah", dummy=True).type == "EMAIL_ADDRESS"
    assert scan.make_event("テスト@xn--eckwd4c7c.xn--zckzah", dummy=True).type == "EMAIL_ADDRESS"
    assert scan.make_event("xn--eckwd4c7c.xn--zckzah:80", dummy=True).type == "OPEN_TCP_PORT"
    assert scan.make_event("http://xn--eckwd4c7c.xn--zckzah:80", dummy=True).type == "URL_UNVERIFIED"
    assert scan.make_event("http://xn--eckwd4c7c.xn--zckzah:80/テスト", dummy=True).type == "URL_UNVERIFIED"

    # thai
    assert scan.make_event("เราเที่ยวด้วยกัน.com", dummy=True).type == "DNS_NAME"
    assert scan.make_event("bob@เราเที่ยวด้วยกัน.com", dummy=True).type == "EMAIL_ADDRESS"
    assert scan.make_event("ทดสอบ@เราเที่ยวด้วยกัน.com", dummy=True).type == "EMAIL_ADDRESS"
    assert scan.make_event("เราเที่ยวด้วยกัน.com:80", dummy=True).type == "OPEN_TCP_PORT"
    assert scan.make_event("http://เราเที่ยวด้วยกัน.com:80", dummy=True).type == "URL_UNVERIFIED"
    assert scan.make_event("http://เราเที่ยวด้วยกัน.com:80/ทดสอบ", dummy=True).type == "URL_UNVERIFIED"

    assert scan.make_event("xn--12c1bik6bbd8ab6hd1b5jc6jta.com", dummy=True).type == "DNS_NAME"
    assert scan.make_event("bob@xn--12c1bik6bbd8ab6hd1b5jc6jta.com", dummy=True).type == "EMAIL_ADDRESS"
    assert scan.make_event("ทดสอบ@xn--12c1bik6bbd8ab6hd1b5jc6jta.com", dummy=True).type == "EMAIL_ADDRESS"
    assert scan.make_event("xn--12c1bik6bbd8ab6hd1b5jc6jta.com:80", dummy=True).type == "OPEN_TCP_PORT"
    assert scan.make_event("http://xn--12c1bik6bbd8ab6hd1b5jc6jta.com:80", dummy=True).type == "URL_UNVERIFIED"
    assert scan.make_event("http://xn--12c1bik6bbd8ab6hd1b5jc6jta.com:80/ทดสอบ", dummy=True).type == "URL_UNVERIFIED"

    # punycode - encoding / decoding tests

    # japanese
    assert scan.make_event("xn--eckwd4c7c.xn--zckzah", dummy=True).data == "xn--eckwd4c7c.xn--zckzah"
    assert scan.make_event("bob@xn--eckwd4c7c.xn--zckzah", dummy=True).data == "bob@xn--eckwd4c7c.xn--zckzah"
    assert scan.make_event("テスト@xn--eckwd4c7c.xn--zckzah", dummy=True).data == "テスト@xn--eckwd4c7c.xn--zckzah"
    assert scan.make_event("xn--eckwd4c7c.xn--zckzah:80", dummy=True).data == "xn--eckwd4c7c.xn--zckzah:80"
    assert scan.make_event("http://xn--eckwd4c7c.xn--zckzah:80", dummy=True).data == "http://xn--eckwd4c7c.xn--zckzah/"
    assert (
        scan.make_event("http://xn--eckwd4c7c.xn--zckzah:80/テスト", dummy=True).data
        == "http://xn--eckwd4c7c.xn--zckzah/テスト"
    )

    assert scan.make_event("ドメイン.テスト", dummy=True).data == "xn--eckwd4c7c.xn--zckzah"
    assert scan.make_event("bob@ドメイン.テスト", dummy=True).data == "bob@xn--eckwd4c7c.xn--zckzah"
    assert scan.make_event("テスト@ドメイン.テスト", dummy=True).data == "テスト@xn--eckwd4c7c.xn--zckzah"
    assert scan.make_event("ドメイン.テスト:80", dummy=True).data == "xn--eckwd4c7c.xn--zckzah:80"
    assert scan.make_event("http://ドメイン.テスト:80", dummy=True).data == "http://xn--eckwd4c7c.xn--zckzah/"
    assert (
        scan.make_event("http://ドメイン.テスト:80/テスト", dummy=True).data
        == "http://xn--eckwd4c7c.xn--zckzah/テスト"
    )
    # thai
    assert (
        scan.make_event("xn--12c1bik6bbd8ab6hd1b5jc6jta.com", dummy=True).data == "xn--12c1bik6bbd8ab6hd1b5jc6jta.com"
    )
    assert (
        scan.make_event("bob@xn--12c1bik6bbd8ab6hd1b5jc6jta.com", dummy=True).data
        == "bob@xn--12c1bik6bbd8ab6hd1b5jc6jta.com"
    )
    assert (
        scan.make_event("ทดสอบ@xn--12c1bik6bbd8ab6hd1b5jc6jta.com", dummy=True).data
        == "ทดสอบ@xn--12c1bik6bbd8ab6hd1b5jc6jta.com"
    )
    assert (
        scan.make_event("xn--12c1bik6bbd8ab6hd1b5jc6jta.com:80", dummy=True).data
        == "xn--12c1bik6bbd8ab6hd1b5jc6jta.com:80"
    )
    assert (
        scan.make_event("http://xn--12c1bik6bbd8ab6hd1b5jc6jta.com:80", dummy=True).data
        == "http://xn--12c1bik6bbd8ab6hd1b5jc6jta.com/"
    )
    assert (
        scan.make_event("http://xn--12c1bik6bbd8ab6hd1b5jc6jta.com:80/ทดสอบ", dummy=True).data
        == "http://xn--12c1bik6bbd8ab6hd1b5jc6jta.com/ทดสอบ"
    )

    assert scan.make_event("เราเที่ยวด้วยกัน.com", dummy=True).data == "xn--12c1bik6bbd8ab6hd1b5jc6jta.com"
    assert scan.make_event("bob@เราเที่ยวด้วยกัน.com", dummy=True).data == "bob@xn--12c1bik6bbd8ab6hd1b5jc6jta.com"
    assert scan.make_event("ทดสอบ@เราเที่ยวด้วยกัน.com", dummy=True).data == "ทดสอบ@xn--12c1bik6bbd8ab6hd1b5jc6jta.com"
    assert scan.make_event("เราเที่ยวด้วยกัน.com:80", dummy=True).data == "xn--12c1bik6bbd8ab6hd1b5jc6jta.com:80"
    assert (
        scan.make_event("http://เราเที่ยวด้วยกัน.com:80", dummy=True).data == "http://xn--12c1bik6bbd8ab6hd1b5jc6jta.com/"
    )
    assert (
        scan.make_event("http://เราเที่ยวด้วยกัน.com:80/ทดสอบ", dummy=True).data
        == "http://xn--12c1bik6bbd8ab6hd1b5jc6jta.com/ทดสอบ"
    )

    # test event uuid
    import uuid

    parent_event1 = scan.make_event("evilcorp.com", parent=scan.root_event, context="test context")
    parent_event2 = scan.make_event("evilcorp.com", parent=scan.root_event, context="test context")

    event1 = scan.make_event("evilcorp.com:80", parent=parent_event1, context="test context")
    assert hasattr(event1, "_uuid")
    assert hasattr(event1, "uuid")
    assert isinstance(event1._uuid, uuid.UUID)
    assert isinstance(event1.uuid, str)
    assert event1.uuid == f"{event1.type}:{event1._uuid}"
    event2 = scan.make_event("evilcorp.com:80", parent=parent_event2, context="test context")
    assert hasattr(event2, "_uuid")
    assert hasattr(event2, "uuid")
    assert isinstance(event2._uuid, uuid.UUID)
    assert isinstance(event2.uuid, str)
    assert event2.uuid == f"{event2.type}:{event2._uuid}"
    # ids should match because the event type + data is the same
    assert event1.id == event2.id
    # but uuids should be unique!
    assert event1.uuid != event2.uuid
    # parent ids should match
    assert event1.parent_id == event2.parent_id == parent_event1.id == parent_event2.id
    # uuids should not
    assert event1.parent_uuid == parent_event1.uuid
    assert event2.parent_uuid == parent_event2.uuid
    assert event1.parent_uuid != event2.parent_uuid

    # test event serialization
    from bbot.core.event import event_from_json

    db_event = scan.make_event("evilcorp.com:80", parent=scan.root_event, context="test context")
    assert db_event.parent == scan.root_event
    assert db_event.parent is scan.root_event
    db_event._resolved_hosts = {"127.0.0.1"}
    db_event.scope_distance = 1
    assert db_event.discovery_context == "test context"
    assert db_event.discovery_path == ["test context"]
    assert len(db_event.parent_chain) == 1
    assert all(event_uuid_regex.match(u) for u in db_event.parent_chain)
    assert db_event.parent_chain[0] == str(db_event.uuid)
    assert db_event.parent.uuid == scan.root_event.uuid
    assert db_event.parent_uuid == scan.root_event.uuid
    timestamp = db_event.timestamp.isoformat()
    json_event = db_event.json()
    assert isinstance(json_event["uuid"], str)
    assert json_event["uuid"] == str(db_event.uuid)
    assert json_event["parent_uuid"] == str(scan.root_event.uuid)
    assert json_event["scope_distance"] == 1
    assert json_event["data"] == "evilcorp.com:80"
    assert json_event["type"] == "OPEN_TCP_PORT"
    assert json_event["host"] == "evilcorp.com"
    assert json_event["timestamp"] == timestamp
    assert json_event["discovery_context"] == "test context"
    assert json_event["discovery_path"] == ["test context"]
    assert json_event["parent_chain"] == db_event.parent_chain
    assert json_event["parent_chain"][0] == str(db_event.uuid)
    reconstituted_event = event_from_json(json_event)
    assert isinstance(reconstituted_event._uuid, uuid.UUID)
    assert str(reconstituted_event.uuid) == json_event["uuid"]
    assert str(reconstituted_event.parent_uuid) == json_event["parent_uuid"]
    assert reconstituted_event.uuid == db_event.uuid
    assert reconstituted_event.parent_uuid == scan.root_event.uuid
    assert reconstituted_event.scope_distance == 1
    assert reconstituted_event.timestamp.isoformat() == timestamp
    assert reconstituted_event.data == "evilcorp.com:80"
    assert reconstituted_event.type == "OPEN_TCP_PORT"
    assert reconstituted_event.host == "evilcorp.com"
    assert reconstituted_event.discovery_context == "test context"
    assert reconstituted_event.discovery_path == ["test context"]
    assert reconstituted_event.parent_chain == db_event.parent_chain
    assert "127.0.0.1" in reconstituted_event.resolved_hosts
    hostless_event = scan.make_event("asdf", "ASDF", dummy=True)
    hostless_event_json = hostless_event.json()
    assert hostless_event_json["type"] == "ASDF"
    assert hostless_event_json["data"] == "asdf"
    assert "host" not in hostless_event_json

    # SIEM-friendly serialize/deserialize
    json_event_siemfriendly = db_event.json(siem_friendly=True)
    assert json_event_siemfriendly["scope_distance"] == 1
    assert json_event_siemfriendly["data"] == {"OPEN_TCP_PORT": "evilcorp.com:80"}
    assert json_event_siemfriendly["type"] == "OPEN_TCP_PORT"
    assert json_event_siemfriendly["host"] == "evilcorp.com"
    assert json_event_siemfriendly["timestamp"] == timestamp
    reconstituted_event2 = event_from_json(json_event_siemfriendly, siem_friendly=True)
    assert reconstituted_event2.scope_distance == 1
    assert reconstituted_event2.timestamp.isoformat() == timestamp
    assert reconstituted_event2.data == "evilcorp.com:80"
    assert reconstituted_event2.type == "OPEN_TCP_PORT"
    assert reconstituted_event2.host == "evilcorp.com"
    assert "127.0.0.1" in reconstituted_event2.resolved_hosts

    http_response = scan.make_event(httpx_response, "HTTP_RESPONSE", parent=scan.root_event)
    assert http_response.parent_id == scan.root_event.id
    assert http_response.data["input"] == "http://example.com:80"
    assert (
        http_response.raw_response
        == 'HTTP/1.1 200 OK\r\nConnection: close\r\nAge: 526111\r\nCache-Control: max-age=604800\r\nContent-Type: text/html; charset=UTF-8\r\nDate: Mon, 14 Nov 2022 17:14:27 GMT\r\nEtag: "3147526947+ident+gzip"\r\nExpires: Mon, 21 Nov 2022 17:14:27 GMT\r\nLast-Modified: Thu, 17 Oct 2019 07:18:26 GMT\r\nServer: ECS (agb/A445)\r\nVary: Accept-Encoding\r\nX-Cache: HIT\r\n\r\n<!doctype html>\n<html>\n<head>\n    <title>Example Domain</title>\n\n    <meta charset="utf-8" />\n    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1" />\n    <style type="text/css">\n    body {\n        background-color: #f0f0f2;\n        margin: 0;\n        padding: 0;\n        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;\n        \n    }\n    div {\n        width: 600px;\n        margin: 5em auto;\n        padding: 2em;\n        background-color: #fdfdff;\n        border-radius: 0.5em;\n        box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);\n    }\n    a:link, a:visited {\n        color: #38488f;\n        text-decoration: none;\n    }\n    @media (max-width: 700px) {\n        div {\n            margin: 0 auto;\n            width: auto;\n        }\n    }\n    </style>    \n</head>\n\n<body>\n<div>\n    <h1>Example Domain</h1>\n    <p>This domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.</p>\n    <p><a href="https://www.iana.org/domains/example">More information...</a></p>\n</div>\n</body>\n</html>\n'
    )
    json_event = http_response.json(mode="graph")
    assert isinstance(json_event["data"], str)
    json_event = http_response.json()
    assert isinstance(json_event["data"], dict)
    assert json_event["type"] == "HTTP_RESPONSE"
    assert json_event["host"] == "example.com"
    assert json_event["parent"] == scan.root_event.id
    reconstituted_event = event_from_json(json_event)
    assert isinstance(reconstituted_event.data, dict)
    assert reconstituted_event.data["input"] == "http://example.com:80"
    assert reconstituted_event.host == "example.com"
    assert reconstituted_event.type == "HTTP_RESPONSE"
    assert reconstituted_event.parent_id == scan.root_event.id

    event_1 = scan.make_event("127.0.0.1", parent=scan.root_event)
    event_2 = scan.make_event("127.0.0.2", parent=event_1)
    event_3 = scan.make_event("127.0.0.3", parent=event_2)
    event_3._omit = True
    event_4 = scan.make_event("127.0.0.4", parent=event_3)
    event_5 = scan.make_event("127.0.0.5", parent=event_4)
    assert event_5.get_parents() == [event_4, event_3, event_2, event_1, scan.root_event]
    assert event_5.get_parents(omit=True) == [event_4, event_2, event_1, scan.root_event]
    assert event_5.get_parents(include_self=True) == [event_5, event_4, event_3, event_2, event_1, scan.root_event]

    # test host backup
    host_event = scan.make_event("asdf.evilcorp.com", "DNS_NAME", parent=scan.root_event)
    assert host_event.host_original == "asdf.evilcorp.com"
    host_event.host = "_wildcard.evilcorp.com"
    assert host_event.host == "_wildcard.evilcorp.com"
    assert host_event.host_original == "asdf.evilcorp.com"

    # test storage bucket validation
    bucket_event = scan.make_event(
        {"name": "ASDF.s3.amazonaws.com", "url": "https://ASDF.s3.amazonaws.com"},
        "STORAGE_BUCKET",
        parent=scan.root_event,
    )
    assert bucket_event.data["name"] == "asdf.s3.amazonaws.com"
    assert bucket_event.data["url"] == "https://asdf.s3.amazonaws.com/"

    # test module sequence
    module = scan._make_dummy_module("mymodule")
    parent_event_1 = scan.make_event("127.0.0.1", module=module, parent=scan.root_event)
    assert str(parent_event_1.module) == "mymodule"
    assert str(parent_event_1.module_sequence) == "mymodule"
    parent_event_2 = scan.make_event("127.0.0.2", module=module, parent=parent_event_1)
    assert str(parent_event_2.module) == "mymodule"
    assert str(parent_event_2.module_sequence) == "mymodule"
    parent_event_3 = scan.make_event("127.0.0.3", module=module, parent=parent_event_2)
    assert str(parent_event_3.module) == "mymodule"
    assert str(parent_event_3.module_sequence) == "mymodule"

    module = scan._make_dummy_module("mymodule")
    parent_event_1 = scan.make_event("127.0.0.1", module=module, parent=scan.root_event)
    parent_event_1._omit = True
    assert str(parent_event_1.module) == "mymodule"
    assert str(parent_event_1.module_sequence) == "mymodule"
    parent_event_2 = scan.make_event("127.0.0.2", module=module, parent=parent_event_1)
    parent_event_2._omit = True
    assert str(parent_event_2.module) == "mymodule"
    assert str(parent_event_2.module_sequence) == "mymodule->mymodule"
    parent_event_3 = scan.make_event("127.0.0.3", module=module, parent=parent_event_2)
    assert str(parent_event_3.module) == "mymodule"
    assert str(parent_event_3.module_sequence) == "mymodule->mymodule->mymodule"

    # event with no data
    with pytest.raises(ValidationError):
        event = scan.make_event(None, "DNS_NAME", parent=scan.root_event)

    await scan._cleanup()


@pytest.mark.asyncio
async def test_event_discovery_context():
    from bbot.modules.base import BaseModule

    scan = Scanner("evilcorp.com")
    await scan.helpers.dns._mock_dns(
        {
            "evilcorp.com": {"A": ["1.2.3.4"]},
            "one.evilcorp.com": {"A": ["1.2.3.4"]},
            "two.evilcorp.com": {"A": ["1.2.3.4"]},
            "three.evilcorp.com": {"A": ["1.2.3.4"]},
            "four.evilcorp.com": {"A": ["1.2.3.4"]},
        }
    )
    await scan._prep()

    dummy_module_1 = scan._make_dummy_module("module_1")
    dummy_module_2 = scan._make_dummy_module("module_2")

    class DummyModule(BaseModule):
        watched_events = ["DNS_NAME"]
        _name = "dummy_module"

        async def handle_event(self, event):
            new_event = None
            if event.data == "evilcorp.com":
                new_event = scan.make_event(
                    "one.evilcorp.com",
                    "DNS_NAME",
                    event,
                    context="{module} invoked forbidden magick to discover {event.type} {event.data}",
                    module=dummy_module_1,
                )
            elif event.data == "one.evilcorp.com":
                new_event = scan.make_event(
                    "two.evilcorp.com",
                    "DNS_NAME",
                    event,
                    context="{module} pledged its allegiance to cthulu and was awarded {event.type} {event.data}",
                    module=dummy_module_1,
                )
            elif event.data == "two.evilcorp.com":
                new_event = scan.make_event(
                    "three.evilcorp.com",
                    "DNS_NAME",
                    event,
                    context="{module} asked nicely and was given {event.type} {event.data}",
                    module=dummy_module_2,
                )
            elif event.data == "three.evilcorp.com":
                new_event = scan.make_event(
                    "four.evilcorp.com",
                    "DNS_NAME",
                    event,
                    context="{module} used brute force to obtain {event.type} {event.data}",
                    module=dummy_module_2,
                )
            if new_event is not None:
                await self.emit_event(new_event)

    dummy_module = DummyModule(scan)

    scan.modules["dummy_module"] = dummy_module

    # test discovery context
    test_event = dummy_module.make_event("evilcorp.com", "DNS_NAME", parent=scan.root_event)
    assert test_event.discovery_context == "dummy_module discovered DNS_NAME: evilcorp.com"

    test_event2 = dummy_module.make_event(
        "evilcorp.com", "DNS_NAME", parent=scan.root_event, context="{module} {found} {event.host}"
    )
    assert test_event2.discovery_context == "dummy_module {found} evilcorp.com"
    # jank input
    test_event3 = dummy_module.make_event(
        "http://evilcorp.com/{http://evilcorp.org!@#%@#$:,,,}", "URL_UNVERIFIED", parent=scan.root_event
    )
    assert (
        test_event3.discovery_context
        == "dummy_module discovered URL_UNVERIFIED: http://evilcorp.com/{http:/evilcorp.org!@"
    )

    events = [e async for e in scan.async_start()]
    assert len(events) == 7

    assert 1 == len(
        [
            e
            for e in events
            if e.type == "DNS_NAME"
            and e.data == "evilcorp.com"
            and e.discovery_context == f"Scan {scan.name} seeded with DNS_NAME: evilcorp.com"
            and e.discovery_path == [f"Scan {scan.name} seeded with DNS_NAME: evilcorp.com"]
        ]
    )
    assert 1 == len(
        [
            e
            for e in events
            if e.type == "DNS_NAME"
            and e.data == "one.evilcorp.com"
            and e.discovery_context == "module_1 invoked forbidden magick to discover DNS_NAME one.evilcorp.com"
            and e.discovery_path
            == [
                f"Scan {scan.name} seeded with DNS_NAME: evilcorp.com",
                "module_1 invoked forbidden magick to discover DNS_NAME one.evilcorp.com",
            ]
        ]
    )
    assert 1 == len(
        [
            e
            for e in events
            if e.type == "DNS_NAME"
            and e.data == "two.evilcorp.com"
            and e.discovery_context
            == "module_1 pledged its allegiance to cthulu and was awarded DNS_NAME two.evilcorp.com"
            and e.discovery_path
            == [
                f"Scan {scan.name} seeded with DNS_NAME: evilcorp.com",
                "module_1 invoked forbidden magick to discover DNS_NAME one.evilcorp.com",
                "module_1 pledged its allegiance to cthulu and was awarded DNS_NAME two.evilcorp.com",
            ]
        ]
    )
    assert 1 == len(
        [
            e
            for e in events
            if e.type == "DNS_NAME"
            and e.data == "three.evilcorp.com"
            and e.discovery_context == "module_2 asked nicely and was given DNS_NAME three.evilcorp.com"
            and e.discovery_path
            == [
                f"Scan {scan.name} seeded with DNS_NAME: evilcorp.com",
                "module_1 invoked forbidden magick to discover DNS_NAME one.evilcorp.com",
                "module_1 pledged its allegiance to cthulu and was awarded DNS_NAME two.evilcorp.com",
                "module_2 asked nicely and was given DNS_NAME three.evilcorp.com",
            ]
        ]
    )
    final_path = [
        f"Scan {scan.name} seeded with DNS_NAME: evilcorp.com",
        "module_1 invoked forbidden magick to discover DNS_NAME one.evilcorp.com",
        "module_1 pledged its allegiance to cthulu and was awarded DNS_NAME two.evilcorp.com",
        "module_2 asked nicely and was given DNS_NAME three.evilcorp.com",
        "module_2 used brute force to obtain DNS_NAME four.evilcorp.com",
    ]
    final_event = [
        e
        for e in events
        if e.type == "DNS_NAME"
        and e.data == "four.evilcorp.com"
        and e.discovery_context == "module_2 used brute force to obtain DNS_NAME four.evilcorp.com"
        and e.discovery_path == final_path
    ]
    assert 1 == len(final_event)
    j = final_event[0].json()
    assert j["discovery_path"] == final_path

    await scan._cleanup()

    # test to make sure this doesn't come back
    #  https://github.com/blacklanternsecurity/bbot/issues/1498
    scan = Scanner("http://blacklanternsecurity.com", config={"dns": {"minimal": False}})
    await scan.helpers.dns._mock_dns(
        {"blacklanternsecurity.com": {"TXT": ["blsops.com"], "A": ["127.0.0.1"]}, "blsops.com": {"A": ["127.0.0.1"]}}
    )
    events = [e async for e in scan.async_start()]
    blsops_event = [e for e in events if e.type == "DNS_NAME" and e.data == "blsops.com"]
    assert len(blsops_event) == 1
    assert blsops_event[0].discovery_path[1] == "URL_UNVERIFIED has host DNS_NAME: blacklanternsecurity.com"

    await scan._cleanup()


@pytest.mark.asyncio
async def test_event_web_spider_distance(bbot_scanner):
    # make sure web spider distance inheritance works as intended
    # and we don't have any runaway situations with SOCIAL events + URLs

    # URL_UNVERIFIED events should not increment web spider distance
    scan = bbot_scanner(config={"web": {"spider_distance": 1}})
    url_event_1 = scan.make_event("http://www.evilcorp.com/test1", "URL_UNVERIFIED", parent=scan.root_event)
    assert url_event_1.web_spider_distance == 0
    url_event_2 = scan.make_event("http://www.evilcorp.com/test2", "URL_UNVERIFIED", parent=url_event_1)
    assert url_event_2.web_spider_distance == 0
    url_event_3 = scan.make_event(
        "http://www.evilcorp.com/test3", "URL_UNVERIFIED", parent=url_event_2, tags=["spider-danger"]
    )
    assert url_event_3.web_spider_distance == 0
    assert "spider-danger" in url_event_3.tags
    assert "spider-max" not in url_event_3.tags

    # URL events should increment web spider distance
    scan = bbot_scanner(config={"web": {"spider_distance": 1}})
    url_event_1 = scan.make_event("http://www.evilcorp.com/test1", "URL", parent=scan.root_event, tags="status-200")
    assert url_event_1.web_spider_distance == 0
    url_event_2 = scan.make_event("http://www.evilcorp.com/test2", "URL", parent=url_event_1, tags="status-200")
    assert url_event_2.web_spider_distance == 0
    url_event_3 = scan.make_event(
        "http://www.evilcorp.com/test3", "URL_UNVERIFIED", parent=url_event_2, tags=["spider-danger"]
    )
    assert url_event_3.web_spider_distance == 1
    assert "spider-danger" in url_event_3.tags
    assert "spider-max" not in url_event_3.tags

    # SOCIAL events should inherit spider distance
    social_event = scan.make_event(
        {"platform": "github", "url": "http://www.evilcorp.com/test4"}, "SOCIAL", parent=url_event_3
    )
    assert social_event.web_spider_distance == 1
    assert "spider-danger" in social_event.tags
    url_event_4 = scan.make_event("http://www.evilcorp.com/test4", "URL_UNVERIFIED", parent=social_event)
    assert url_event_4.web_spider_distance == 2
    assert "spider-danger" in url_event_4.tags
    assert "spider-max" in url_event_4.tags
    social_event_2 = scan.make_event(
        {"platform": "github", "url": "http://www.evilcorp.com/test5"}, "SOCIAL", parent=url_event_4
    )
    assert social_event_2.web_spider_distance == 2
    assert "spider-danger" in social_event_2.tags
    assert "spider-max" in social_event_2.tags
    url_event_5 = scan.make_event("http://www.evilcorp.com/test5", "URL_UNVERIFIED", parent=social_event_2)
    assert url_event_5.web_spider_distance == 3
    assert "spider-danger" in url_event_5.tags
    assert "spider-max" in url_event_5.tags

    url_event = scan.make_event("http://www.evilcorp.com", "URL_UNVERIFIED", parent=scan.root_event)
    assert url_event.web_spider_distance == 0
    assert "spider-danger" not in url_event.tags
    assert "spider-max" not in url_event.tags
    url_event_2 = scan.make_event(
        "http://www.evilcorp.com", "URL_UNVERIFIED", parent=scan.root_event, tags="spider-danger"
    )
    url_event_2b = scan.make_event("http://www.evilcorp.com", "URL", parent=url_event_2, tags="status-200")
    assert url_event_2b.web_spider_distance == 0
    assert "spider-danger" in url_event_2b.tags
    assert "spider-max" not in url_event_2b.tags
    url_event_3 = scan.make_event(
        "http://www.evilcorp.com/3", "URL_UNVERIFIED", parent=url_event_2b, tags="spider-danger"
    )
    assert url_event_3.web_spider_distance == 1
    assert "spider-danger" in url_event_3.tags
    assert "spider-max" not in url_event_3.tags
    url_event_4 = scan.make_event("http://evilcorp.com", "URL", parent=url_event_3, tags="status-200")
    assert url_event_4.web_spider_distance == 0
    assert "spider-danger" not in url_event_4.tags
    assert "spider-max" not in url_event_4.tags
    url_event_4.add_tag("spider-danger")
    assert url_event_4.web_spider_distance == 0
    assert "spider-danger" in url_event_4.tags
    assert "spider-max" not in url_event_4.tags
    url_event_4.remove_tag("spider-danger")
    assert url_event_4.web_spider_distance == 0
    assert "spider-danger" not in url_event_4.tags
    assert "spider-max" not in url_event_4.tags
    url_event_5 = scan.make_event("http://evilcorp.com/5", "URL_UNVERIFIED", parent=url_event_4)
    assert url_event_5.web_spider_distance == 0
    assert "spider-danger" not in url_event_5.tags
    assert "spider-max" not in url_event_5.tags
    url_event_5.add_tag("spider-danger")
    # if host is the same as parent, web spider distance should auto-increment after adding spider-danger tag
    assert url_event_5.web_spider_distance == 1
    assert "spider-danger" in url_event_5.tags
    assert "spider-max" not in url_event_5.tags


def test_event_confidence():
    scan = Scanner()
    # default 100
    event1 = scan.make_event("evilcorp.com", "DNS_NAME", dummy=True)
    assert event1.confidence == 100
    assert event1.cumulative_confidence == 100
    # custom confidence
    event2 = scan.make_event("evilcorp.com", "DNS_NAME", confidence=90, dummy=True)
    assert event2.confidence == 90
    assert event2.cumulative_confidence == 90
    # max 100
    event3 = scan.make_event("evilcorp.com", "DNS_NAME", confidence=999, dummy=True)
    assert event3.confidence == 100
    assert event3.cumulative_confidence == 100
    # min 1
    event4 = scan.make_event("evilcorp.com", "DNS_NAME", confidence=0, dummy=True)
    assert event4.confidence == 1
    assert event4.cumulative_confidence == 1
    # first event in chain
    event5 = scan.make_event("evilcorp.com", "DNS_NAME", confidence=90, parent=scan.root_event)
    assert event5.confidence == 90
    assert event5.cumulative_confidence == 90
    # compounding confidence
    event6 = scan.make_event("evilcorp.com", "DNS_NAME", confidence=50, parent=event5)
    assert event6.confidence == 50
    assert event6.cumulative_confidence == 45
    event7 = scan.make_event("evilcorp.com", "DNS_NAME", confidence=50, parent=event6)
    assert event7.confidence == 50
    assert event7.cumulative_confidence == 22
    # 100 confidence resets
    event8 = scan.make_event("evilcorp.com", "DNS_NAME", confidence=100, parent=event7)
    assert event8.confidence == 100
    assert event8.cumulative_confidence == 100


def test_event_closest_host():
    scan = Scanner()
    # first event has a host
    event1 = scan.make_event("evilcorp.com", "DNS_NAME", parent=scan.root_event)
    assert event1.host == "evilcorp.com"
    # second event has a host + url
    event2 = scan.make_event(
        {
            "method": "GET",
            "url": "http://www.evilcorp.com/asdf",
            "hash": {"header_mmh3": "1", "body_mmh3": "2"},
            "raw_header": "HTTP/1.1 301 Moved Permanently\r\nLocation: http://www.evilcorp.com/asdf\r\n\r\n",
        },
        "HTTP_RESPONSE",
        parent=event1,
    )
    assert event2.host == "www.evilcorp.com"
    # third event has a path
    event3 = scan.make_event({"path": "/tmp/asdf.txt"}, "FILESYSTEM", parent=event2)
    assert not event3.host
    # finding automatically uses the host from the second event
    finding = scan.make_event({"description": "test"}, "FINDING", parent=event3)
    assert finding.data["host"] == "www.evilcorp.com"
    assert finding.data["url"] == "http://www.evilcorp.com/asdf"
    assert finding.data["path"] == "/tmp/asdf.txt"
    assert finding.host == "www.evilcorp.com"
    # same with vuln
    vuln = scan.make_event({"description": "test", "severity": "HIGH"}, "VULNERABILITY", parent=event3)
    assert vuln.data["host"] == "www.evilcorp.com"
    assert vuln.data["url"] == "http://www.evilcorp.com/asdf"
    assert vuln.data["path"] == "/tmp/asdf.txt"
    assert vuln.host == "www.evilcorp.com"

    # no host and no path == not allowed
    event3 = scan.make_event("wat", "ASDF", parent=scan.root_event)
    assert not event3.host
    with pytest.raises(ValueError):
        finding = scan.make_event({"description": "test"}, "FINDING", parent=event3)
    finding = scan.make_event({"path": "/tmp/asdf.txt", "description": "test"}, "FINDING", parent=event3)
    assert finding is not None
    finding = scan.make_event({"host": "evilcorp.com", "description": "test"}, "FINDING", parent=event3)
    assert finding is not None
    with pytest.raises(ValueError):
        vuln = scan.make_event({"description": "test", "severity": "HIGH"}, "VULNERABILITY", parent=event3)
    vuln = scan.make_event(
        {"path": "/tmp/asdf.txt", "description": "test", "severity": "HIGH"}, "VULNERABILITY", parent=event3
    )
    assert vuln is not None
    vuln = scan.make_event(
        {"host": "evilcorp.com", "description": "test", "severity": "HIGH"}, "VULNERABILITY", parent=event3
    )
    assert vuln is not None


def test_event_magic():
    from bbot.core.helpers.libmagic import get_magic_info, get_compression

    import base64

    zip_base64 = "UEsDBAoDAAAAAOMmZ1lR4FaHBQAAAAUAAAAIAAAAYXNkZi50eHRhc2RmClBLAQI/AwoDAAAAAOMmZ1lR4FaHBQAAAAUAAAAIACQAAAAAAAAAIICkgQAAAABhc2RmLnR4dAoAIAAAAAAAAQAYAICi2B77MNsBgKLYHvsw2wGAotge+zDbAVBLBQYAAAAAAQABAFoAAAArAAAAAAA="
    zip_bytes = base64.b64decode(zip_base64)
    zip_file = Path("/tmp/.bbottestzipasdkfjalsdf.zip")
    with open(zip_file, "wb") as f:
        f.write(zip_bytes)

    # test magic helpers
    extension, mime_type, description, confidence = get_magic_info(zip_file)
    assert extension == ".zip"
    assert mime_type == "application/zip"
    assert description == "PKZIP Archive file"
    assert confidence > 0
    assert get_compression(mime_type) == "zip"

    # test filesystem event - file
    scan = Scanner()
    event = scan.make_event({"path": zip_file}, "FILESYSTEM", parent=scan.root_event)
    assert event.data == {
        "path": "/tmp/.bbottestzipasdkfjalsdf.zip",
        "magic_extension": ".zip",
        "magic_mime_type": "application/zip",
        "magic_description": "PKZIP Archive file",
        "magic_confidence": 0.9,
        "compression": "zip",
    }
    assert event.tags == {"file", "zip-archive", "compressed"}

    # test filesystem event - folder
    scan = Scanner()
    event = scan.make_event({"path": "/tmp"}, "FILESYSTEM", parent=scan.root_event)
    assert event.data == {"path": "/tmp"}
    assert event.tags == {"folder"}

    zip_file.unlink()


@pytest.mark.asyncio
async def test_mobile_app():
    scan = Scanner()
    with pytest.raises(ValidationError):
        scan.make_event("com.evilcorp.app", "MOBILE_APP", parent=scan.root_event)
    with pytest.raises(ValidationError):
        scan.make_event({"id": "com.evilcorp.app"}, "MOBILE_APP", parent=scan.root_event)
    with pytest.raises(ValidationError):
        scan.make_event({"url": "https://play.google.com/store/apps/details"}, "MOBILE_APP", parent=scan.root_event)
    mobile_app = scan.make_event(
        {"url": "https://play.google.com/store/apps/details?id=com.evilcorp.app"}, "MOBILE_APP", parent=scan.root_event
    )
    assert sorted(mobile_app.data.items()) == [
        ("id", "com.evilcorp.app"),
        ("url", "https://play.google.com/store/apps/details?id=com.evilcorp.app"),
    ]

    scan = Scanner("MOBILE_APP:https://play.google.com/store/apps/details?id=com.evilcorp.app")
    events = [e async for e in scan.async_start()]
    assert len(events) == 3
    mobile_app_event = [e for e in events if e.type == "MOBILE_APP"][0]
    assert mobile_app_event.type == "MOBILE_APP"
    assert sorted(mobile_app_event.data.items()) == [
        ("id", "com.evilcorp.app"),
        ("url", "https://play.google.com/store/apps/details?id=com.evilcorp.app"),
    ]


@pytest.mark.asyncio
async def test_filesystem():
    scan = Scanner("FILESYSTEM:/tmp/asdf")
    events = [e async for e in scan.async_start()]
    assert len(events) == 3
    filesystem_events = [e for e in events if e.type == "FILESYSTEM"]
    assert len(filesystem_events) == 1
    assert filesystem_events[0].type == "FILESYSTEM"
    assert filesystem_events[0].data == {"path": "/tmp/asdf"}


def test_event_hashing():
    scan = Scanner("example.com")
    url_event = scan.make_event("https://api.example.com/", "URL_UNVERIFIED", parent=scan.root_event)
    host_event_1 = scan.make_event("www.example.com", "DNS_NAME", parent=url_event)
    host_event_2 = scan.make_event("test.example.com", "DNS_NAME", parent=url_event)
    finding_data = {"description": "Custom Yara Rule [find_string] Matched via identifier [str1]"}
    finding1 = scan.make_event(finding_data, "FINDING", parent=host_event_1)
    finding2 = scan.make_event(finding_data, "FINDING", parent=host_event_2)
    finding3 = scan.make_event(finding_data, "FINDING", parent=host_event_2)

    assert finding1.data == {
        "description": "Custom Yara Rule [find_string] Matched via identifier [str1]",
        "host": "www.example.com",
    }
    assert finding2.data == {
        "description": "Custom Yara Rule [find_string] Matched via identifier [str1]",
        "host": "test.example.com",
    }
    assert finding3.data == {
        "description": "Custom Yara Rule [find_string] Matched via identifier [str1]",
        "host": "test.example.com",
    }
    assert finding1.id != finding2.id
    assert finding2.id == finding3.id
    assert finding1.data_id != finding2.data_id
    assert finding2.data_id == finding3.data_id
    assert finding1.data_hash != finding2.data_hash
    assert finding2.data_hash == finding3.data_hash
    assert hash(finding1) != hash(finding2)
    assert hash(finding2) == hash(finding3)
