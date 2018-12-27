#!/usr/bin/env python


def remove_deprecated_elements(deprecated, elements, version):
    """Remove deprecated items from a list or dictionary"""
    # Attempt to parse the major, minor, and revision
    (major, minor, revision) = version.split('.')

    # Strings to int and sanitize alphas and betas from revision number
    (major, minor, revision) = (int(major), int(minor), int(revision.split('-')[0]))

    # Iterate over deprecation lists and remove any keys that were deprecated
    # prior to the current version
    for dep in deprecated:
        if (major > dep['major']) \
                or (major == dep['major'] and minor > dep['minor']) \
                or (major == dep['major'] and minor == dep['minor']
                    and revision >= dep['revision']):
            if type(elements) is list:
                for key in dep['keys']:
                    if key in elements:
                        elements.remove(key)
            if type(elements) is dict:
                for key in dep['keys']:
                    if key in elements:
                        del elements[key]
    return elements
