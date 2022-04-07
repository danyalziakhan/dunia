# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

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
