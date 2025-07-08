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

from dunia.lxml._core import cssselect, get_attribute, inner_text, text_content

if TYPE_CHECKING:
    from typing import Self

    import lxml.html as lxml

    from dunia.element import Element


@dataclass(slots=True, frozen=True)
class LXMLDocument:
    handle: lxml.HtmlElement

    async def query_selector(self, selector: str) -> Element | None:
        handles = await asyncio.to_thread(cssselect, self.handle, selector)
        return LXMLElement(handles[0]) if len(handles) else None

    async def query_selector_all(self, selector: str) -> list[Element]:
        return [
            LXMLElement(handle)
            for handle in await asyncio.to_thread(cssselect, self.handle, selector)
        ]

    async def text_content(
        self, selector: str, timeout: int | None = None
    ) -> str | None:
        return await asyncio.to_thread(text_content, self.handle, selector)

    async def inner_text(self, selector: str, timeout: int | None = None) -> str | None:
        return await asyncio.to_thread(inner_text, self.handle, selector)

    async def get_attribute(
        self, selector: str, name: str, timeout: int | None = None
    ) -> str | None:
        return await asyncio.to_thread(get_attribute, self.handle, selector, name)


@dataclass(slots=True, frozen=True)
class LXMLElement:
    handle: lxml.HtmlElement

    async def query_selector(self, selector: str) -> Self | None:
        handles = await asyncio.to_thread(cssselect, self.handle, selector)
        return LXMLElement(handles[0]) if len(handles) else None

    async def query_selector_all(self, selector: str) -> list[Self]:
        return [
            LXMLElement(handle)
            for handle in await asyncio.to_thread(cssselect, self.handle, selector)
        ]

    async def text_content(self) -> str | None:
        if text := await asyncio.to_thread(self.handle.text_content):
            return text

        return None

    async def get_attribute(self, name: str) -> str | None:
        return self.handle.get(name, default=None)
