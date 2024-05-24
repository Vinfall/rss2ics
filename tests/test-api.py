#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Documentation
# pytest: https://docs.pytest.org/en/latest/

import pytest
import importlib.util
import os

gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../api/gen.py"))
spec = importlib.util.spec_from_file_location("gen", gen_path)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

app = gen.app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_get_ics_with_url(client):
    response = client.get("/?url=https://blog.vinfall.com/index.xml")
    assert response.status_code == 200
    assert response.mimetype == "text/calendar"
    assert b"BEGIN:VCALENDAR" in response.data


def test_get_ics_without_url(client):
    response = client.get("/")
    assert response.status_code == 400
    assert b"No RSS URL provided" in response.data
