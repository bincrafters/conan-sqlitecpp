#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class SQLiteCppConan(ConanFile):
    name = "sqlitecpp"
    version = "2.2.0"
    description = "SQLiteCpp is a smart and easy to use C++ sqlite3 wrapper"
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ["conan", "sqlitecpp", "sqlite3"]
    url = "https://github.com/arnesor/conan-sqlitecpp"
    homepage = "https://github.com/SRombauts/SQLiteCpp"
    author = "Arne Sørli <arnese.sorli@kongsberg.frisurf.no>"
    # Indicates License type of the packaged library
    license = "MIT"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]

    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "lint": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "lint": False,
                       "sqlite3:threadsafe": 2,
                       "sqlite3:enable_column_metadata": True,
                       "sqlite3:enable_explain_comments": True,
                       "sqlite3:enable_fts3": True,
                       "sqlite3:enable_json1": True,
                       "sqlite3:enable_rtree": True
                       }

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "sqlite3/3.20.1@bincrafters/stable"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            raise ConanInvalidConfiguration("This library doesn't support dll's on Windows")

    def source(self):
        source_url = "https://github.com/SRombauts/SQLiteCpp.git"
        git = tools.Git(folder=self._source_subfolder)
        git.clone(source_url, "master")
        git.checkout(element=self.version)
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
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
