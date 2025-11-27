#!/usr/bin/env python3

# Documentation
# Feedparser: https://feedparser.readthedocs.io/en/latest/
# ICS (outdated): https://icspy.readthedocs.io/en/stable/api.html#event

import hashlib
import random
import re
from datetime import datetime

import dateparser
import feedparser
import pytz
from flask import Flask, Response, request
from ics import Calendar, Event

# import uuid

app = Flask(__name__)


# Sanitize img src in feed summary
def sanitize_summary(summary):
    return re.sub(r"<img src=\".*?\" />", "", summary)


def rss_to_ics(rss_url):
    # Parse RSS
    feed = feedparser.parse(rss_url)
    # Add metadata for iCalendar
    cal = Calendar(creator="RSS2ICS")
    now = datetime.now()  # noqa: DTZ005

    for entry in reversed(feed.entries):
        # NOTE: feedparser has a reverse fallback to "published" if "updated" does not exist...
        # Fallback to "updated" if "published" does not exist
        if hasattr(entry, "published") and entry.published is not None:
            entry_time = dateparser.parse(entry.published).replace(tzinfo=pytz.UTC)
        elif entry.updated:
            entry_time = dateparser.parse(entry.updated).replace(tzinfo=pytz.UTC)
        else:
            entry_time = now
        # Prefer "updated" element over now
        entry_updated = (
            dateparser.parse(entry.updated).replace(tzinfo=pytz.UTC)
            if entry.updated
            else now
        )
        # unique UUID
        # uid = uuid.uuid4().hex
        combined_string = entry.title + "-" + entry_time.strftime("%Y-%m-%d")
        uid = hashlib.md5(combined_string.encode()).hexdigest()  # noqa: S324
        # Some ATOM feeds have no summary/description
        desc = ""
        if hasattr(entry, "summary") and entry.summary:
            desc = sanitize_summary(entry.summary) + "\n" + entry.link
        else:
            desc = entry.link

        # Enough info for a calendar event
        event = Event(
            uid=uid,
            begin=entry_time,
            last_modified=entry_updated,
            dtstamp=now,
            summary=entry.title,
            description=desc,
            # categories=["rss"],
        )
        event.make_all_day()

        cal.events.append(event)

    return cal


def coin():
    return random.choice([0, 1])  # noqa: S311


def get_error_message():
    # Cat or dog, that is the question
    return """
    No RSS URL provided. Usage: https://rss2ics.vercel.app/?url=example.com/feed

    <div><img src="https://{}/400.jpg" alt="Bad Request" style="max-width:400px;"></div>
    """.format("http.cat" if coin() == 0 else "http.dog")


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
    app.run(debug=False)
