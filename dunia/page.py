# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Protocol, TypeVar, runtime_checkable

from dunia.element import Element, Node


if TYPE_CHECKING:
    import asyncio

    from pathlib import Path
    from types import NoneType
    from typing import TYPE_CHECKING, Any, Literal

ReturnSelectorType = TypeVar("ReturnSelectorType")
T = TypeVar("T")


class DocumentTextSelector(Protocol):
    async def text_content(
        self, selector: str, *, timeout: int | None = None
    ) -> str | None:
        ...

    async def inner_text(
        self, selector: str, *, timeout: int | None = None
    ) -> str | None:
        ...


class DocumentAttributeSelector(Protocol):
    async def get_attribute(
        self, selector: str, name: str, *, timeout: int | None = None
    ) -> str | None:
        ...


class QuerySelector(
    Protocol[ReturnSelectorType],
):
    async def query_selector(self, selector: str) -> ReturnSelectorType | None:
        ...

    async def query_selector_all(self, selector: str) -> list[ReturnSelectorType]:
        ...


@runtime_checkable
class Document(
    QuerySelector[Element], DocumentTextSelector, DocumentAttributeSelector, Protocol
):
    pass


@runtime_checkable
class Page(
    QuerySelector[Node], DocumentTextSelector, DocumentAttributeSelector, Protocol
):
    async def click(self, selector: str, *, timeout: int | None = None) -> None:
        ...

    async def press(
        self, selector: str, key: str, *, timeout: int | None = None
    ) -> None:
        ...

    async def fill(
        self, selector: str, value: str, *, timeout: int | None = None
    ) -> None:
        ...

    async def evaluate(self, expression: str) -> Any:
        ...

    async def type(
        self, selector: str, text: str, *, timeout: int | None = None
    ) -> None:
        ...

    async def inner_html(
        self, selector: str, *, timeout: int | None = None
    ) -> str | None:
        ...

    @property
    def mouse(self) -> Any:
        ...

    async def content(self) -> str:
        ...

    async def set_content(
        self,
        html: str,
        *,
        timeout: int | None = None,
        wait_until: Literal[
            "commit", "domcontentloaded", "load", "networkidle"
        ] = "load",
    ) -> None:
        ...

    async def goto(
        self,
        url: str,
        *,
        timeout: int | None = None,
        wait_until: Literal[
            "commit", "domcontentloaded", "load", "networkidle"
        ] = "load",
    ) -> None:
        ...

    async def close(self) -> None:
        ...

    async def pause(self) -> None:
        ...

    @property
    def url(self) -> str:
        ...

    async def screenshot(
        self, path: str, *, full_page: bool = False, timeout: int | None = None
    ) -> bytes | None:
        ...

    async def wait_for_load_state(
        self,
        state: Literal["domcontentloaded", "load", "networkidle"],
        *,
        timeout: int | None = None,
    ) -> None:
        ...

    async def wait_for_selector(
        self,
        selector: str,
        *,
        timeout: int | None = None,
        state: Literal["attached", "detached", "hidden", "visible"] | None = None,
    ) -> Node | None:
        ...

    async def wait_for_timeout(self, timeout: int) -> None:
        ...

    async def select_option(
        self,
        selector: str,
        value: str | list[str] | None = None,
        *,
        label: str | list[str] | None = None,
        timeout: int | None = None,
    ) -> list[str]:
        ...

    def frame(self, name: str) -> Frame | None:
        ...

    def expect_navigation(
        self, *, timeout: int | None = None
    ) -> AsyncEventContextManager[None]:
        ...

    def expect_download(
        self, *, timeout: int | None = None
    ) -> AsyncEventContextManager[Download]:
        ...

    async def check(self, selector: str, *, timeout: int | None = None) -> None:
        ...

    async def reload(self, *, timeout: int | None = None) -> None:
        ...


# ? Interfaces taken from Playwright's code
class AsyncEventInfo(Generic[T]):
    def __init__(self, future: asyncio.Future[T]) -> None:
        ...

    @property
    async def value(self) -> T:
        ...

    def is_done(self) -> bool:
        ...


class AsyncEventContextManager(Generic[T]):
    def __init__(self, future: asyncio.Future[T]) -> None:
        ...

    async def __aenter__(self) -> AsyncEventInfo[T]:
        ...

    async def __aexit__(self, *args: Any) -> None:
        ...


# ? We only need these methods from Playwright's Download
class Download(Protocol):
    @property
    def suggested_filename(self) -> str:
        ...

    async def save_as(self, path: str | Path) -> NoneType:
        ...


class FileChooser(Protocol):
    @property
    def page(self) -> Page:
        ...

    @property
    def element(self) -> Node:
        ...

    def is_multiple(self) -> bool:
        ...

    async def set_files(
        self,
        files: str | Path | list[str | Path],
        *,
        timeout: float | None = None,
        no_wait_after: bool | None = None,
    ) -> NoneType:
        ...


# ? We only need these methods from Playwright's Frame
class Frame(Protocol):
    async def query_selector(self, selector: str) -> Node | None:
        ...

    async def query_selector_all(self, selector: str) -> list[Node]:
        ...
