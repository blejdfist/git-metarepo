"""Command line user interface helpers"""
from typing import Tuple, Union
from colorama import Fore, Style

CHECK_MARK = "\u2713"
CROSS_MARK = "\u2717"
BULLET = "\u2022"


def info(message):
    """
    Print information message
    :param message: Message to print
    """
    print(f"{Fore.BLUE}{message}{Style.RESET_ALL}")


def item_symbol(symbol: str, message: str, *attributes: Union[Tuple[str, str], str]):
    """
    Format and print one item with custom symbol
    :param symbol: Symbol
    :param message: Message to print
    :param attributes: List of extra attributes to format
    """
    formatted_attributes = []
    for attribute in attributes:
        if isinstance(attribute, str):
            formatted_attributes.append(attribute)
        else:
            formatted_attributes.append(f"{attribute[0]}:{Fore.CYAN}{attribute[1]}{Style.RESET_ALL}")

    print(f"  {symbol}{Style.RESET_ALL} {message} ({' '.join(formatted_attributes)})")


def item(message: str, *attributes: Union[Tuple[str, str], str]):
    """
    Format and print one list item
    :param message: Message to print
    :param attributes: List of extra attributes to format
    """
    item_symbol(f"{Fore.LIGHTBLUE_EX}{BULLET}", message, *attributes)


def item_ok(message: str, *attributes: Union[Tuple[str, str], str]):
    """
    Format and print one successful list item
    :param message: Message to print
    :param attributes: List of extra attributes to format
    """
    item_symbol(f"{Fore.GREEN}{CHECK_MARK}", message, *attributes)


def item_error(message: str, error: str):
    """
    Format and print one error list item
    :param message: Message to print
    :param error: Error details
    """
    item_symbol(f"{Fore.RED}{CROSS_MARK}", message, f"{Fore.RED}{error}{Fore.RESET}")
