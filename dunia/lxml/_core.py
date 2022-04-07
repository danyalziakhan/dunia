# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

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
    html_elements = cssselect(tree, selector)
    if len(html_elements):
        return html_elements[0].text_content()

    return None


def inner_text(tree: lxml.HtmlElement, selector: str) -> str | None:
    html_elements = cssselect(tree, selector)
    if len(html_elements):
        return html_elements[0].text

    return None


def get_attribute(tree: lxml.HtmlElement, selector: str, name: str) -> str | None:
    html_elements = cssselect(tree, selector)
    if len(html_elements):
        return html_elements[0].get(name, None)

    return None
