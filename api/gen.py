#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Documentation
# Feedparser: https://feedparser.readthedocs.io/en/latest/
# ICS: https://icspy.readthedocs.io/en/stable/api.html#event

from datetime import datetime
import re
import random
import dateparser
from flask import Flask, request, Response
import feedparser
from ics import Calendar, Event
import pytz
import uuid

app = Flask(__name__)


# Sanitize img src in feed summary
def sanitize_summary(summary):
    sanitized_summary = re.sub(r"<img src=\".*?\" />", "", summary)
    return sanitized_summary


def rss_to_ics(rss_url):
    # Parse RSS
    feed = feedparser.parse(rss_url)
    # Add metadata for iCalendar
    cal = Calendar(creator="RSS2ICS")
    now = datetime.now()

    for entry in feed.entries:
        uid = uuid.uuid4().hex  # unique UUID
        entry_time = dateparser.parse(entry.published).replace(tzinfo=pytz.UTC)
        # Prefer "updated" element over now
        entry_updated = (
            dateparser.parse(entry.updated).replace(tzinfo=pytz.UTC)
            if entry.updated
            else now
        )
        # Enough info for a calendar event
        desc = sanitize_summary(entry.summary) + "\n" + entry.link

        event = Event(
            uid=uid,
            name=entry.title,
            description=desc,
            begin=entry_time,
            last_modified=entry_updated,
            # categories=["rss"],
        )
        event.make_all_day

        cal.events.add(event)

    return cal


def coin():
    return random.choice([0, 1])


def get_error_message():
    # Cat or dog, that is the question
    error_msg = """
    No RSS URL provided. Usage: https://rss2ics.vercel.app/?url=example.com/feed

    <div><img src="https://{}/400.jpg" alt="Bad Request" style="max-width:400px;"></div>
    """.format("http.cat" if coin() == 0 else "http.dog")

    return error_msg


@app.route("/", methods=["GET"])
def get_ics():
    # Generate via `?url=blahblah.tld/atom.xml`
    rss_url = request.args.get("url")
    if rss_url:
        ics_content = rss_to_ics(rss_url).serialize()
        # EOL should be CRLF already
        response = Response(ics_content, mimetype="text/calendar")
        # TODO: figure out why feed.title cannot be used as filename
        response.headers["Content-Disposition"] = "attachment; filename=rss.ics"
        return response
    else:
        return (
            get_error_message(),
            400,
        )


if __name__ == "__main__":
    app.run(debug=True)
