# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

from __future__ import annotations

from typing import TYPE_CHECKING

from colorama import Fore, init
from playwright.async_api import Error, TimeoutError

from dunia.helpers import compile_regex
from dunia.log import warning


if TYPE_CHECKING:
    from typing import Final


init()


class BasicError(Exception):
    __slots__ = ("message", "url")
    __match_args__: Final = ("message", "url")

    def __init__(self, message: Exception | str, url: str | None = None) -> None:
        self.message = message
        self.url = url

        super().__init__(
            (
                Fore.RED
                + str(self.message)
                + Fore.RESET
                + Fore.CYAN
                + f" || {self.url} ||"
            )
            if self.url
            else (Fore.RED + str(self.message) + Fore.RESET)
        )


class LoginInputNotFound(BasicError):
    pass


class NotAbleToLogin(BasicError):
    pass


class BrowserNotInitialized(BasicError):
    pass


class PasswordInputNotFound(BasicError):
    pass


class TimeoutException(BasicError):
    pass


class HTMLParsingError(BasicError):
    pass


PlaywrightTimeoutError = TimeoutError
PlaywrightError = Error


def backoff_hdlr(details: dict[str, int | float]):

    text = "Backing off {wait:0.1f} seconds after {tries} tries calling function {target} with args {args} and kwargs {kwargs}".format(
        **details
    )

    # ? Fix the loguru's mismatch of <> tag for ANSI color directive
    if source := compile_regex(r"\<\w*\>").findall(text):
        text = text.replace(source[0], source[0].replace("<", r"\<"))

    warning(text)
