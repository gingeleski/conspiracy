"""consolidate_reqs.py

Updates the top-level requirements.txt after considering requirements from all plugins

"""

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + os.sep + '..')

from plugins import *

import math
import re

#######################################################################################################################

class Requirement:
    """
    Stores information about a Python package required by subcomponents of Conspiracy,
    and considers different version requirements when determining which package version
    to obtain.

    TODO more doc ?
    """

    def __init__(self, name):
        """
        TODO more doc ?
        """
        self.name = name
        self.min_version = '0.0.0'
        self.max_version = '0.0.0'

    def accommodate_another_version(self, specifier, version):
        """
        Accomodates/considers another version of this requirement, updating
        the min and max version fields accordingly

        Params:
            specifier (str)
            version (str)
        """
        if specifier == '==' or specifier == '>=' or specifier == '>':
            # Make this the new minimum if it's greater than existing minimum
            if compare_software_versions(self.min_version, version) < 0:
                self.min_version = version
            # Make this the new maximum if it's greater than existing maximum
            if compare_software_versions(self.max_version, version) < 0:
                self.max_version = version
        elif specifier == '<=' or specifier == '<':
            # Bring the maximum down to this version if it's greater
            if compare_software_versions(self.max_version, version) > 0:
                self.max_version = version
        else:
            raise RuntimeError('Something went wrong with specifier "' + specifier + '" or version "' + version + '"')

class RequirementsHolder:
    """
    TODO document me
    """

    def __init__(self):
        """
        TODO document me
        """
        self.requirements = []

    def add(self, obj_to_add):
        """
        TODO document me
        """
        if len(self.requirements) == 0:
            self.requirements.append(obj_to_add)
        elif len(self.requirements) == 1:
            # TODO
            pass
        else:
            # TODO
            pass

#######################################################################################################################

BROWSER_PAGE_PLUGINS = [cls() for cls in IBrowserPagePlugin.__subclasses__()]
DOMAIN_PLUGINS = [cls() for cls in IDomainPlugin.__subclasses__()]
AUXILIARY_PLUGINS = [cls() for cls in IAuxiliaryPlugin.__subclasses__()]
ALL_PLUGINS = BROWSER_PAGE_PLUGINS + DOMAIN_PLUGINS + AUXILIARY_PLUGINS

#######################################################################################################################

def compare_software_versions(version1, version2):
    """
    Normalizes then compares two software version strings.
    
    Params:
        version1 (str)
        version2 (str)
        
    Returns:
        (int)
    """
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))

def get_reqs_tuple(dep_line):
    """
    Takes in a dependency line (think requirements.txt) then returns
    a tuple where dependency name is index 0, the version specifier is
    index 1, and the version number is in the final index, 2.

    Params:
        req_line (str)

    Returns:
        (tuple)
    """
    if '==' in req_line:
        version_spec = '=='
    elif '>=' in req_line:
        version_spec = '>='
    elif '<=' in req_line:
        version_spec = '<='
    else:
        raise RuntimeError('Unexpected version specifier in dependency string ' + req_line)
    split_req_line_for_tuple = req_line.split(version_spec)
    split_req_line_for_tuple.insert(1, version_spec)
    # Unwanted newlines fix
    if '\n' in split_req_line_for_tuple[2]:
        split_req_line_for_tuple[2] = split_req_line_for_tuple[2][:-1]
    req_tuple = tuple(split_req_line_for_tuple)
    return req_tuple

def consolidate_req_from_multiple(req_tuple_list):
    """
    Takes a list of dependency tuples that are the same package and returns
    just one tuple of the latest possible version.

    Params:
        req_tuple_list (list)

    Returns:
        (tuple)
    """
    # TODO
    return req_tuple_list[0]

def make_requirementstxt_string(reqs):
    """
    Takes a list of dependency tuples and returns a string that can be
    written out as a requirements.txt

    Params:
        reqs (list)

    Returns:
        (str)
    """
    requirementstxt_lines = []
    # Take the requirements list and sort it by first element (package name)
    reqs_sorted = sorted(reqs, key=lambda x : x[0])
    for i, req in enumerate(reqs_sorted):
        # If there's at least one more element
        if len(reqs_sorted) > i + 1:
            # And the name is different than this one
            if req[0] != reqs_sorted[i+1][0]:
                # Just add the package
                this_req_line = req[0] + req[1] + req[2]
                print(this_req_line)
                requirementstxt_lines.append(this_req_line)
            else:
                # Figure out all the versions of this requirement - may have more than two
                this_req_tuples = [req, reqs_sorted[i+1]]
                # Check the subset of requirements after the next one...
                reqs_after_that = reqs_sorted[i+2:] # <- will be empty if the indices don't go that high
                for req_after in reqs_after_that:
                    # Once/if we find a dependency with a different name, break
                    if req_after[0] != req[0]:
                        break
                    this_req_tuples.append(req_after)
                this_req = consolidate_req_from_multiple(this_req_tuples)
                this_req_line = req[0] + req[1] + req[2]
                requirementstxt_lines.append(this_req_line)
    requirementstxt_str = '\n'.join(requirementstxt_lines)
    return requirementstxt_str

#######################################################################################################################

if __name__ == '__main__':
    requirements = []
    reqs_f = open('requirements.txt', 'r')
    req_lines = reqs_f.readlines()
    reqs_f.close()
    for req_line in req_lines:
        # requirements.txt tends to come with weird chars + whitespace from utf-16 so clean this
        clean_req_line = re.sub(r'([^A-Za-z=\d\.])+', '', req_line)
        if 0 == len(clean_req_line):
            continue
        req_tuple = get_reqs_tuple(clean_req_line)
        requirements.append(req_tuple)
    for plugin in ALL_PLUGINS:
        for dep in plugin.requirements:
            req_tuple = get_reqs_tuple(dep)
            requirements.append(req_tuple)
    print('DEBUG START')
    for entry in requirements:
        print(entry)
    print('DEBUG END')
    requirementstxt_str = make_requirementstxt_string(requirements)
    # Write new requirements.txt out as requirements.txt.new before swapping with original
    reqs_new_f = open('requirements.txt.new', 'w')
    reqs_new_f.write(requirementstxt_str)
    reqs_new_f.close()
    # Now delete original requirements.txt
    os.remove('requirements.txt')
    # Finally rename requirements.txt.new as requirements.txt
    os.rename('requirements.txt.new', 'requirements.txt')
