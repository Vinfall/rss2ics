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
import uuid

app = Flask(__name__)


def rss_to_ics(rss_url):
    feed = feedparser.parse(rss_url)
    cal = Calendar(creator="RSS2ICS")
    now = datetime.now()

    for entry in feed.entries:
        uid = uuid.uuid4().hex
        entry_time = dateparser.parse(entry.published).replace(tzinfo=pytz.UTC)
        entry_updated = (
            dateparser.parse(entry.updated).replace(tzinfo=pytz.UTC)
            if entry.updated
            else now
        )

        event = Event(
            uid=uid,
            name=entry.title,
            description=entry.summary,
            begin=entry_time,
            last_modified=entry_updated,
            # categories=["rss"],
        )
        event.make_all_day

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
