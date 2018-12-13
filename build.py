#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default

if __name__ == "__main__":

    builder = build_template_default.get_builder(pure_c=False)
    builder.builds = filter(lambda build: not ((build.settings['compiler'] == 'Visual Studio') and
                                               (build.options['sqlitecpp:shared'] == True)), builder.items)
    builder.run()
