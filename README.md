# RSS to ICS

## Intro

Python script written in [Flask](https://github.com/pallets/flask/) to generate iCalendar (ICS) from RSS/Atom feeds.
This should work as a serverless function.

Tested against [my blog feed](https://blog.vinfall.com/index.xml) and several RSS feeds generated by [RSSHub](https://github.com/DIYgod/RSSHub).

For whatever reason, it does not work for offcial RSSHub instance (`rsshub.app`) due to either official instance security configuration or a bug introduced between [legacy branch](https://github.com/DIYgod/RSSHub/tree/legacy) (which I test against on my own instance) and latest master commit.

## Usage

Let's say the instance is running at `rss2ics.vercel.app`,
the RSS feed is `example.com/feed`,
you can generate ics via `rss2ics.vercel.app/?url=example.com/feed`.

## Install

IMO there is nothing to talk about. Just clone the repo and install the requirements to run it locally,
or simply run commands like `vercel` to deploy it on platforms that support Python (serverless) functions.

## Test

You can run the test suite via the following command:

```python
# Setup venv
python3 -m venv
source .venv/bin/activate
# Install packages
pip install requirements-dev.txt
# Make sure to use module if you have pytest installed system-wide
# otherwise they would conflict and complain forever
python -m pytest tests/test_api.py
```

Maybe I would add more rules soon™, but for now it's nothing and only serve for my exploration of `pytest`.

## Todo

- [ ] Setup pytest and coverage for fun (WIP)
- [x] Add (better) Atom support
- [ ] Use `feed.title` for ICS filename (not sure why it's `None`...)

## [License](LICENSE)

BSD 3-Clause License
