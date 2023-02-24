import argparse
import os
from pprint import pformat

import lib.logger as logger
from lib.load_charts import LoadCharts


def parse_arguments():
    """
    Parses command line arguments

    Returns: Parsed args as object

    Raises: argparse.ArgumentError exception
    """
    parser = argparse.ArgumentParser(
        description="Road Fatalities website updater")
    parser.add_argument("-f", "--data_file", help="Relative path to "
                        'fatalities data file in csv format inside the project directory',
                        type=str, required=False)
    parser.add_argument("-s", "--compare_start_year", help="Year1 or start year "
                        'for generating comparison statistics between two years.'
                        "Defaults to minimum year in the given data.",
                        type=int, required=False)
    parser.add_argument("-e", "--compare_end_year", help="Year2 or end year "
                        'for generating comparison statistics between two years.'
                        "Defaults to maximum year in the given data.",
                        type=int, required=False)
    parser.add_argument("-d", "--debug", help="Enable debug logs",
                        required=False, action='store_true')

    parsed_args = parser.parse_args()
    if parsed_args.debug:
        logger.set_level(logger.logging.DEBUG)
    return parsed_args


def print_details(parsed_args):
    """
    Print the details related to the run

    Args:
      parsed_args(object): Parsed args
    """
    logger.INFO("Arguments passed:\n%s" % pformat(parsed_args))


def main():
    """
    This method serves as the starting point of the execution
    """
    parsed_args = parse_arguments()
    print_details(parsed_args)
    loader = LoadCharts(parsed_args=parsed_args)
    loader.run()


if __name__ == '__main__':
    main()
