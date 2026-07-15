"""
The following is a verbatim copy from https://github.com/jnothman/UpSetPlot, the upset plot package developed by
jnothman. This was necessary to implement compatibility with numpy >2.4 and pandas >3.0 since the repository
is not maintained at this point (July 2026). Hopefully, it will be possible to switch back to the package in the future.
NOTE: The following has only been updated to work with the specific plot desired by our analysis script. There is
no guarantee that this code functionally replicates the upsetplot package. Therefore, routines from this subpackage
are not exported at the main package level.
Original license: https://github.com/jnothman/UpSetPlot/blob/master/LICENSE
"""

"""Generic utilities"""
import re

# The below is adapted from an answer to
# https://stackoverflow.com/questions/66822945
# by Andrius at https://stackoverflow.com/a/66869159/1017546
# Reproduced under the CC-BY-SA 3.0 licence.

ODD_REPEAT_PATTERN = r"((?<!{c}){c}({c}{c})*(?!{c}))"
EVEN_REPEAT_PATTERN = r"(?<!{c})({c}{c})+(?!{c})"
SPECIFIER_PATTERN = r"[^(]*[diouxXeEfFgGcs]"  # TODO: handle r


def __to_new_format(fmt: str, named=True):
    def to_named_fmt(fmt):
        pattern = rf"{odd_perc_pattern}\((.*?)\)({SPECIFIER_PATTERN})"
        match = re.search(pattern, fmt)
        while match:
            # Only care about placeholder group here.
            __, __, placeholder, specifier = match.groups()
            fmt = fmt.replace(
                f"%({placeholder}){specifier}", f"{{{placeholder}:{specifier}}}"
            )
            match = re.search(pattern, fmt)
        return fmt

    def to_pos_fmt(fmt):
        even_perc_pattern = EVEN_REPEAT_PATTERN.format(c="%")
        pattern = rf"{even_perc_pattern}s"
        # When positional placeholder has even amount of percents, it
        # will be treated as not having enough arguments passed.
        if re.search(pattern, fmt):
            raise TypeError("not all arguments converted during string formatting")
        return re.sub(
            rf"%({SPECIFIER_PATTERN})",
            lambda sub_match: f"{{:{sub_match.group(1)}}}",
            fmt,
        )

    odd_perc_pattern = ODD_REPEAT_PATTERN.format(c="%")
    # Escape `{` and `}`, because new formatting uses it.
    fmt = fmt.replace("{", "{{").replace("}", "}}")
    fmt = to_named_fmt(fmt) if named else to_pos_fmt(fmt)
    # If we find odd number of occurring percentage symbols, it means
    # those were not escaped and we can't finish conversion.
    if re.search(odd_perc_pattern, fmt):
        raise ValueError("incomplete format")
    return fmt.replace("%%", "%")


def to_new_named_format(fmt: str) -> str:
    """Convert old style named formatting to new style formatting.
    For example: '%(x)s - %%%(y)s' -> '{x} - %{y}'
    Args:
        fmt: old style formatting to convert.
    Returns:
        new style formatting.
    """
    return __to_new_format(fmt, named=True)


def to_new_pos_format(fmt: str) -> str:
    """Convert old style positional formatting to new style formatting.
    For example: '%s - %%%s' -> '{} - %{}'
    Args:
        fmt: old style formatting to convert.
    Returns:
        new style formatting.
    """
    return __to_new_format(fmt, named=False)