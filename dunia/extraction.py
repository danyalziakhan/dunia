# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

from __future__ import annotations

import asyncio
import os

from contextlib import suppress
from typing import TYPE_CHECKING, cast, overload

import backoff
import lxml.html as lxml

from selectolax.lexbor import LexborHTMLParser
from selectolax.parser import HTMLParser
from throttler import throttle

from dunia.aio import with_timeout
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

    from dunia.browser import Browser
    from dunia.html import HTML
    from dunia.page import Page


# ? Sometimes websites are throwing JavaScript exceptions in devtools console, which makes the page stuck on "networkidle", so let's make "load" by default for now
@backoff.on_exception(
    backoff.expo,
    TimeoutException,
    max_tries=5,
    on_backoff=backoff_hdlr,
)
async def visit_link(
    page: Page,
    product_href: str,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):
    """
    Visit the page (url) and retry for 5 times if the navigation has been failed within the configured timeout
    """
    try:
        await page.goto(product_href, wait_until=wait_until)
    except (PlaywrightTimeoutError, PlaywrightError) as err:
        raise TimeoutException(err) from err


async def load_html(
    html: HTML,
):

    return await html.load() if await html.exists() else None


async def load_content(
    *,
    browser: Browser,
    url: str,
    html: HTML,
    page_throttle_rate_limit: int = 10,
    async_timeout: int = 600,
    save_html: bool = True,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):

    if save_html:
        if await html.exists():
            debug(f"Loading content from existing HTML: {html.file}")
            content = await html.load()
        else:
            try:
                debug(f"Fetching content from URL: {url}")
                content = await fetch_content(browser, url, page_throttle_rate_limit)
            except UnicodeDecodeError as err:
                debug(
                    f'Fetching fails due to an error -> "{err}", visiting the URL ({url}) ...'
                )
                visit = with_timeout(async_timeout)(  # type: ignore
                    throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                        visit_link
                    )
                )
                page = await browser.new_page()
                await visit(page, url, wait_until=wait_until)
                content = await page.content()
                await page.close()
            await html.save(content)
    else:
        try:
            debug(f"Fetching content from URL: {url}")
            content = await fetch_content(browser, url, page_throttle_rate_limit)
        except UnicodeDecodeError as err:
            debug(
                f'Fetching fails due to an error -> "{err}", visiting the URL ({url}) ...'
            )
            visit = with_timeout(async_timeout)(  # type: ignore
                throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                    visit_link
                )
            )
            page = await browser.new_page()
            await visit(page, url, wait_until=wait_until)
            content = await page.content()
            await page.close()

    return content


async def reload_content(
    *,
    browser: Browser,
    url: str,
    html: HTML,
    page_throttle_rate_limit: int = 10,
    async_timeout: int = 600,
    save_html: bool = True,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):
    if save_html:
        with suppress(OSError):
            os.remove(html.file)

    try:
        debug(f"Fetching content from URL: {url}")
        content = await fetch_content(browser, url, page_throttle_rate_limit)
    except UnicodeDecodeError as err:
        debug(
            f'Fetching fails due to an error -> "{err}", visiting the URL ({url}) ...'
        )
        visit = with_timeout(async_timeout)(  # type: ignore
            throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                visit_link
            )
        )
        page = await browser.new_page()
        await visit(page, url, wait_until=wait_until)
        content = await page.content()
        await page.close()

    if save_html:
        await html.save(content)

    return content


@backoff.on_exception(
    backoff.expo,
    TimeoutException,
    max_tries=5,
    on_backoff=backoff_hdlr,
)
async def fetch_content(browser: Browser, url: str, rate_limit: int):
    get = throttle(rate_limit=rate_limit, period=1.0)(  # type: ignore
        browser.request.get
    )
    try:
        return cast(str, await (await get(url)).text())
    except (PlaywrightTimeoutError, PlaywrightError) as err:
        raise TimeoutException(err) from err
    except UnicodeDecodeError as err:
        raise err from err


async def load_page(
    *,
    browser: Browser,
    url: str,
    html: HTML,
    page_throttle_rate_limit: int = 10,
    async_timeout: int = 600,
    save_html: bool = True,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):

    if save_html:
        if await html.exists():
            debug(f"Loading content from existing HTML: {html.file}")
            content = await html.load()
            page = await browser.new_page()
            await page.set_content(content, wait_until=wait_until)
        else:
            debug(f"Visiting the URL ({url}) ...")
            visit = with_timeout(async_timeout)(  # type: ignore
                throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                    visit_link
                )
            )
            page = await browser.new_page()
            await visit(page, url, wait_until=wait_until)
            content = await page.content()
            await html.save(content)
    else:
        debug(f"Visiting the URL ({url}) ...")
        visit = with_timeout(async_timeout)(  # type: ignore
            throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                visit_link
            )
        )
        page = await browser.new_page()
        await visit(page, url, wait_until=wait_until)

    return page


async def reload_page(
    *,
    browser: Browser,
    url: str,
    html: HTML,
    page_throttle_rate_limit: int = 10,
    async_timeout: int = 600,
    save_html: bool = True,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):
    if save_html:
        with suppress(OSError):
            os.remove(html.file)

    debug(f"Visiting the URL ({url}) ...")
    visit = with_timeout(async_timeout)(  # type: ignore
        throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
            visit_link
        )
    )
    page = await browser.new_page()
    await visit(page, url, wait_until=wait_until)
    content = await page.content()

    if save_html:
        await html.save(content)

    return page


@overload
async def parse_document(
    content: str,
    *,
    engine: Literal["lxml"],
) -> LXMLDocument | None:
    ...


@overload
async def parse_document(
    content: str,
    *,
    engine: Literal["modest"],
) -> ModestDocument | None:
    ...


@overload
async def parse_document(
    content: str,
    *,
    engine: Literal["lexbor"],
) -> LexborDocument | None:
    ...


async def parse_document(
    content: str,
    *,
    engine: Literal["lxml", "modest", "lexbor"] = "lxml",
) -> LXMLDocument | ModestDocument | LexborDocument | None:
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


@overload
async def parse_document_from_url(
    browser: Browser,
    url: str,
    *,
    page_throttle_rate_limit: int,
    async_timeout: int,
    engine: Literal["lxml"],
) -> LXMLDocument:
    ...


@overload
async def parse_document_from_url(
    browser: Browser,
    url: str,
    *,
    page_throttle_rate_limit: int,
    async_timeout: int,
    engine: Literal["modest"],
) -> ModestDocument:
    ...


@overload
async def parse_document_from_url(
    browser: Browser,
    url: str,
    *,
    page_throttle_rate_limit: int,
    async_timeout: int,
    engine: Literal["lexbor"],
) -> LexborDocument:
    ...


async def parse_document_from_url(
    browser: Browser,
    url: str,
    *,
    page_throttle_rate_limit: int = 10,
    async_timeout: int = 600,
    engine: Literal["lxml", "modest", "lexbor"] = "lxml",
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
) -> LXMLDocument | ModestDocument | LexborDocument:

    page = await browser.new_page()
    visit = with_timeout(async_timeout)(  # type: ignore
        throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
            visit_link
        )
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
