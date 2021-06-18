import sys
import calendar
from collections.abc import Iterable
from typing import List, Union, NamedTuple, Dict

from pathlib import Path
import tempfile

# {january: 1, february: 2, ...}
MONTH_NUMBER_ = {
    month.lower(): index for index, month in enumerate(calendar.month_name) if month
}


def month_number_from_name(name_of_the_month: str) -> int:
    """Retrieves the month number from the name of the month

    Examples:
        >>> print(month_number_from_name("JaNuAry"))
        1

    """
    return MONTH_NUMBER_[name_of_the_month.lower()]


def parse_nums(value: str) -> float:
    """Parses a string to a floating number, if it contains % divide by 100

    Examples:
        >>> parse_nums("12")
        12.0
        >>> parse_nums("4%")
        0.04

    """
    if "%" in value:
        value = value.replace("%", "")
        return float(value) / 100
    return float(value)


def list_of_strings_2_floats(strings: List[str]) -> List[float]:
    """Parses a list of strings to a list of floating numbers.

    If the list of strings contains strings with % these are removed
    and the affected strings are divided by 100

    Examples:
        >>> print(list_of_strings_2_floats(['2000', '1000', '500']))
        [2000.0, 1000.0, 500.0]
        >>> print(list_of_strings_2_floats(['-10.00%', '40.00%', '0.00%']))
        [-0.1, 0.4, 0.0]

    """
    return [parse_nums(string) for string in strings]


def read_file_2_list(_file_path: str = str(Path().absolute())) -> List[List[str]]:
    """Takes in a filepath and outputs its content as a list of lists

    Args:
        _file_path (str): A path to a file to be read.

    Returns:
        a list of lists of strings where each string is a word (or text)
        seperated by whitespace in the original file

    Examples:
        >>> with tempfile.NamedTemporaryFile() as tmpfile:
        ...     tmpfile.write(b'ALLOCATE 6000 3000\\nCHANGE 13.00% MAY\\nBALANCE MARCH') and True
        ...     tmpfile.flush()
        ...     read_file_2_list(_file_path=tmpfile.name)
        True
        [['ALLOCATE', '6000', '3000'], ['CHANGE', '13.00%', 'MAY'], ['BALANCE', 'MARCH']]
    """
    with open(_file_path, "r") as fp:
        return [line.strip().split() for line in fp.readlines()]


class Command(NamedTuple):
    """Named tuple of investor commands: name, values, month

    Common names: "balance", "allocate", "sip", "change",
    Values = [1000, 2000, 3000, 4000, 5000, ...],
    month = 1, 2, 3, ..., 12

    """

    name: str = ""
    values: Dict[str, float] = dict()
    month: int = 0


def parse_list_2_commands(
    list_of_commands: List[List[str]], asset_order: List[str]
) -> Iterable[Command]:
    """Summary line.

    This takes in a list of commands in a nested text format, and parses
    the output into three categories: name, values and month. These three
    categories are inserted into a namedtuple, and yielded.

    Args:
        list_of_commands: Input is a list of text commands, which again are
                          split into strings

    Yields:
        int: A NamedTupe called Command(name, value, month)

    Examples:
        >>> str_commands = [["ALLOCATE", "6000", "3000"], ["CHANGE", "13.00%", "MAY"], ["BALANCE", "MARCH"]]
        >>> asset_order = ["Gold", "Equity"]
        >>> commands = [i for i in parse_list_2_commands(str_commands, asset_order)]
        >>> print(commands[0])
        Command(name='allocate', values={'Gold': 6000.0, 'Equity': 3000.0}, month=0)
        >>> print(commands[1])
        Command(name='change', values={'Gold': 0.13}, month=5)
        >>> print(commands[2])
        Command(name='balance', values={}, month=3)

    """
    for commands in list_of_commands:
        command, values, month = "", dict(), 0

        if len(commands) < 2:
            if commands:
                command = commands[0]
                yield Command(name=command.lower(), values=values, month=month)
            continue

        command, *remaining = commands
        last_command_is_a_month_name = remaining[-1].lower() in MONTH_NUMBER_

        if last_command_is_a_month_name:
            *string_values, month_name = remaining
            month = month_number_from_name(month_name)
        else:
            string_values = remaining

        values = list_of_strings_2_floats(string_values)
        yield Command(
            name=command.lower(), values=dict(zip(asset_order, values)), month=month
        )


def bank_rounding_system(allocation: Union[str, float]) -> int:
    """
    This determines how the allocations are rounded, for instance
    we can use 'round(balance, 2)' to round to 2 decimal places
    """
    return int(allocation)


class Asset:
    def __init__(self, name: str, allocations: float = 0, weight: int = 0):
        self.name = name
        self._allocation = 0
        self.allocation = allocations
        self.weight = weight

    @property
    def weight(self) -> int:
        return self._weight

    @weight.setter
    def weight(self, weight: int) -> None:
        if weight < 0 or weight > 100:
            raise ValueError("The weight of the asset has to be in the range 0 to 100")
        self._weight = weight

    @property
    def allocation(self) -> int:
        return self._allocation

    @allocation.setter
    def allocation(self, allocation) -> None:
        self._allocation = bank_rounding_system(allocation)

    def monthly_rate_of_change(self, rate: float) -> None:
        self.allocation *= 1 + rate

    def __str__(self) -> str:
        return f"{self.name} {self.allocation} {self.weight}"


class InvestorPortfolio:
    def __init__(self, name: str, assets: dict[str, Asset]):
        self.name = name
        self.assets = assets

        total_weights = sum(asset.weight for asset in self.assets.values())
        if total_weights != 100:
            raise ValueError(
                "The sum of your portofolio must equal 100%, please update your distribution of assets."
            )

        self.sip: Dict[str, float] = dict(
            zip(self.assets.keys(), [float(0)] * len(self.assets))
        )

    def allocate(self, values: Dict[str, float]) -> None:
        for name, value in values.items():
            self.assets[name].allocation += value

    def add_sip(self) -> None:
        self.allocate(self.sip)

    def change(self, rates: Dict[str, float]) -> None:
        for name, rate in rates.items():
            self.assets[name].monthly_rate_of_change(rate)

    def rebalance(self) -> None:
        total_allocation = sum(asset.allocation for asset in self.assets.values())
        for asset in self.assets.values():
            asset.allocation = total_allocation * asset.weight / 100

    def balance(self) -> List[float]:
        return [asset.allocation for asset in self.assets.values()]


class MoneyBank:
    NAME = "MoneyBank"
    INITIAL_MONTH = 1
    SIP_MONTH = 2
    REBALANCE_MONTHS = [6, 12]
    REBALANCE_ERROR_MSG = "CANNOT_REBALANCE"

    def __init__(self, investors: List[InvestorPortfolio]):
        self.initial_month = self.INITIAL_MONTH

        self.investors = dict()
        for investor in investors:
            self.investors[investor.name] = investor

        self.log = dict()
        for i in range(len(MONTH_NUMBER_)):
            self.log[i] = dict()

    def allocate(self, name: str, values: Dict[str, List[float]]) -> None:
        self.investors[name].allocate(values)

    def sip(self, name: str, sip_amounts: Dict[str, List[float]]):
        self.investors[name].sip = sip_amounts

    def change(self, name: str, rates: Dict[str, List[float]], month: int) -> None:
        self.current_month = month
        if self.current_month >= self.SIP_MONTH:
            self.investors[name].add_sip()
        self.investors[name].change(rates)
        self.log[month][name] = [
            asset.allocation for asset in self.investors[name].assets.values()
        ]

    def balance(self, name: str, month: int) -> List[int]:
        return [val for val in self.log[month][name]]

    def rebalance(self, name: str) -> bool:
        if self.current_month not in self.REBALANCE_MONTHS:
            print(self.REBALANCE_ERROR_MSG)
            return False
        else:
            self.investors[name].rebalance()
            self.log[self.current_month][name] = [
                asset.allocation for asset in self.investors[name].assets.values()
            ]
        return True

    def execute_investor_commands(
        self,
        investor_name: str,
        list_of_commands: List[List[str]],
        assets_order: List[str],
    ) -> None:
        for command, values, month in parse_list_2_commands(
            list_of_commands, assets_order
        ):
            if command == "allocate":
                self.allocate(investor_name, values)
            elif command == "sip":
                self.sip(investor_name, values)
            elif command == "change":
                self.change(investor_name, values, month)
            elif command == "balance":
                print(*self.balance(investor_name, month))
            elif command == "rebalance":
                if self.rebalance(investor_name):
                    print(*self.balance(investor_name, self.current_month))


def main():
    input_file = sys.argv[1]
    #
    # sys.argv[1] should give the absolute path to the input file
    # parse the file and process the command
    # print the output

    investor_name = "John Doe"
    asset_order = ["Equity", "Debt", "Gold"]
    weights = [60, 30, 10]
    investors_assets_ = dict(
        zip(
            asset_order,
            [
                Asset(name=name, weight=weight)
                for name, weight in zip(asset_order, weights)
            ],
        )
    )

    investor = InvestorPortfolio(investor_name, investors_assets_)
    list_of_commands = read_file_2_list(input_file)
    moneybank = MoneyBank([investor])
    moneybank.execute_investor_commands(investor.name, list_of_commands, asset_order)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    doctest.testmod(extraglobs={"asset": Asset("test")})
    main()
