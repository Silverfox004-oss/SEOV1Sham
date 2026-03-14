"""
Alianza Search Readiness Scanner — HTML Parser
Extracts metadata, headings, schema, images, links, and text from HTML.
"""

import json
from html.parser import HTMLParser


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.meta_description = ""
        self.meta_viewport = ""
        self.meta_robots = ""
        self.canonical = ""
        self.og_title = ""
        self.og_description = ""
        self.og_image = ""
        self.twitter_card = ""
        self.headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}
        self.current_heading = None
        self.current_heading_text = ""
        self.images_total = 0
        self.images_with_alt = 0
        self.internal_links = 0
        self.external_links = 0
        self.has_contact_link = False
        self.json_ld_blocks = []
        self.schema_types = []
        self.in_json_ld = False
        self.json_ld_text = ""
        self.semantic_tags = set()
        self.semantic_tag_list = {"article", "section", "nav", "main", "header", "footer", "aside"}
        self.word_count = 0
        self.paragraph_count = 0
        self.in_p = False
        self.p_text = ""
        self.all_text = ""
        self.has_faq_heading = False
        self.question_headings = 0
        self.hreflang_tags = []
        self.geo_meta = False
        self.has_maps_embed = False
        self.speakable_schema = False
        self.last_modified_meta = ""
        self.date_meta = ""
        self.base_url = ""
        self.phone_in_content = False
        self.address_in_content = False
        self.has_schema_scripts = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "title":
            self.in_title = True
            self.title = ""

        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")

            if name == "description":
                self.meta_description = content
            elif name == "viewport":
                self.meta_viewport = content
            elif name == "robots":
                self.meta_robots = content
            elif name == "geo.position" or name == "geo.region" or name == "icbm":
                self.geo_meta = True
            elif name == "last-modified" or name == "date":
                self.date_meta = content
            elif prop == "og:title":
                self.og_title = content
            elif prop == "og:description":
                self.og_description = content
            elif prop == "og:image":
                self.og_image = content
            elif name == "twitter:card" or prop == "twitter:card":
                self.twitter_card = content

        elif tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            href = attrs_dict.get("href", "")
            hreflang = attrs_dict.get("hreflang", "")
            if rel == "canonical":
                self.canonical = href
            if hreflang:
                self.hreflang_tags.append(hreflang)

        elif tag in self.headings:
            self.current_heading = tag
            self.current_heading_text = ""

        elif tag == "img":
            self.images_total += 1
            alt = attrs_dict.get("alt", None)
            if alt is not None and alt.strip():
                self.images_with_alt += 1

        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href:
                if href.startswith("http") and self.base_url and self.base_url not in href:
                    self.external_links += 1
                else:
                    self.internal_links += 1
                if "/contact" in href.lower() or "contact" in href.lower():
                    self.has_contact_link = True

        elif tag == "script":
            stype = attrs_dict.get("type", "").lower()
            if stype == "application/ld+json":
                self.in_json_ld = True
                self.json_ld_text = ""

        elif tag == "iframe":
            src = attrs_dict.get("src", "")
            if "google.com/maps" in src or "maps.google" in src:
                self.has_maps_embed = True

        elif tag == "p":
            self.in_p = True
            self.p_text = ""

        if tag in self.semantic_tag_list:
            self.semantic_tags.add(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

        elif tag in self.headings and self.current_heading == tag:
            text = self.current_heading_text.strip()
            self.headings[tag].append(text)
            # Check for question patterns
            if text and ("?" in text or text.lower().startswith(("what ", "how ", "why ", "when ", "where ", "who ", "can ", "do ", "does ", "is ", "are "))):
                self.question_headings += 1
                if tag in ("h2", "h3"):
                    self.has_faq_heading = True
            self.current_heading = None

        elif tag == "script" and self.in_json_ld:
            self.in_json_ld = False
            try:
                parsed = json.loads(self.json_ld_text)
                self.json_ld_blocks.append(parsed)
                self.has_schema_scripts += 1
            except (json.JSONDecodeError, ValueError):
                pass

        elif tag == "p" and self.in_p:
            self.in_p = False
            text = self.p_text.strip()
            if len(text) > 20:
                self.paragraph_count += 1
                words = text.split()
                self.word_count += len(words)
                self.all_text += " " + text

    def handle_data(self, data):
        if self.in_title:
            self.title += data

        if self.current_heading:
            self.current_heading_text += data

        if self.in_json_ld:
            self.json_ld_text += data

        if self.in_p:
            self.p_text += data

        # Also accumulate text for phone/address detection
        stripped = data.strip()
        if stripped:
            self.all_text += " " + stripped
