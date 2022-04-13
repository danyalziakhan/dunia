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

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing_extensions import Self


class Element(Protocol):
    async def query_selector(self, selector: str) -> Self | None:
        ...

    async def query_selector_all(self, selector: str) -> list[Self]:
        ...

    async def text_content(self) -> str | None:
        ...

    async def get_attribute(self, name: str) -> str | None:
        ...


class Node(Element, Protocol):
    async def click(self, *, timeout: int | None = None) -> None:
        ...

    async def select_option(
        self,
        value: str | list[str] | None = None,
        *,
        label: str | list[str] | None = None,
        timeout: int | None = None,
    ) -> list[str]:
        ...

    async def scroll_into_view_if_needed(self, *, timeout: int | None = None) -> None:
        ...

    async def focus(self) -> None:
        ...

    async def is_visible(self) -> bool:
        ...

    async def is_enabled(self) -> bool:
        ...

    async def fill(self, value: str, *, timeout: int | None = None) -> None:
        ...

    async def type(self, text: str, *, timeout: int | None = None) -> None:
        ...

    async def press(self, key: str, *, timeout: int | None = None) -> None:
        ...

    async def inner_html(self) -> str:
        ...


# ? Aliases
Fragment = Element
ElementHandle = Node
