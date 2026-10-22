"""
Static site generator for the AI Engineering Learning Hub.

Reads learn-hub/topics.json and writes a fully static site to learn-hub/site/:

    site/index.html              hub home (search, filters, all topics)
    site/<topic-id>/index.html   one crawlable page per topic (SEO, OG, JSON-LD)
    site/sitemap.xml             submitted via robots.txt at the domain root
    site/hub.css, site/hub.js    shared assets

FastAPI mounts learn-hub/site at /learn (see main.py). Run after editing
topics.json or the templates:

    python learn-hub/build.py

No LLM is involved; everything on the hub is hand-written content.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "site"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
TOPICS_FILE = ROOT / "topics.json"

SITE_URL = "https://abdurrehmanafzal.cloud"
HUB_PATH = "/learn"
SITE_NAME = "AI Engineering Learning Hub"
OG_IMAGE = f"{SITE_URL}/assets/learn-og.jpg"

AUTHOR = {
    "name": "Abdur Rehman Afzal",
    "email": "abdurrehmanafzal786@gmail.com",
    "linkedin": "https://linkedin.com/in/abdurrehmanafzal",
    "url": SITE_URL,
}

INDEX_DESCRIPTION = (
    "Free, practical AI engineering lessons: machine learning fundamentals, "
    "embeddings, RAG pipelines, vector databases, function calling and more. "
    "Each topic has working code and interview questions, written from real projects."
)

_HL_PATTERN = re.compile(
    r"(#.*$)"
    r"|('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")"
    r"|\b(import|from|def|class|return|if|elif|else|for|while|in|as|not|and|or|is|True|False|None|lambda|with|try|except|yield|async|await)\b"
    r"|\b(\d+\.?\d*)\b",
    re.MULTILINE,
)


def highlight(code: str) -> Markup:
    """Tiny Python syntax highlighter, mirrors the old client-side one."""
    escaped = html.escape(code, quote=False)

    def repl(m: re.Match) -> str:
        comment, string, keyword, number = m.groups()
        if comment:
            return f'<span class="hl-comment">{comment}</span>'
        if string:
            return f'<span class="hl-string">{string}</span>'
        if keyword:
            return f'<span class="hl-keyword">{keyword}</span>'
        if number:
            return f'<span class="hl-number">{number}</span>'
        return m.group(0)

    return Markup(_HL_PATTERN.sub(repl, escaped))


def paras(text: str) -> list[str]:
    """Split a field on blank lines so templates can render real paragraphs."""
    return [p.strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]


def reading_minutes(topic: dict) -> int:
    text = " ".join(
        [topic["whatIs"], topic["why"], *topic["how"], topic["code"], *topic["useCases"]]
        + [p["q"] + " " + p["a"] for p in topic["qa"]]
        + [topic.get("usedIn", ""), *topic.get("pitfalls", [])]
    )
    words = len(text.split())
    return max(1, round(words / 200))


def build_id() -> str:
    h = hashlib.sha1()
    for p in sorted(STATIC.iterdir()):
        h.update(p.read_bytes())
    return h.hexdigest()[:8]


def load_topics() -> tuple[list[dict], list[dict]]:
    data = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    categories: list[dict] = []
    flat: list[dict] = []
    number = 0
    for cat in data["categories"]:
        cat_entry = {
            "id": cat["id"],
            "name": cat["name"],
            "description": cat.get("description", ""),
            "topics": [],
        }
        for topic in cat["topics"]:
            number += 1
            t = dict(topic)
            t["number"] = number
            t["category"] = cat_entry
            t["url"] = f"{HUB_PATH}/{t['id']}/"
            t["canonical"] = f"{SITE_URL}{t['url']}"
            t["code_html"] = highlight(t["code"])
            t["reading_time"] = reading_minutes(t)
            t["search_text"] = " ".join(
                [t["title"], t["summary"], cat["name"], *[p["q"] for p in t["qa"]]]
            ).lower()
            cat_entry["topics"].append(t)
            flat.append(t)
        categories.append(cat_entry)

    for i, t in enumerate(flat):
        t["prev"] = flat[i - 1] if i > 0 else None
        t["next"] = flat[i + 1] if i + 1 < len(flat) else None
        siblings = [s for s in t["category"]["topics"] if s["id"] != t["id"]]
        # Nearest neighbours in the same category read best as "related".
        siblings.sort(key=lambda s: abs(s["number"] - t["number"]))
        t["related"] = siblings[:3]

    return categories, flat


def jsonld_person() -> dict:
    return {
        "@type": "Person",
        "name": AUTHOR["name"],
        "url": AUTHOR["url"],
        "sameAs": [AUTHOR["linkedin"]],
    }


def topic_jsonld(t: dict, today: str) -> list[dict]:
    article = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": t["title"],
        "description": t["summary"],
        "author": jsonld_person(),
        "dateModified": today,
        "mainEntityOfPage": t["canonical"],
        "inLanguage": "en",
        "proficiencyLevel": "Beginner",
        "about": t["category"]["name"],
    }
    breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": f"{SITE_URL}{HUB_PATH}/"},
            {"@type": "ListItem", "position": 2, "name": t["category"]["name"], "item": f"{SITE_URL}{HUB_PATH}/#{t['category']['id']}"},
            {"@type": "ListItem", "position": 3, "name": t["title"], "item": t["canonical"]},
        ],
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": p["q"],
                "acceptedAnswer": {"@type": "Answer", "text": p["a"]},
            }
            for p in t["qa"]
        ],
    }
    return [article, breadcrumbs, faq]


def index_jsonld(flat: list[dict]) -> list[dict]:
    return [
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": SITE_NAME,
            "description": INDEX_DESCRIPTION,
            "url": f"{SITE_URL}{HUB_PATH}/",
            "author": jsonld_person(),
            "inLanguage": "en",
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": [
                    {"@type": "ListItem", "position": t["number"], "name": t["title"], "url": t["canonical"]}
                    for t in flat
                ],
            },
        }
    ]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build() -> None:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["paras"] = paras

    categories, flat = load_topics()
    today = dt.date.today().isoformat()
    common = {
        "site_name": SITE_NAME,
        "site_url": SITE_URL,
        "hub_path": HUB_PATH,
        "og_image": OG_IMAGE,
        "author": AUTHOR,
        "year": dt.date.today().year,
        "build_id": build_id(),
        "categories": categories,
        "topics": flat,
    }

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for asset in STATIC.iterdir():
        shutil.copy2(asset, OUT / asset.name)

    index_tpl = env.get_template("index.html")
    write(
        OUT / "index.html",
        index_tpl.render(
            **common,
            page="index",
            topic=None,
            page_title=f"{SITE_NAME} · {AUTHOR['name']}",
            description=INDEX_DESCRIPTION,
            canonical=f"{SITE_URL}{HUB_PATH}/",
            og_type="website",
            jsonld=index_jsonld(flat),
        ),
    )

    topic_tpl = env.get_template("topic.html")
    for t in flat:
        write(
            OUT / t["id"] / "index.html",
            topic_tpl.render(
                **common,
                page="topic",
                topic=t,
                page_title=f"{t['title']} · {SITE_NAME}",
                description=t["summary"],
                canonical=t["canonical"],
                og_type="article",
                jsonld=topic_jsonld(t, today),
            ),
        )

    urls = [(f"{SITE_URL}{HUB_PATH}/", "1.0", "weekly")] + [
        (t["canonical"], "0.8", "monthly") for t in flat
    ]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, priority, freq in urls:
        sitemap.append(
            f"  <url><loc>{html.escape(loc)}</loc><lastmod>{today}</lastmod>"
            f"<changefreq>{freq}</changefreq><priority>{priority}</priority></url>"
        )
    sitemap.append("</urlset>")
    write(OUT / "sitemap.xml", "\n".join(sitemap) + "\n")

    print(f"Built {len(flat)} topic pages + index + sitemap into {OUT.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    build()
