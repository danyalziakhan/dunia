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
from typing import TYPE_CHECKING

import playwright.async_api as playwright

from dunia.error import BrowserNotInitialized
from dunia.log import info
from dunia.login import Login
from dunia.playwright._types import PlaywrightBrowser, PlaywrightPage

if TYPE_CHECKING:
    from pathlib import Path

    from dunia.browser import BrowserConfig
    from dunia.login import LoginInfo


@dataclass(slots=True, kw_only=True)
class AsyncPlaywrightBrowser(PlaywrightBrowser):
    """
    This class contains all the possible data/state required for initialization of Playwright browser (Chrome)
    """

    browser_config: BrowserConfig
    playwright: playwright.Playwright
    login_info: LoginInfo | None = None

    __browser_context: playwright.BrowserContext | None = field(
        default=None,
        init=False,
        repr=False,
    )

    async def create(self) -> PlaywrightBrowser:
        self.__browser_context = await create_playwright_persistent_browser(self)
        self._impl_obj = self.__browser_context

        if self.login_info:
            login = Login(self.login_info)
            await login(self)

        return self

    async def new_page(self) -> PlaywrightPage:
        if not self.__browser_context:
            raise BrowserNotInitialized("Please call create() first")

        return await self.__browser_context.new_page()


async def create_playwright_persistent_browser(
    browser: AsyncPlaywrightBrowser,
) -> playwright.BrowserContext:
    """
    This creates the browser that saves the cache of visited pages in cache directory configured in BrowserConfig
    """
    if browser.browser_config.user_data_dir:
        info(
            f"Browser cache directory: <blue>{browser.browser_config.user_data_dir}</>"
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
        user_data_dir=browser.browser_config.user_data_dir,
        headless=browser.browser_config.headless,
        channel=browser.browser_config.channel,
        locale=browser.browser_config.locale,
        accept_downloads=browser.browser_config.accept_downloads,
        devtools=browser.browser_config.devtools,
    )

    if browser.browser_config.slow_mo:
        browser_args["slow_mo"] = browser.browser_config.slow_mo

    if browser.browser_config.viewport:
        browser_args["viewport"] = browser.browser_config.viewport
    else:
        browser_args["no_viewport"] = True

    if browser.browser_config.proxy:
        browser_args["proxy"] = browser.browser_config.proxy

    browser_args["ignore_https_errors"] = True

    if browser.browser_config.browser == "chromium":
        persistent_browser = await browser.playwright.chromium.launch_persistent_context(**browser_args)  # type: ignore
    else:
        persistent_browser = await browser.playwright.firefox.launch_persistent_context(**browser_args)  # type: ignore

    persistent_browser.set_default_navigation_timeout(
        browser.browser_config.default_navigation_timeout
    )
    persistent_browser.set_default_timeout(browser.browser_config.default_timeout)

    return persistent_browser
