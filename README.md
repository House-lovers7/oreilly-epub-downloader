# O'Reilly EPUB Downloader

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

A CLI to download O'Reilly books as EPUB for offline reading. Uses cookie-based authentication to access your subscription content and generates clean EPUBs with images, cover art, and proper chapter structure.

## Installation

```bash
pip install -e .
```

## Usage

### 1. Export cookies from O'Reilly

1. Log into https://learning.oreilly.com in your browser
2. Open Developer Tools (Cmd+Option+I)
3. Go to Console and run:
   ```javascript
   JSON.stringify(Object.fromEntries(document.cookie.split('; ').map(c => c.split('='))))
   ```
4. Save the output to `cookies.json`

### 2. Download books

```bash
# By book ID
oreilly-dl 9781098166298 -c cookies.json

# By URL
oreilly-dl "https://learning.oreilly.com/library/view/ai-engineering/9781098166298/" -c cookies.json

# Custom output path
oreilly-dl 9781098166298 -c cookies.json -o "My Book.epub"
```

Example output:

![Example output](assets/example.png)

Books are saved to `./downloads/` by default.

## Finding Book IDs

The book ID is the number in the O'Reilly URL:
- URL: `https://learning.oreilly.com/library/view/ai-engineering/9781098166298/`
- Book ID: `9781098166298`

## Refreshing Cookies

Cookies expire periodically. When downloads fail, re-export cookies from your browser.

## Requirements

- Python 3.11+
- Active O'Reilly Learning subscription

<!-- BEGIN GENERATED ENGINEERING HANDBOOK -->
## Engineering handbook

- [Start here](./docs/engineering/README.md)
- [Architecture / system diagram](./docs/engineering/02_architecture.md)
- [API](./docs/engineering/04_api.md) / [Data model](./docs/engineering/05_data_model.md) / [Screens](./docs/engineering/06_screen_design.md)
- Detected check: `oreilly-dl`
- Snapshot: API 0 / entity 1 / screen 0 / test files 0
- Data sources: `src/epub.py`
- Handoff gaps: 0 P0/P1 items — [details](./docs/engineering/00_one_pager.md#引継ぎ時の未解決ギャップ)

> Generated from the current checkout. Existing ADR/schema/runbook remains authoritative; production state is not asserted.
<!-- END GENERATED ENGINEERING HANDBOOK -->
