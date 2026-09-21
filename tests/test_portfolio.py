"""Offline checks for the static portfolio; run with unittest discovery."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGES = (Path("index.html"), Path("book-rpg/index.html"))
LINKEDIN = "https://nl.linkedin.com/in/gerko-schrieken-b1853246"
VOID_TAGS = frozenset("area base br col embed hr img input link meta param source track wbr".split())


class Page(HTMLParser):
    """Collect structure and references in these explicitly closed HTML pages.

    This is a focused regression checker, not a complete HTML conformance validator.
    """
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.elements: list[dict] = []
        self.stack: list[dict] = []
        self.ids: set[str] = set()
        self.errors: list[str] = []
        self.feed(text)
        self.close()
        if self.stack:
            self.errors.append("Unclosed tags: " + ", ".join(el["tag"] for el in self.stack))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element = {"tag": tag, "attrs": values, "text": "",
                   "parents": tuple(el["tag"] for el in self.stack)}
        self.elements.append(element)
        identifier = values.get("id")
        if identifier:
            if identifier in self.ids:
                self.errors.append("Duplicate id: " + identifier)
            self.ids.add(identifier)
        if tag not in VOID_TAGS:
            self.stack.append(element)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1]["tag"] != tag:
            self.errors.append("Unexpected closing tag: " + tag)
        else:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        for element in self.stack:
            element["text"] += data

    def tags(self, tag: str) -> list[dict]:
        return [el for el in self.elements if el["tag"] == tag]


def read_page(relative: Path) -> Page:
    return Page((ROOT / relative).read_text(encoding="utf-8"))


def reference_error(relative: Path, reference: str) -> str | None:
    """Resolve relative files and HTML fragments without network requests."""
    if not reference.strip():
        return "Empty reference"
    url = urlsplit(urljoin("https://portfolio.invalid/" + relative.as_posix(), reference))
    if url.scheme != "https":
        return "Unexpected URL scheme: " + url.scheme
    if url.netloc != "portfolio.invalid":
        return None  # External availability is deliberately outside this check.
    target = (ROOT / unquote(url.path).lstrip("/")).resolve()
    if not target.is_relative_to(ROOT):
        return "Reference escapes the site root"
    if target.is_dir():
        target /= "index.html"
    if not target.is_file():
        return "Missing local file: " + str(target.relative_to(ROOT))
    if url.fragment:
        if target.suffix != ".html":
            return "Fragment target is not HTML"
        if unquote(url.fragment) not in read_page(target.relative_to(ROOT)).ids:
            return "Missing fragment: " + url.fragment
    return None


class PortfolioTests(unittest.TestCase):
    def test_page_structure_and_unique_ids(self):
        for path in PAGES:
            with self.subTest(page=str(path)):
                page = read_page(path)
                self.assertEqual(page.errors, [])
                self.assertEqual(len(page.tags("h1")), 1)
                self.assertEqual(len(page.tags("main")), 1)
                self.assertEqual(page.tags("html")[0]["attrs"].get("lang"), "en")

    def test_page_metadata(self):
        for path in PAGES:
            with self.subTest(page=str(path)):
                page = read_page(path)
                self.assertTrue(page.tags("title")[0]["text"].strip())
                for key, value in (("name", "viewport"), ("name", "description"),
                                   ("property", "og:title"), ("property", "og:description")):
                    matches = [el for el in page.tags("meta") if el["attrs"].get(key) == value]
                    self.assertEqual(len(matches), 1, value)
                    self.assertTrue(matches[0]["attrs"].get("content"), value)

    def test_all_internal_links_fragments_and_assets(self):
        for path in PAGES:
            for element in read_page(path).elements:
                for attr in ("href", "src"):
                    if attr in element["attrs"]:
                        ref = element["attrs"][attr]
                        with self.subTest(page=str(path), reference=ref):
                            self.assertIsNone(reference_error(path, ref))

    def test_navigation_reaches_contact_from_both_pages(self):
        for path in PAGES:
            links = [el for el in read_page(path).tags("a") if "nav" in el["parents"]]
            contact = [el for el in links if el["text"].strip() == "Contact"]
            self.assertEqual(len(contact), 1)
            self.assertIsNone(reference_error(path, contact[0]["attrs"]["href"]))
            self.assertEqual(urlsplit(contact[0]["attrs"]["href"]).fragment, "contact")

    def test_hero_has_direct_contact_action(self):
        links = read_page(PAGES[0]).tags("a")
        self.assertTrue(any(el["text"].strip() == "Get in touch" and
                            el["attrs"].get("href") == "#contact" for el in links))

    def test_contact_uses_the_verified_public_linkedin_profile(self):
        page = read_page(PAGES[0])
        contact = [el for el in page.tags("section") if el["attrs"].get("id") == "contact"]
        self.assertEqual(len(contact), 1)
        self.assertIn("Connect on LinkedIn", contact[0]["text"])
        self.assertTrue(any(el["attrs"].get("href") == LINKEDIN for el in page.tags("a")))

    def test_links_have_accessible_names(self):
        for path in PAGES:
            for link in read_page(path).tags("a"):
                name = link["attrs"].get("aria-label") or link["text"]
                self.assertTrue(name.strip(), link["attrs"])
                self.assertIn(" ".join(link["text"].split()), " ".join(name.split()))

    def test_accessibility_references_and_skip_links(self):
        for path in PAGES:
            page = read_page(path)
            self.assertEqual(page.tags("a")[0]["attrs"].get("href"), "#main")
            for element in page.elements:
                for identifier in (element["attrs"].get("aria-labelledby") or "").split():
                    self.assertIn(identifier, page.ids)

    def test_senior_positioning_and_availability(self):
        page = read_page(PAGES[0])
        self.assertIn("Senior Software Engineer", page.tags("title")[0]["text"])
        main = page.tags("main")[0]["text"]
        for phrase in (".NET", "React", "TypeScript", "Azure", "Amsterdam",
                       "Open to senior software engineering roles"):
            self.assertIn(phrase, main)

    def test_amsterdam_is_first_and_load_test_is_qualified(self):
        projects = read_page(PAGES[0]).tags("article")
        self.assertEqual(len(projects), 2)
        first = projects[0]["text"]
        for phrase in ("Amsterdam 750", "independent case study", "126,124",
                       "registration requests", "synthetic load test", "250 virtual users"):
            self.assertIn(phrase, first)

    def test_book_rpg_experimental_status_and_limits_remain(self):
        project = read_page(PAGES[0]).tags("article")[1]["text"]
        self.assertIn("experimental story engine", project)
        case_study = read_page(PAGES[1]).tags("main")[0]["text"]
        self.assertIn("This is an evolving implementation.", case_study)
        self.assertIn("No aggregate reliability or latency benchmark is claimed here.", case_study)

    def test_no_scripts_forms_placeholder_links_or_private_contact_added(self):
        for path in PAGES:
            page = read_page(path)
            self.assertEqual(page.tags("script"), [])
            self.assertEqual(page.tags("form"), [])
            for link in page.tags("a"):
                href = link["attrs"].get("href", "")
                self.assertNotIn(href, ("", "#"))
                self.assertFalse(href.startswith("mailto:"))

    def test_domain_and_static_publishing_marker_are_preserved(self):
        self.assertEqual((ROOT / "CNAME").read_text(encoding="utf-8").strip(), "gerko.amsterdam")
        self.assertTrue((ROOT / ".nojekyll").is_file())


class CheckerRegressionTests(unittest.TestCase):
    def test_checker_rejects_duplicate_ids(self):
        self.assertTrue(Page('<div id="x"></div><div id="x"></div>').errors)

    def test_checker_rejects_unbalanced_tags(self):
        self.assertTrue(Page("<section><h2>Title</section>").errors)

    def test_checker_rejects_missing_fragment(self):
        self.assertIn("Missing fragment", reference_error(PAGES[0], "#not-a-section"))

    def test_checker_rejects_missing_asset(self):
        self.assertIn("Missing local file", reference_error(PAGES[0], "./missing.png"))

    def test_checker_resolves_nested_contact_link(self):
        self.assertIsNone(reference_error(PAGES[1], "../#contact"))
        self.assertIn("Missing fragment", reference_error(PAGES[1], "./#contact"))

    def test_checker_rejects_unsafe_scheme(self):
        self.assertIn("Unexpected URL scheme", reference_error(PAGES[0], "javascript:void(0)"))

    def test_checker_rejects_empty_reference(self):
        self.assertEqual(reference_error(PAGES[0], ""), "Empty reference")


if __name__ == "__main__":
    unittest.main()
