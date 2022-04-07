# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

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
