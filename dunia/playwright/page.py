# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from dunia.error import PlaywrightTimeoutError
from dunia.page import AsyncEventContextManager, Download, FileChooser, Frame


if TYPE_CHECKING:
    from typing import Any, Literal

    import playwright.async_api as playwright

    from typing_extensions import Self

    from dunia.element import Node

@dataclass(slots=True, frozen=True)
class PlaywrightPage:
    page: playwright.Page

    async def query_selector(self, selector: str) -> Node | None:
        if handle := await self.page.query_selector(selector):
            return PlaywrightElementHandle(handle)

        return None

    async def query_selector_all(self, selector: str) -> list[Node]:
        return [
            PlaywrightElementHandle(handle)
            for handle in await self.page.query_selector_all(selector)
        ]

    async def text_content(
        self, selector: str, *, timeout: float | None = None
    ) -> str | None:
        try:
            text = await self.page.text_content(selector, timeout=timeout)  # type: ignore
        except PlaywrightTimeoutError:
            return None
        else:
            return text

    async def inner_text(
        self, selector: str, *, timeout: float | None = None
    ) -> str | None:
        try:
            text = await self.page.inner_text(selector, timeout=timeout)  # type: ignore
        except PlaywrightTimeoutError:
            return None
        else:
            return text

    async def get_attribute(
        self, selector: str, name: str, *, timeout: float | None = None
    ) -> str | None:
        try:
            attribute = await self.page.get_attribute(selector, name, timeout=timeout)  # type: ignore
        except PlaywrightTimeoutError:
            return None
        else:
            return attribute

    async def click(self, selector: str, *, timeout: float | None = None) -> None:
        await self.page.click(selector, timeout=timeout)  # type: ignore

    async def press(
        self, selector: str, key: str, *, timeout: float | None = None
    ) -> None:
        await self.page.press(selector, key, timeout=timeout)  # type: ignore

    async def fill(
        self, selector: str, value: str, *, timeout: float | None = None
    ) -> None:
        await self.page.fill(selector, value, timeout=timeout)  # type: ignore

    async def evaluate(self, expression: str) -> Any:
        return await self.page.evaluate(expression)

    async def type(
        self, selector: str, text: str, *, timeout: float | None = None
    ) -> None:
        await self.page.type(selector, text, timeout=timeout)  # type: ignore

    async def inner_html(
        self, selector: str, *, timeout: float | None = None
    ) -> str | None:
        try:
            html = await self.page.inner_html(selector, timeout=timeout)  # type: ignore
        except PlaywrightTimeoutError:
            return None
        else:
            return html

    @property
    def mouse(self) -> playwright.Mouse:
        return self.page.mouse

    async def content(self) -> str:
        return await self.page.content()

    async def set_content(
        self,
        html: str,
        *,
        timeout: float | None = None,
        wait_until: Literal[
            "commit", "domcontentloaded", "load", "networkidle"
        ] = "load",
    ) -> None:
        await self.page.set_content(html, timeout=timeout, wait_until=wait_until)  # type: ignore

    async def goto(
        self,
        url: str,
        *,
        timeout: float | None = None,
        wait_until: Literal[
            "commit", "domcontentloaded", "load", "networkidle"
        ] = "load",
    ) -> None:
        await self.page.goto(url, timeout=timeout, wait_until=wait_until)  # type: ignore

    async def close(self) -> None:
        await self.page.close()

    async def pause(self) -> None:
        await self.page.pause()

    @property
    def url(self) -> str:
        return self.page.url

    async def screenshot(
        self,
        path: str,
        *,
        full_page: bool = False,
        timeout: float | None = None,
    ) -> bytes | None:
        try:
            screenshot = await self.page.screenshot(
                path=path, full_page=full_page, timeout=timeout  # type: ignore
            )
        except PlaywrightTimeoutError:
            return None

        return screenshot

    async def wait_for_load_state(
        self,
        state: Literal["domcontentloaded", "load", "networkidle"],
        *,
        timeout: float | None = None,
    ) -> None:
        await self.page.wait_for_load_state(state, timeout=timeout)  # type: ignore

    async def wait_for_selector(
        self,
        selector: str,
        *,
        timeout: float | None = None,
        state: Literal["attached", "detached", "hidden", "visible"] | None = None,
    ) -> Node | None:
        if handle := await self.page.wait_for_selector(
            selector, timeout=timeout, state=state  # type: ignore
        ):
            return PlaywrightElementHandle(handle)

        return None

    async def wait_for_timeout(self, timeout: float) -> None:
        await self.page.wait_for_timeout(timeout=timeout)

    async def select_option(
        self,
        selector: str,
        value: str | list[str] | None = None,
        *,
        label: str | list[str] | None = None,
        timeout: float | None = None,
    ) -> list[str]:
        return await self.page.select_option(
            selector, value=value, label=label, timeout=timeout  # type: ignore
        )

    def frame(self, name: str) -> Frame | None:
        return cast(Frame | None, self.page.frame(name))

    def expect_navigation(
        self, *, timeout: float | None = None
    ) -> AsyncEventContextManager[None]:
        return cast(
            AsyncEventContextManager[None],
            self.page.expect_navigation(timeout=timeout),  # type: ignore
        )

    def expect_download(
        self, *, timeout: float | None = None
    ) -> AsyncEventContextManager[Download]:
        return cast(
            AsyncEventContextManager[Download],
            self.page.expect_download(timeout=timeout),  # type: ignore
        )

    def expect_file_chooser(
        self, *, timeout: float | None = None
    ) -> AsyncEventContextManager[FileChooser]:
        return cast(
            AsyncEventContextManager[FileChooser],
            self.page.expect_file_chooser(timeout=timeout),  # type: ignore
        )

    async def check(self, selector: str, *, timeout: float | None = None) -> None:
        await self.page.check(selector, timeout=timeout)  # type: ignore

    async def reload(self, *, timeout: float | None = None) -> None:
        await self.page.reload(timeout=timeout)  # type: ignore


@dataclass(slots=True, frozen=True)
class PlaywrightElementHandle:
    html_element: playwright.ElementHandle

    async def query_selector(self, selector: str) -> Self | None:
        if html_element := await self.html_element.query_selector(selector):
            return PlaywrightElementHandle(html_element)

        return None

    async def query_selector_all(self, selector: str) -> list[Self]:
        return [
            PlaywrightElementHandle(html_element)
            for html_element in await self.html_element.query_selector_all(selector)
        ]

    async def text_content(self) -> str | None:
        return await self.html_element.text_content()

    async def get_attribute(self, name: str) -> str | None:
        return await self.html_element.get_attribute(name)

    async def click(self, *, timeout: float | None = None) -> None:
        await self.html_element.click(timeout=timeout)  # type: ignore

    async def select_option(
        self,
        value: str | list[str] | None = None,
        *,
        label: str | list[str] | None = None,
        timeout: float | None = None,
    ) -> list[str]:
        return await self.html_element.select_option(
            value=value, label=label, timeout=timeout  # type: ignore
        )

    async def scroll_into_view_if_needed(self, *, timeout: float | None = None) -> None:
        await self.html_element.scroll_into_view_if_needed(timeout=timeout)  # type: ignore

    async def focus(self):
        await self.html_element.focus()

    async def is_visible(self) -> bool:
        return await self.html_element.is_visible()

    async def is_enabled(self) -> bool:
        return await self.html_element.is_enabled()

    async def fill(self, value: str, *, timeout: float | None = None) -> None:
        await self.html_element.fill(value, timeout=timeout)  # type: ignore

    async def type(self, text: str, *, timeout: float | None = None) -> None:
        await self.html_element.type(text, timeout=timeout)  # type: ignore

    async def press(self, key: str, *, timeout: float | None = None) -> None:
        await self.html_element.press(key, timeout=timeout)  # type: ignore

    async def inner_html(self) -> str:
        return await self.html_element.inner_html()
