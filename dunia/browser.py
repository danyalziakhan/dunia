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

"""
These Protocols can be used in any case of Browser-like class (such as Playwright's BrowserContext, etc.) for static type checking as long as the implementation contains these methods

Sub-classes don't need to explicitly inherit from it to be used in place of this super-class.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, TypedDict, TypeVar

from dunia.page import Page

if TYPE_CHECKING:

    from typing import Final, Literal

    from typing_extensions import Self

    from dunia.request import Request

SCRIPT_PATH: Final[Path] = Path().absolute()
CACHE_DIR: Final[str] = os.path.join(SCRIPT_PATH, "cache")

PageType = TypeVar("PageType", covariant=True)


class ViewportSize(TypedDict):
    width: int
    height: int


class ProxySettings(TypedDict, total=False):
    server: str
    bypass: str | None
    username: str | None
    password: str | None


@dataclass(slots=True, frozen=True, kw_only=True)
class BrowserConfig:
    """
    Basic Browser config dataclass that can be used in any kind of browser instance (including Chrome, Firefox, etc.) of any type (i.e., Playwright's Browser or BrowserContext with/without cookies storage state file, etc.) making it browser agnostic.
    """

    user_data_dir: Path | str = field(
        default=CACHE_DIR,
        metadata={"help": "Pass an empty string to use a temporary directory instead"},
    )
    headless: bool = field(
        default=True, metadata={"help": "Whether the browser should be displayed"}
    )
    default_navigation_timeout: int = field(
        default=300000,
        metadata={
            "help": "Time in milliseconds to wait for the new page to load while navigating from the previous page (e.g., it is used in goto(), expect_navigation(), etc.)"
        },
    )
    default_timeout: int = field(
        default=30000,
        metadata={
            "help": "Time in milliseconds to wait for the element to get displayed/enabled that has been queried (e.g., it is used in click(), text_content(), etc.)"
        },
    )
    slow_mo: int | None = field(
        default=None,
        metadata={
            "help": "Delay in milliseconds between actions in the browser (slow motion mode) for debugging purposes. Normally this is not needed as we can simply write unit tests for problematic pages or queries"
        },
    )
    accept_downloads: bool = field(
        default=True,
        metadata={
            "help": "Whether to accept the downloads. This must be set to true in markets where downloading is done by the browser/driver"
        },
    )
    viewport: ViewportSize | None = field(
        default=None,
        metadata={
            "help": "Viewport size. By default it does not enforce fixed viewport, allows resizing window in the headed mode"
        },
    )
    devtools: bool = field(
        default=False,
        metadata={
            "help": "Open the devtools when the browser is launched (it doesn't work on Firefox browser)"
        },
    )
    browser: Literal["chromium", "firefox"] = field(
        default="chromium",
        metadata={"help": "Whether to use Chromium or Firefox browser"},
    )
    channel: Literal[
        "",
        "chrome",
        "chrome-beta",
        "chrome-dev",
        "chrome-canary",
        "msedge",
        "msedge-beta",
        "msedge-dev",
        "msedge-canary",
    ] = field(
        default="",
        metadata={
            "help": "Channel to download the browser from. If no value is provided, it will use default browser which needs to be downloaded during Playwright installation"
        },
    )
    locale: str = field(
        default="ko-KR",
        metadata={"help": "Set language locale"},
    )
    proxy: ProxySettings | None = field(
        default=None,
        metadata={"help": "Proxy server configuration"},
    )


class BrowserPageSpawner(Protocol[PageType]):
    async def new_page(self) -> PageType:
        """This is present here so that new_page() for its sub-classes will work regardless of the type of Browser"""
        ...


class BrowserRequestHandle(Protocol):
    @property
    def request(self) -> Request:
        """Returns the Request object for HTTP methods"""
        ...


class Browser(BrowserPageSpawner[Page], BrowserRequestHandle, Protocol):
    pass


class BrowserWithLogin(Browser, Protocol):
    async def login(self) -> Self:
        """Returns the self to enable fluent interface programming"""
        ...


class BrowserWithoutLogin(Browser, Protocol):
    async def create(self) -> Self:
        """Returns the self to enable fluent interface programming"""
        ...
