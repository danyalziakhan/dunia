# MIT License

# Copyright (c) 2022-2025 Danyal Zia Khan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from functools import cache
from typing import cast

import lxml.html as lxml
from cssselect import HTMLTranslator, SelectorError


@cache
def css_to_xpath(selector: str) -> str | None:
    # ? If the selector is already XPATH, then just return it
    if (
        selector.startswith("xpath=")
        or selector.startswith("//")
        or selector.startswith("..")
    ):
        return selector.removeprefix("xpath=")

    try:
        return HTMLTranslator().css_to_xpath(selector)
    except SelectorError:
        return None


def cssselect(tree: lxml.HtmlElement, selector: str) -> list[lxml.HtmlElement]:
    if expression := css_to_xpath(selector):
        return cast(list[lxml.HtmlElement], tree.xpath(expression))

    return []


def text_content(tree: lxml.HtmlElement, selector: str) -> str | None:
    handles = cssselect(tree, selector)
    return handles[0].text_content() if len(handles) else None


def inner_text(tree: lxml.HtmlElement, selector: str) -> str | None:
    handles = cssselect(tree, selector)
    return handles[0].text if len(handles) else None


def get_attribute(tree: lxml.HtmlElement, selector: str, name: str) -> str | None:
    handles = cssselect(tree, selector)
    return handles[0].get(name, None) if len(handles) else None
