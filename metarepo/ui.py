"""Command line user interface helpers"""
from typing import Tuple, Union

import click
from colorama import Fore, Style

CHECK_MARK = "\u2713"
CROSS_MARK = "\u2717"
BULLET = "\u2022"


def format_info(message):
    """
    Format information message
    :param message: Message to format
    """
    return f"{Fore.BLUE}{message}{Style.RESET_ALL}"


def info(message):
    """
    Print information message
    :param message: Message to print
    """
    click.echo(format_info(message))


def format_error(message):
    """
    Format error message
    :param message: Message to format
    """
    return f"{Fore.RED}{message}{Style.RESET_ALL}"


def error(message):
    """
    Print error message
    :param message: Message to print
    """
    click.echo(format_error(message))


def format_item_symbol(symbol: str, message: str, *attributes: Union[Tuple[str, str], str]):
    """
    Format one item with custom symbol
    :param symbol: Symbol
    :param message: Message to format
    :param attributes: List of extra attributes to format
    """
    formatted_attributes = []
    for attribute in attributes:
        if isinstance(attribute, str):
            formatted_attributes.append(attribute)
        else:
            formatted_attributes.append(f"{attribute[0]}:{Fore.CYAN}{attribute[1]}{Style.RESET_ALL}")

    if formatted_attributes:
        attributes = f" ({' '.join(formatted_attributes)})"
    else:
        attributes = ""

    return f"  {symbol}{Style.RESET_ALL} {message}{attributes}"


def format_item(message: str, *attributes: Union[Tuple[str, str], str]):
    """
    Format one list item
    :param message: Message to format
    :param attributes: List of extra attributes to format
    """
    return format_item_symbol(f"{Fore.LIGHTBLUE_EX}{BULLET}", message, *attributes)


def format_item_ok(message: str, *attributes: Union[Tuple[str, str], str]):
    """
    Format one successful list item
    :param message: Message to format
    :param attributes: List of extra attributes to format
    """
    return format_item_symbol(f"{Fore.GREEN}{CHECK_MARK}", message, *attributes)


def format_item_error(message: str, err: str):
    """
    Format one error list item
    :param message: Message to format
    :param err: Error details
    """
    return format_item_symbol(f"{Fore.RED}{CROSS_MARK}", message, f"{Fore.RED}{err}{Fore.RESET}")


def item(message: str, *attributes: Union[Tuple[str, str], str]):
    """
    Print one list item
    :param message: Message to format
    :param attributes: List of extra attributes to format
    """
    click.echo(format_item(message, *attributes))


def item_ok(message: str, *attributes: Union[Tuple[str, str], str]):
    """
    Print one successful list item
    :param message: Message to format
    :param attributes: List of extra attributes to format
    """
    click.echo(format_item_ok(message, *attributes))


def item_error(message: str, err: str):
    """
    Print one error list item
    :param message: Message to format
    :param err: Error details
    """
    click.echo(format_item_error(message, err))
