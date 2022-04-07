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

from dunia.lxml._core import cssselect, get_attribute, inner_text, text_content


if TYPE_CHECKING:
    import lxml.html as lxml

    from typing_extensions import Self

    from dunia.element import Element


@dataclass(slots=True, frozen=True)
class LXMLDocument:
    html_element: lxml.HtmlElement

    async def query_selector(self, selector: str) -> Element | None:
        html_elements = await asyncio.to_thread(cssselect, self.html_element, selector)
        if len(html_elements):
            return LXMLElement(html_elements[0])

        return None

    async def query_selector_all(self, selector: str) -> list[Element]:
        return [
            LXMLElement(html_element)
            for html_element in await asyncio.to_thread(
                cssselect, self.html_element, selector
            )
        ]

    async def text_content(
        self, selector: str, timeout: int | None = None
    ) -> str | None:
        return await asyncio.to_thread(text_content, self.html_element, selector)

    async def inner_text(self, selector: str, timeout: int | None = None) -> str | None:
        return await asyncio.to_thread(inner_text, self.html_element, selector)

    async def get_attribute(
        self, selector: str, name: str, timeout: int | None = None
    ) -> str | None:
        return await asyncio.to_thread(get_attribute, self.html_element, selector, name)


@dataclass(slots=True, frozen=True)
class LXMLElement:
    html_element: lxml.HtmlElement

    async def query_selector(self, selector: str) -> Self | None:
        html_elements = await asyncio.to_thread(cssselect, self.html_element, selector)
        if len(html_elements):
            return LXMLElement(html_elements[0])

        return None

    async def query_selector_all(self, selector: str) -> list[Self]:
        return [
            LXMLElement(html_element)
            for html_element in await asyncio.to_thread(
                cssselect, self.html_element, selector
            )
        ]

    async def text_content(self) -> str | None:
        if text := await asyncio.to_thread(self.html_element.text_content):
            return text

        return None

    async def get_attribute(self, name: str) -> str | None:
        return self.html_element.get(name, default=None)
