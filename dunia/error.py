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
