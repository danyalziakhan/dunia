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
    handle: playwright.Page

    async def query_selector(self, selector: str) -> Node | None:
        if handle := await self.handle.query_selector(selector):
            return PlaywrightElement(handle)

        return None

    async def query_selector_all(self, selector: str) -> list[Node]:
        return [
            PlaywrightElement(handle)
            for handle in await self.handle.query_selector_all(selector)
        ]

    async def text_content(
        self, selector: str, *, timeout: float | None = None
    ) -> str | None:
        try:
            text = await self.handle.text_content(selector, timeout=timeout)  # type: ignore
        except PlaywrightTimeoutError:
            return None
        else:
            return text

    async def inner_text(
        self, selector: str, *, timeout: float | None = None
    ) -> str | None:
        try:
            text = await self.handle.inner_text(selector, timeout=timeout)  # type: ignore
        except PlaywrightTimeoutError:
            return None
        else:
            return text

    async def get_attribute(
        self, selector: str, name: str, *, timeout: float | None = None
    ) -> str | None:
        try:
            attribute = await self.handle.get_attribute(selector, name, timeout=timeout)  # type: ignore
        except PlaywrightTimeoutError:
            return None
        else:
            return attribute

    async def click(self, selector: str, *, timeout: float | None = None) -> None:
        await self.handle.click(selector, timeout=timeout)  # type: ignore

    async def press(
        self, selector: str, key: str, *, timeout: float | None = None
    ) -> None:
        await self.handle.press(selector, key, timeout=timeout)  # type: ignore

    async def fill(
        self, selector: str, value: str, *, timeout: float | None = None
    ) -> None:
        await self.handle.fill(selector, value, timeout=timeout)  # type: ignore

    async def evaluate(self, expression: str) -> Any:
        return await self.handle.evaluate(expression)

    async def type(
        self, selector: str, text: str, *, timeout: float | None = None
    ) -> None:
        await self.handle.type(selector, text, timeout=timeout)  # type: ignore

    async def inner_html(
        self, selector: str, *, timeout: float | None = None
    ) -> str | None:
        try:
            html = await self.handle.inner_html(selector, timeout=timeout)  # type: ignore
        except PlaywrightTimeoutError:
            return None
        else:
            return html

    @property
    def mouse(self) -> playwright.Mouse:
        return self.handle.mouse

    async def content(self) -> str:
        return await self.handle.content()

    async def set_content(
        self,
        html: str,
        *,
        timeout: float | None = None,
        wait_until: Literal[
            "commit", "domcontentloaded", "load", "networkidle"
        ] = "load",
    ) -> None:
        await self.handle.set_content(html, timeout=timeout, wait_until=wait_until)  # type: ignore

    async def goto(
        self,
        url: str,
        *,
        timeout: float | None = None,
        wait_until: Literal[
            "commit", "domcontentloaded", "load", "networkidle"
        ] = "load",
    ) -> None:
        await self.handle.goto(url, timeout=timeout, wait_until=wait_until)  # type: ignore

    async def close(self) -> None:
        await self.handle.close()

    async def pause(self) -> None:
        await self.handle.pause()

    @property
    def url(self) -> str:
        return self.handle.url

    async def screenshot(
        self,
        path: str,
        *,
        full_page: bool = False,
        timeout: float | None = None,
    ) -> bytes | None:
        try:
            screenshot = await self.handle.screenshot(
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
        await self.handle.wait_for_load_state(state, timeout=timeout)  # type: ignore

    async def wait_for_selector(
        self,
        selector: str,
        *,
        timeout: float | None = None,
        state: Literal["attached", "detached", "hidden", "visible"] | None = None,
    ) -> Node | None:
        if handle := await self.handle.wait_for_selector(
            selector, timeout=timeout, state=state  # type: ignore
        ):
            return PlaywrightElement(handle)

        return None

    async def wait_for_timeout(self, timeout: float) -> None:
        await self.handle.wait_for_timeout(timeout=timeout)

    async def select_option(
        self,
        selector: str,
        value: str | list[str] | None = None,
        *,
        label: str | list[str] | None = None,
        timeout: float | None = None,
    ) -> list[str]:
        return await self.handle.select_option(
            selector, value=value, label=label, timeout=timeout  # type: ignore
        )

    def frame(self, name: str) -> Frame | None:
        return cast(Frame | None, self.handle.frame(name))

    def expect_navigation(
        self, *, timeout: float | None = None
    ) -> AsyncEventContextManager[None]:
        return cast(
            AsyncEventContextManager[None],
            self.handle.expect_navigation(timeout=timeout),  # type: ignore
        )

    def expect_request_finished(
        self, *, timeout: float | None = None
    ) -> AsyncEventContextManager[None]:
        return cast(
            AsyncEventContextManager[None],
            self.handle.expect_request_finished(timeout=timeout),  # type: ignore
        )

    def expect_download(
        self, *, timeout: float | None = None
    ) -> AsyncEventContextManager[Download]:
        return cast(
            AsyncEventContextManager[Download],
            self.handle.expect_download(timeout=timeout),  # type: ignore
        )

    def expect_file_chooser(
        self, *, timeout: float | None = None
    ) -> AsyncEventContextManager[FileChooser]:
        return cast(
            AsyncEventContextManager[FileChooser],
            self.handle.expect_file_chooser(timeout=timeout),  # type: ignore
        )

    async def check(self, selector: str, *, timeout: float | None = None) -> None:
        await self.handle.check(selector, timeout=timeout)  # type: ignore

    async def reload(self, *, timeout: float | None = None) -> None:
        await self.handle.reload(timeout=timeout)  # type: ignore


@dataclass(slots=True, frozen=True)
class PlaywrightElement:
    handle: playwright.ElementHandle

    async def query_selector(self, selector: str) -> Self | None:
        if handle := await self.handle.query_selector(selector):
            return PlaywrightElement(handle)

        return None

    async def query_selector_all(self, selector: str) -> list[Self]:
        return [
            PlaywrightElement(handle)
            for handle in await self.handle.query_selector_all(selector)
        ]

    async def text_content(self) -> str | None:
        return await self.handle.text_content()

    async def get_attribute(self, name: str) -> str | None:
        return await self.handle.get_attribute(name)

    async def click(self, *, timeout: float | None = None) -> None:
        await self.handle.click(timeout=timeout)  # type: ignore

    async def select_option(
        self,
        value: str | list[str] | None = None,
        *,
        label: str | list[str] | None = None,
        timeout: float | None = None,
    ) -> list[str]:
        return await self.handle.select_option(
            value=value, label=label, timeout=timeout  # type: ignore
        )

    async def scroll_into_view_if_needed(self, *, timeout: float | None = None) -> None:
        await self.handle.scroll_into_view_if_needed(timeout=timeout)  # type: ignore

    async def focus(self):
        await self.handle.focus()

    async def is_visible(self) -> bool:
        return await self.handle.is_visible()

    async def is_enabled(self) -> bool:
        return await self.handle.is_enabled()

    async def fill(self, value: str, *, timeout: float | None = None) -> None:
        await self.handle.fill(value, timeout=timeout)  # type: ignore

    async def type(self, text: str, *, timeout: float | None = None) -> None:
        await self.handle.type(text, timeout=timeout)  # type: ignore

    async def press(self, key: str, *, timeout: float | None = None) -> None:
        await self.handle.press(key, timeout=timeout)  # type: ignore

    async def inner_html(self) -> str:
        return await self.handle.inner_html()
