#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Documentation
# Feedparser: https://feedparser.readthedocs.io/en/latest/
# ICS: https://icspy.readthedocs.io/en/stable/api.html#event

from datetime import datetime, timedelta
import dateparser
from flask import Flask, request, Response
import feedparser
from ics import Calendar, Event
import pytz

app = Flask(__name__)


def rss_to_ics(rss_url):
    feed = feedparser.parse(rss_url)
    cal = Calendar()
    for entry in feed.entries:
        event = Event()
        event.name = entry.title
        event.begin = dateparser.parse(entry.published).replace(tzinfo=pytz.UTC)
        event.end = dateparser.parse(entry.published).replace(
            tzinfo=pytz.UTC
        ) + timedelta(hours=1)
        event.description = entry.summary
        cal.events.add(event)
    return cal


@app.route("/", methods=["GET"])
def get_ics():
    rss_url = request.args.get("rss")
    if rss_url:
        ics_content = rss_to_ics(rss_url).serialize()
        response = Response(ics_content, mimetype="text/calendar")
        response.headers["Content-Disposition"] = "attachment; filename=rss.ics"
        return response
    else:
        return "No RSS URL provided", 400


if __name__ == "__main__":
    app.run(debug=True)
