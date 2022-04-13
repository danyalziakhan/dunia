# MIT License

# Copyright (c) 2022 Danyal Zia Khan

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

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dunia.modest._core import css, css_first

if TYPE_CHECKING:
    from selectolax.parser import HTMLParser, Node
    from typing_extensions import Self

    from dunia.element import Element


@dataclass(slots=True, frozen=True)
class ModestDocument:
    html_element: HTMLParser

    async def query_selector(self, selector: str) -> Element | None:
        if html_element := await css_first(self.html_element, selector):
            return ModestElement(html_element)  # type: ignore

        return None

    async def query_selector_all(self, selector: str) -> list[Element]:
        return [
            ModestElement(html_element)
            for html_element in await css(self.html_element, selector)
        ]

    async def text_content(
        self, selector: str, *, timeout: int | None = None
    ) -> str | None:
        if html_element := await css_first(self.html_element, selector):
            return html_element.text(deep=True)  # type: ignore

        return None

    async def inner_text(
        self, selector: str, *, timeout: int | None = None
    ) -> str | None:
        if html_element := await css_first(self.html_element, selector):
            return html_element.text(deep=False)  # type: ignore

        return None

    async def get_attribute(
        self, selector: str, name: str, *, timeout: int | None = None
    ) -> str | None:
        if html_element := await css_first(self.html_element, selector):
            return html_element.attrs.sget(name, None)  # type: ignore

        return None


@dataclass(slots=True, frozen=True)
class ModestElement:
    html_element: Node

    async def query_selector(self, selector: str) -> Self | None:
        if html_element := await css_first(self.html_element, selector):
            return ModestElement(html_element)  # type: ignore

        return None

    async def query_selector_all(self, selector: str) -> list[Self]:
        return [
            ModestElement(html_element)
            for html_element in await css(self.html_element, selector)
        ]

    async def text_content(self) -> str | None:
        if text := await asyncio.to_thread(self.html_element.text):
            return text

        return None

    async def get_attribute(self, name: str) -> str | None:
        return self.html_element.attrs.sget(name, default=None)
