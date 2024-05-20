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
from typing import TYPE_CHECKING, Any, cast

import backoff
import lxml.html as lxml
from async_lru import alru_cache  # type: ignore
from charset_normalizer import detect
from selectolax.lexbor import LexborHTMLParser
from selectolax.parser import HTMLParser
from throttler import throttle

from dunia.aio import with_timeout
from dunia.document import Document
from dunia.error import (
    HTMLParsingError,
    PlaywrightError,
    PlaywrightTimeoutError,
    TimeoutException,
    backoff_hdlr,
)
from dunia.lexbor import LexborDocument
from dunia.log import debug
from dunia.lxml import LXMLDocument
from dunia.modest import ModestDocument

if TYPE_CHECKING:
    from typing import Literal

    from dunia.html import HTML
    from dunia.playwright._types import PlaywrightBrowser, PlaywrightPage


# ? Sometimes websites are throwing JavaScript exceptions in devtools console, which makes the page stuck on "networkidle", so let's make "load" by default for now
@backoff.on_exception(
    backoff.expo,
    TimeoutException,
    max_tries=5,
    on_backoff=backoff_hdlr,  # type: ignore
)
async def visit_link(
    page: PlaywrightPage,
    url: str,
    *,
    timeout: int | None = None,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
) -> None:
    """
    Visit the page (url) and retry for 5 times if the navigation has been failed within the configured timeout
    """
    try:
        await page.goto(url, timeout=timeout, wait_until=wait_until)
    except (PlaywrightTimeoutError, PlaywrightError) as err:
        raise TimeoutException(err) from err


async def load_html(
    html: HTML,
) -> str | None:
    """
    Utility function to load the html page with "None" type checking/narrowing
    """
    return await html.load() if await html.exists() else None


async def load_content(
    *,
    browser: PlaywrightBrowser,
    url: str,
    html: HTML,
    on_failure: Literal["fetch", "visit", "fetch_first", "visit_first"] | None = None,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
    async_timeout: int = 600,
    rate_limit: int = 10,
) -> str:
    """
    Load HTML content

    Read from the file if it exists on disk, otherwise fetch it with Browser using HTTP's GET request

    If the request fails and 'strict' is False, then visit the URL
    """

    if await html.exists():
        debug(f"Loading content from existing HTML: {html.file}")
        content = await html.load()

    match on_failure:
        case None:
            raise FileNotFoundError("HTML content is not present on disk")
        case "fetch" | "fetch_first":
            try:
                debug(
                    f"HTML content is not present on disk. Fetching content from URL: {url}"
                )
                content = await fetch_content(browser, url, rate_limit)
            except UnicodeDecodeError as err:
                if on_failure == "fetch":
                    raise err from err

                # ? In the case of "fetch_first"
                debug(
                    f"Fetching failed due to an error ({err}). Visiting the URL ({url}) ..."
                )
                try:
                    visit_link_with_timeout = with_timeout(async_timeout)(  # type: ignore
                        throttle(rate_limit=rate_limit, period=1.0)(visit_link)  # type: ignore
                    )

                    page = await browser.new_page()
                    await visit_link_with_timeout(page, url, wait_until=wait_until)
                    content = await page.content()
                    await page.close()
                except TimeoutException as err:
                    raise err from err

        case "visit" | "visit_first":
            debug(f"HTML content is not present on disk. Visiting the URL ({url}) ...")

            try:
                visit_link_with_timeout = with_timeout(async_timeout)(  # type: ignore
                    throttle(rate_limit=rate_limit, period=1.0)(visit_link)  # type: ignore
                )

                page = await browser.new_page()
                await visit_link_with_timeout(page, url, wait_until=wait_until)
                content = await page.content()
                await page.close()
            except TimeoutException as err:
                if on_failure == "visit":
                    raise err from err

                # ? In the case of "visit_first"
                try:
                    debug(
                        f"Visiting failed due to an error ({err}). Fetching the URL ({url}) ..."
                    )
                    content = await fetch_content(browser, url, rate_limit)
                except UnicodeDecodeError as err:
                    raise err from err

    return content


@backoff.on_exception(
    backoff.expo,
    TimeoutException,
    max_tries=5,
    on_backoff=backoff_hdlr,  # type: ignore
)
async def fetch_content(
    browser: PlaywrightBrowser, url: str, rate_limit: int, encoding: str | None = None
) -> str:
    """
    Use the Browser to send HTTP's GET request and receive the content response

    If encoding is not provided, then it will try to find the encoding from content body

    If it fails, then encoding will be detected using `charset_normalizer`
    """
    get = throttle(rate_limit=rate_limit, period=1.0)(  # type: ignore
        browser.request.get
    )

    try:
        response: Any = await get(url)
    except (PlaywrightTimeoutError, PlaywrightError) as err:
        raise TimeoutException(err) from err

    body = cast(bytes, await response.body())

    if encoding:
        return body.decode(encoding)

    try:
        content_type = response.headers["content-type"]
    except KeyError:
        detected_encoding = await detect_encoding(body)
        debug(f"Detected encoding: {detected_encoding}")

        return body.decode(detected_encoding)
    else:
        debug(f"Content-Type: {content_type}")

        if "charset=" in content_type:
            content_encoding = content_type.split("charset=")[-1].strip()
            debug(f"Content encoding: {content_encoding}")

            return body.decode(content_encoding)
        else:
            detected_encoding = await detect_encoding(body)
            debug(f"Detected encoding: {detected_encoding}")

            return body.decode(detected_encoding)


@alru_cache
async def detect_encoding(content: bytes) -> str:
    """
    Find the most probable encoding of the content
    """
    encoding = await asyncio.to_thread(detect, content)
    return encoding["encoding"]  # type: ignore


async def load_page(
    *,
    browser: PlaywrightBrowser,
    url: str,
    html: HTML,
    on_failure: Literal["fetch", "visit", "fetch_first", "visit_first"] | None = None,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
    async_timeout: int = 600,
    rate_limit: int = 10,
) -> PlaywrightPage:
    """
    Create a new page in the browser and visit the URL
    """
    if await html.exists():
        debug(f"Loading content from existing HTML: {html.file}")
        content = await html.load()
        page = await browser.new_page()
        await page.set_content(content, wait_until=wait_until)

    match on_failure:
        case None:
            raise FileNotFoundError("HTML content is not present on disk")
        case "fetch" | "fetch_first":
            try:
                debug(
                    f"HTML content is not present on disk. Fetching content from URL: {url}"
                )
                content = await fetch_content(browser, url, rate_limit)
            except UnicodeDecodeError as err:
                if on_failure == "fetch":
                    raise err from err

                # ? In the case of "fetch_first"
                debug(
                    f"Fetching failed due to an error ({err}). Visiting the URL ({url}) ..."
                )
                try:
                    visit_link_with_timeout = with_timeout(async_timeout)(  # type: ignore
                        throttle(rate_limit=rate_limit, period=1.0)(visit_link)  # type: ignore
                    )

                    page = await browser.new_page()
                    await visit_link_with_timeout(page, url, wait_until=wait_until)
                    content = await page.content()
                    await page.set_content(content, wait_until=wait_until)
                except TimeoutException as err:
                    raise err from err
            else:
                page = await browser.new_page()
                await page.set_content(content, wait_until=wait_until)

        case "visit" | "visit_first":
            debug(f"HTML content is not present on disk. Visiting the URL ({url}) ...")

            try:
                visit_link_with_timeout = with_timeout(async_timeout)(  # type: ignore
                    throttle(rate_limit=rate_limit, period=1.0)(visit_link)  # type: ignore
                )

                page = await browser.new_page()
                await visit_link_with_timeout(page, url, wait_until=wait_until)
                content = await page.content()
                await page.set_content(content, wait_until=wait_until)
            except TimeoutException as err:
                if on_failure == "visit":
                    raise err from err

                # ? In the case of "visit_first"
                try:
                    debug(
                        f"Visiting failed due to an error ({err}). Fetching the URL ({url}) ..."
                    )
                    content = await fetch_content(browser, url, rate_limit)
                except UnicodeDecodeError as err:
                    raise err from err
                else:
                    page = await browser.new_page()
                    await page.set_content(content, wait_until=wait_until)

    return page


async def parse_document(
    content: str,
    *,
    engine: Literal["lxml", "modest", "lexbor"] = "lxml",
) -> Document | None:
    """
    Parse the HTML content using the specified parser ("lxml", "modest", "lexbor")

    Return document object
    """
    if engine == "lxml":
        try:
            tree = cast(lxml.HtmlElement, await asyncio.to_thread(lxml.fromstring, content))  # type: ignore
        except lxml.etree.ParserError:
            return None

        return LXMLDocument(tree)

    elif engine == "lexbor":
        try:
            tree = await asyncio.to_thread(LexborHTMLParser, content)
        except Exception:
            return None

        return LexborDocument(tree)

    elif engine == "modest":
        try:
            tree = await asyncio.to_thread(HTMLParser, content)
        except Exception:
            return None

        return ModestDocument(tree)

    raise ValueError(
        f'Wrong engine type: {engine}\nSupported engines: ["lxml", "modest", "lexbor"]'
    )


async def parse_document_from_url(
    browser: PlaywrightBrowser,
    url: str,
    *,
    rate_limit: int = 10,
    async_timeout: int = 600,
    engine: Literal["lxml", "modest", "lexbor"] = "lxml",
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
) -> Document:
    """
    Visit the URL and parse the HTML content using the specified parser ("lxml", "modest", "lexbor")

    Return document object if parsing is successful, however, unlike parse_document(), it raises an HTMLParsingError exception if parsing is failed
    """
    page = await browser.new_page()
    visit = with_timeout(async_timeout)(  # type: ignore
        throttle(rate_limit=rate_limit, period=1.0)(visit_link)  # type: ignore
    )
    await visit(page, url, wait_until=wait_until)
    content = await page.content()
    await page.close()

    if engine == "lxml":
        try:
            tree = cast(
                lxml.HtmlElement,
                await asyncio.to_thread(lxml.fromstring, content),  # type: ignore
            )
        except lxml.etree.ParserError as err:
            raise HTMLParsingError(
                f'Could not parse LXML document due to an error -> "{err}"'
            ) from err

        return LXMLDocument(tree)

    elif engine == "lexbor":
        try:
            tree = await asyncio.to_thread(LexborHTMLParser, content)
        except Exception as err:
            raise HTMLParsingError(
                f'Could not parse LEXXBOR document due to an error -> "{err}"'
            ) from err

        return LexborDocument(tree)

    elif engine == "modest":
        try:
            tree = await asyncio.to_thread(HTMLParser, content)
        except Exception as err:
            raise HTMLParsingError(
                f'Could not parse MODEST document due to an error -> "{err}"'
            ) from err

        return ModestDocument(tree)

    raise ValueError(
        f'Wrong engine type: {engine}\nSupported engines: ["lxml", "modest", "lexbor"]'
    )
