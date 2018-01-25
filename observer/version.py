#!/usr/bin/env python3
# coding=utf-8
# by nearg1e (nearg1e.com@gmail[dot]com)
"""about version.
thx. aploium
"""

from distutils.version import LooseVersion
from utils.common import remove_blank

from utils.common import IS_PY3
from utils.log import LOGGER as logger

# reverse: operator
OPERATOR_MAP = {
    True: "<=",
    False: ">="
}


def str2version(version):
    """to version"""
    if IS_PY3:
        str_types = str
    else:
        str_types = (unicode, str, basestring)
    
    if isinstance(version, str_types):
        return LooseVersion(remove_blank(version))

    return version


def match(static_map, fingerprint):
    """return if fingerprint match or not."""
    def _gen_match():
        for path, filehash in fingerprint.items():
            real_hash = static_map.get(path)
            # LICENSE or file change will make real_hash different
            if filehash and real_hash:
                yield real_hash == filehash
    return all(_gen_match())


def make_version(static_map, fingerprint_map, reverse=True):
    """
    return version expression. compare to each version fingerprint.
    make compare expressions. like [(">=", 'v2.3.3.3')]
    """
    version_compare_set = set()
    key_lst = fingerprint_map.keys()
    version_lst = sorted([str2version(ver_) for ver_ in key_lst], reverse=reverse)

    # head version in reverse version list is different
    head_version_str = version_lst[0].vstring
    fingerprint = head_fingerprint = fingerprint_map.get(head_version_str)
    match_head = match(static_map, head_fingerprint)
    if match_head and reverse:
        version_compare_set.add(('>', version_lst[1].vstring))
    elif match_head and not reverse:
        version_compare_set.add(('>=', head_version_str))

    for version in version_lst[1:]:
        logger.debug('create operator in version: %s', version.vstring)
        fingerprint.update(fingerprint_map.get(version.vstring))
        if match(static_map, fingerprint):
            operator = OPERATOR_MAP.get(reverse)
            version_compare_set.add((operator, version.vstring))
            logger.verbose(
                'create version opreator: %s %s',
                operator, version.vstring
            )
    logger.debug("operator: %s", version_compare_set)
    return version_compare_set


def make_all(static_map, fingerprint):
    """call the make_version"""
    version_compare_set = set()
    version_compare_set.update(
        make_version(static_map, fingerprint.get('fingerprint'))
    )
    version_compare_set.update(
        make_version(static_map, fingerprint.get('reverse_fingerprint'), False)
    )
    return version_compare_set
