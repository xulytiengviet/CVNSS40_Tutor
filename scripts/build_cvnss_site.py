#!/usr/bin/env python3
"""Build the dependency-free CVNSS4.0 guide and check its local links.

Run from any directory. Default output: dist/site, suitable for GitHub Pages
at a repository subpath. Canonical data and the skills-only ZIP are copied at
build time; no remote service is contacted and no deployment is performed.
"""
from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import sys
from urllib.parse import unquote, urlsplit

# Permit both `python scripts/build_cvnss_site.py` and module imports.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.build_cvnss_chatgpt_plugin import make_archive


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.topics: set[str] = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise ValueError(f"Duplicate HTML id: {attrs['id']}")
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])
        if "data-topic" in attrs:
            self.topics.add(attrs["data-topic"])


def validate_site(out: Path) -> None:
    page = PageLinks()
    page.feed((out / "index.html").read_text(encoding="utf-8"))
    for href in page.links:
        url = urlsplit(href)
        if url.scheme or url.netloc:
            if url.scheme != "https":
                raise ValueError(f"Unexpected external link protocol: {href}")
            continue
        if url.path.startswith("/"):
            raise ValueError(f"Root-relative link breaks project Pages: {href}")
        if url.path:
            target = (out / unquote(url.path)).resolve()
            if not target.is_relative_to(out.resolve()) or not target.is_file():
                raise ValueError(f"Missing or escaping local target: {href}")
        elif url.fragment and unquote(url.fragment) not in page.ids:
            raise ValueError(f"Unknown fragment: {href}")
    knowledge = json.loads((out / "knowledge.json").read_text(encoding="utf-8"))
    if page.topics != {topic["id"] for topic in knowledge["topics"]}:
        raise ValueError("Page topic index is out of sync with the knowledge registry")


def build(out: Path) -> Path:
    out = out.resolve()
    # Refuse destinations that could overwrite source or checkout metadata.
    source = ROOT / "docs-for-dev" / "site"
    if out == ROOT or (out.is_relative_to(ROOT) and not out.is_relative_to(ROOT / "dist")):
        raise ValueError("Inside the checkout, output must be below dist/")
    if source.is_relative_to(out):
        raise ValueError("Choose a dedicated output directory, not a source directory")
    out.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "style.css", "app.js", "LICENSE.txt"):
        shutil.copyfile(source / name, out / name)
    for source_name, target_name in (
        ("knowledge.json", "knowledge.json"),
        ("knowledge.schema.json", "knowledge.schema.json"),
        ("STANDARDIZATION.md", "standardization.md"),
    ):
        shutil.copyfile(ROOT / "cvnss_hub" / source_name, out / target_name)
    manifest = json.loads((ROOT / "integrations/chatgpt-plugin/plugin.json").read_text())
    name = f"{manifest['name']}-{manifest['version']}.zip"
    make_archive(out=out / "downloads" / name)
    (out / ".nojekyll").write_text("", encoding="utf-8")
    validate_site(out)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "dist" / "site")
    args = parser.parse_args()
    print(f"Built and validated CVNSS4.0 guide: {build(args.out)}")
