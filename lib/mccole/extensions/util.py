"""McCole template utilities."""

import ark
import markdown
from pathlib import Path
import re
import sys
import yaml


# Names of parts.
KIND = {
    "en": {
        "appendix": "Appendix",
        "chapter": "Chapter",
        "figure": "Figure",
        "table": "Table",
    },
}

# Markdown extensions.
MD_EXTENSIONS = [
    "markdown.extensions.extra",
    "markdown.extensions.smarty"
]

# Match inside HTML paragraph markers.
INSIDE_PARAGRAPH = re.compile(r"<p>(.+?)</p>")


def allowed(kwargs, allowed):
    """Check that dictionary keys are a subset of those allowed."""
    return set(kwargs.keys()).issubset(allowed)


def ensure_links():
    """Load links and create appendable text."""
    if "_links_" in ark.site.config:
        return
    filepath = Path(ark.site.home(), "info", "links.yml")
    links = yaml.safe_load(filepath.read_text()) or []
    ark.site.config["_links_"] = {lnk["key"]: lnk for lnk in links}
    ark.site.config["_links_block_"] = "\n".join(
        f"[{key}]: {value['url']}" for key, value in ark.site.config["_links_"].items()
    )


def fail(msg):
    """Fail unilaterally."""
    print(msg, file=sys.stderr)
    raise AssertionError(msg)


def kind(part_name):
    """Localize name of part."""
    lang = ark.site.config["lang"]
    require(
        part_name in KIND[lang],
        f"Unknown part name {part_name} for language {lang}",
    )
    return KIND[lang][part_name]


def markdownify(text, strip_p=True, with_links=False):
    """Convert Markdown to HTML."""
    links = ark.site.config.get("_links_block_", "")
    result = markdown.markdown(f"{text}\n{links}", extensions=MD_EXTENSIONS)
    if strip_p and result.startswith("<p>"):
        result = INSIDE_PARAGRAPH.match(result).group(1)
    return result


def require(cond, msg):
    """Fail if condition untrue."""
    if not cond:
        fail(msg)


def require_file(node, filename, kind):
    """Require that a file exists."""
    filepath = Path(Path(node.filepath).parent, filename)
    require(filepath.exists(), f"Missing {kind} file {filename} from {node.path}")
