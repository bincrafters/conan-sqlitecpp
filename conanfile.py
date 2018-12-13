#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class SQLiteCppConan(ConanFile):
    name = "sqlitecpp"
    version = "2.2.0"
    description = "SQLiteCpp is a smart and easy to use C++ sqlite3 wrapper"
    topics = ["conan", "sqlitecpp", "sqlite3"]
    url = "https://github.com/bincrafters/conan-sqlitecpp"
    homepage = "https://github.com/SRombauts/SQLiteCpp"
    author = "Arne Sørli <arnese.sorli@kongsberg.frisurf.no>"
    license = "MIT"
    exports = ["LICENSE.md", "LICENSE"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "lint": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "lint": False,
                       "sqlite3:threadsafe": 2,
                       "sqlite3:enable_column_metadata": True
                       }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "sqlite3/3.20.1@bincrafters/stable"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.os == 'Windows' and self.options.shared:
            raise ConanInvalidConfiguration("This library doesn't support dll's on Windows")

    def source(self):
        sha256 = "cd61247c5c9acab3c8a76929c9026e5f2a6daf6bae48d8cd4e9606d045203a28"
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = "SQLiteCpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        tools.replace_in_file(os.path.join(self._source_subfolder, 'CMakeLists.txt'),
                              'endif (SQLITECPP_INTERNAL_SQLITE)',
                              """else (SQLITECPP_INTERNAL_SQLITE)
    target_link_libraries(SQLiteCpp PUBLIC CONAN_PKG::sqlite3)
endif (SQLITECPP_INTERNAL_SQLITE)
""")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SQLITECPP_INTERNAL_SQLITE"] = False
        if self.options.lint:
            cmake.definitions["SQLITECPP_RUN_CPPLINT"] = 1
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
