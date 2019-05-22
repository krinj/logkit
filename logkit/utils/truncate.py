# -*- coding: utf-8 -*-

"""
Truncates string or JSON data so that it fits a specific number of characters.
"""

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


def truncate(message: str, max_length: int=128, split_ratio: float=0.8) -> str:
    """ Truncates the message if it is longer than max_length. It will be split at the
    'split_ratio' point, where the remaining last half is added on. """
    if max_length == 0 or len(message) <= max_length:
        return message

    split_index_start = int(max_length * split_ratio)
    split_index_end = max_length - split_index_start
    message_segments = [message[:split_index_start], message[-split_index_end:]]
    return " ... ".join(message_segments)

