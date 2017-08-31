# -*- coding: utf-8 -*-
from mrbob.bobexceptions import ValidationError
from mrbob.bobexceptions import MrBobError
import logging
import os

logger = logging.getLogger("bobtemplates.plone")


def is_string_in_file(configurator, file_path, match_str):
    with open(file_path, 'r+') as xml_file:
        contents = xml_file.readlines()
    for index, line in enumerate(contents):
        if match_str in line:
            return True
    return False


def update_file(configurator, file_path, match_str, insert_str):
    """ Insert insert_str into given file, by match_str.
    """
    with open(file_path, 'r+') as xml_file:
        contents = xml_file.readlines()
        if match_str in contents[-1]:  # Handle last line, prev. IndexError
            contents.append(insert_str)
        else:
            for index, line in enumerate(contents):
                if (match_str in line and
                        insert_str not in contents[index + 1]):
                    contents.insert(index + 1, insert_str)
                    break
        xml_file.seek(0)
        xml_file.writelines(contents)


def _get_package_root_folder():
    file_name = 'setup.py'
    root_folder = None
    cur_dir = os.getcwd()
    while True:
        files = os.listdir(cur_dir)
        parent_dir = os.path.dirname(cur_dir)
        if file_name in files:
            root_folder = cur_dir
            break
        else:
            if cur_dir == parent_dir:
                break
            cur_dir = parent_dir
    return root_folder


def check_root_folder(configurator, question):
    """ Check if we are in a package.
        Should be called in first question pre hook.
    """
    root_folder = _get_package_root_folder()
    if not root_folder:
        raise ValidationError(
            "\n\nNo setup.py found in path!\n"
            "Please run this subtemplate inside an existing package,\n"
            "in the package dir, where the actual code is!\n"
            "In the package collective.dx it's in collective.dx/collective/dx"
            "\n")


def dottedname_to_path(dottedname):
    path = "/".join(dottedname.split('.'))
    return path


def base_prepare_renderer(configurator):
    """ generic rendering before template specific rendering
    """
    configurator.variables['package.root_folder'] = _get_package_root_folder()
    if not configurator.variables['package.root_folder']:
        raise MrBobError("No setup.py found in path!\n")
    configurator.variables['package.dottedname'] = configurator.variables[
        'package.root_folder'].split('/')[-1]
    configurator.variables['package.namespace'] = configurator.variables[
        'package.dottedname'].split('.')[0]
    configurator.variables['package.name'] = configurator.variables[
        'package.dottedname'].split('.')[-1]
    # package.uppercasename = 'COLLECTIVE_FOO_SOMETHING'
    configurator.variables['package.uppercasename'] = configurator.variables[
        'package.dottedname'
    ].replace('.', '_').upper()

    package_subpath = dottedname_to_path(
        configurator.variables['package.dottedname'])
    configurator.variables['package_folder'] = configurator.variables[
        'package.root_folder'] + u'/src/' + package_subpath
    configurator.target_directory = configurator.variables[
        'package.root_folder']
    return configurator
