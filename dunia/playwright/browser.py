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

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, cast

import playwright.async_api as playwright

from dunia.browser import Browser
from dunia.error import BrowserNotInitialized
from dunia.log import info
from dunia.login import Login
from dunia.playwright.page import PlaywrightPage
from dunia.request import Request

if TYPE_CHECKING:
    from pathlib import Path

    from dunia.browser import BrowserConfig
    from dunia.login import LoginInfo


class PlaywrightBrowser(Browser, Protocol):
    async def new_page(self) -> PlaywrightPage:
        ...

    @property
    def context(self) -> playwright.BrowserContext:
        ...


@dataclass(slots=True, kw_only=True)
class PlaywrightPersistentBrowser:
    """
    This class contains all the possible data/state required for initialization of Playwright browser (Chrome)
    """

    browser_config: BrowserConfig
    playwright: playwright.Playwright


@dataclass(slots=True, kw_only=True)
class PlaywrightBrowserWithLogin(PlaywrightPersistentBrowser):
    """
    Use this class when the market requires login for crawling the information
    """

    login_info: LoginInfo
    __browser_context: playwright.BrowserContext | None = field(
        default=None,
        init=False,
        repr=False,
    )

    async def login(self) -> PlaywrightBrowser:
        login = Login(self.login_info)
        self.__browser_context = await create_playwright_persistent_browser(self)
        await login(self)
        return self

    # ? We only need new_page() from playwright's BrowserContext to make this class API compatible with all the existing markets because we can then simply use PlaywrightBrowser instead of playwright's BrowserContext
    async def new_page(self) -> PlaywrightPage:
        if not self.__browser_context:
            raise BrowserNotInitialized("Please call login() first")

        return PlaywrightPage(await self.context.new_page())

    @property
    def context(self) -> playwright.BrowserContext:
        if not self.__browser_context:
            raise BrowserNotInitialized("Please call login() first")

        return self.__browser_context

    @property
    def request(self) -> Request:
        return cast(Request, self.context.request)


@dataclass(slots=True, kw_only=True)
class PlaywrightBrowserWithoutLogin(PlaywrightPersistentBrowser):
    """
    Use this class when the market doesn't require a login for crawling the information
    """

    __browser_context: playwright.BrowserContext | None = field(
        default=None,
        init=False,
        repr=False,
    )

    async def create(self) -> PlaywrightBrowser:
        self.__browser_context = await create_playwright_persistent_browser(self)
        return self

    # ? We only need new_page() from playwright's BrowserContext to make this class API compatible with all the existing markets because we can then simply use PlaywrightBrowser instead of playwright's BrowserContext
    async def new_page(self) -> PlaywrightPage:
        if not self.__browser_context:
            raise BrowserNotInitialized("Please call create() first")

        return PlaywrightPage(await self.__browser_context.new_page())

    @property
    def context(self) -> playwright.BrowserContext:
        if not self.__browser_context:
            raise BrowserNotInitialized("Please call create() first")

        return self.__browser_context

    @property
    def request(self) -> Request:
        return cast(Request, self.context.request)


async def create_playwright_persistent_browser(
    persistent_browser: PlaywrightPersistentBrowser,
) -> playwright.BrowserContext:
    """
    This creates the browser that saves the cache of visited pages in cache directory configured in BrowserConfig
    """
    if persistent_browser.browser_config.user_data_dir:
        info(
            f"Browser cache directory: <blue>{persistent_browser.browser_config.user_data_dir}</>"
        )
    browser_args: dict[
        str,
        Path
        | str
        | bool
        | list[str]
        | int
        | playwright.ViewportSize
        | playwright.ProxySettings,
    ] = dict(
        user_data_dir=persistent_browser.browser_config.user_data_dir,
        headless=persistent_browser.browser_config.headless,
        channel=persistent_browser.browser_config.channel,
        locale=persistent_browser.browser_config.locale,
        accept_downloads=persistent_browser.browser_config.accept_downloads,
        devtools=persistent_browser.browser_config.devtools,
    )

    if persistent_browser.browser_config.slow_mo:
        browser_args["slow_mo"] = persistent_browser.browser_config.slow_mo

    if persistent_browser.browser_config.viewport:
        browser_args["viewport"] = persistent_browser.browser_config.viewport
    else:
        browser_args["no_viewport"] = True

    if persistent_browser.browser_config.proxy:
        browser_args["proxy"] = persistent_browser.browser_config.proxy

    if persistent_browser.browser_config.browser == "chromium":
        browser = await persistent_browser.playwright.chromium.launch_persistent_context(**browser_args)  # type: ignore
    else:
        browser = await persistent_browser.playwright.firefox.launch_persistent_context(**browser_args)  # type: ignore

    browser.set_default_navigation_timeout(
        persistent_browser.browser_config.default_navigation_timeout
    )
    browser.set_default_timeout(persistent_browser.browser_config.default_timeout)

    return browser


async def close_first_blank_page(browser: PlaywrightBrowser):
    if len(browser.context.pages) > 1 and "about:blank" in browser.context.pages[0].url:
        await browser.context.pages[0].close()


async def main_page_only(browser: PlaywrightBrowser) -> PlaywrightPage:
    new_page = await browser.new_page()
    all_pages = browser.context.pages
    if len(all_pages) > 1:
        for page in all_pages[:-1]:
            await page.close()
    return new_page
