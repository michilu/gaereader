# -*- coding: utf-8 -*-

"""
Self-updating on "hg tag" version number.

How to use
===============

1) Save this file somewhere inside package sources
   (for example src/«MODULE»/version.py)

2) Refer this file from setup.py::

    import os
    execfile(os.path.join(os.path.dirname(__file__), "src", "«MODULE»", "version.py"))

    setup(
       version=VERSION,
       # ...
    )

3) Refer «MODULE».version.VERSION inside the module code (in case version
   number is to be used for something there)

4) In your .hg/hgrc (of your development repo, where you commit and tag)
   write::

    [hooks]
    pre-tag=python:src/«MODULE»/version.py:version_update

   Note: pre-tag, not pretag! In the latter the changeset being tagged
   is already set.

5) Unless you use "1.2.3" or "something-1.2.3" or "something_1-2-3"
   format, review regexps in the code.

What it does
=============

Before actual tag is created, this hook:

- parses tag name, trying to extract version number from it,

- updates it's own code ("VERSION=" line in this file)

- commits the change

Local tags and tags placed by revision are ignored.

Diagnostics
===========

To see more details about hook work, add --verbose or --debug::

    hg tag --verbose sometag-1.2.3

"""

VERSION = "1.2.2"

def version_update(repo, ui, hooktype, pats, opts, **kwargs):
    """
    Method used in mercurial version-update hook. Don't call directly.
    """
    import re
    import mercurial.commands

    # Regexps for handled version number syntaxes
    tag_regexps = [
        # something_1-2-3, something-1.2.3 and similar
        re.compile(r"[^-_0-9][-_](?P<major>[0-9]+)[-_\.](?P<minor>[0-9]+)[-_\.](?P<patch>[0-9]+)$"),
        # 1.2.3, 1-2-3, 1_2_3
        re.compile(r"^(?P<major>[0-9]+)[-_\.](?P<minor>[0-9]+)[-_\.](?P<patch>[0-9]+)$"),
        ]
    # Regexp for VERSION= line
    version_regexp = re.compile(r"^VERSION *= *")

    if opts.get('local'):
        ui.note("Version updater: ignoring local tag\n")
        return
    if opts.get('remove'):
        ui.note("Version updater: ignoring tag removal\n")
        return
    if opts.get('rev'):
        ui.note("Version updater: ignoring tag placed by rev\n")
        return

    if len(pats) != 1:
        ui.warn("Version updater: unexpected arguments, pats=%s\n" % pats)
        return True # means fail

    tag_name = pats[0]

    version_no = None
    for tag_regexp in tag_regexps:
        m = tag_regexp.search(tag_name)
        if m:
            version_no = "{major:>s}.{minor:>s}.{patch:>s}".format(**m.groupdict())
            break
    if not version_no:
        ui.warn("Version updater: Given tag does not seem to be versioned. Please make proper tags (1.2.3, xxxx_1-2-3, xaear-aera-1.2.3 or similar\n")
        return True # means fail

    if version_no == VERSION:
        ui.note("Version updater: version number {0:>s} is already correct\n".format(version_no))
        return False # means OK

    my_name = __file__
    if my_name.endswith(".pyc") or my_name.endswith(".pyo"):
        my_name = my_name[:-1]

    ui.status("Version updater: Replacing old version number {0:>s} with {1:>s} in {2}\n".format(
        VERSION, version_no, my_name))

    file_lines = []
    changes = 0
    with open(my_name, "r") as input:
        for line in input.readlines():
            if version_regexp.search(line):
                file_lines.append('VERSION = "%s"\n' % version_no)
                changes += 1
            else:
                file_lines.append(line)
    if not changes:
        ui.warn("Version updater: Line starting with VERSION= not found in {0:>s}.\nPlease correct this file and retry\n".format(my_name))
        return True #means fail
    with open(my_name, "w") as output:
        output.writelines(file_lines)

    ui.note("Commiting updated version number\n")
    mercurial.commands.commit(
        ui, repo,
        my_name,
        message="Version number set to %s" % version_no)
    return False #means ok
