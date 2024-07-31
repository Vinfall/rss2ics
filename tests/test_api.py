#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Documentation
# pytest: https://docs.pytest.org/en/latest/

import importlib.util
import os

import pytest

gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../api/gen.py"))
spec = importlib.util.spec_from_file_location("gen", gen_path)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

app = gen.app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


# Test against different specs
test_urls = {
    "RSS 2.0": "https://blog.vinfall.com/index.xml",
    "Atom": "https://git.vinfall.com/Vinfall/rss2ics/tags.atom",
    # "RSSHub": "https://rsshub.app/rsshub/routes/en",
}


@pytest.mark.parametrize("name, url", test_urls.items())
def test_get_ics_with_url(client, name, url):
    # Fetch response using the URL from the dictionary
    response = client.get(f"/?url={url}")

    # trunk-ignore-all(bandit/B101): pytest uses assert extensively
    # Check response status code
    assert response.status_code == 200, f"Failed for URL: {url}"

    # Check response mimetype
    assert response.mimetype == "text/calendar", f"Incorrect mimetype for URL: {url}"

    # Check for VCALENDAR content
    assert (
        b"BEGIN:VCALENDAR" in response.data
    ), f"Missing VCALENDAR content for URL: {url}"


def test_get_ics_without_url(client):
    response = client.get("/")
    assert response.status_code == 400
    assert b"No RSS URL provided" in response.data
