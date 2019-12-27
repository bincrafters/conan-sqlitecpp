#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration
import os


class SQLiteCppConan(ConanFile):
    name = "sqlitecpp"
    version = "2.3.0"
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
                       "sqlite3:threadsafe": 1,
                       "sqlite3:enable_column_metadata": True
                       }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "sqlite3/3.30.1"
    )

    @property
    def is_mingw_windows(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'gcc' and os.name == 'nt'

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.os == 'Windows' and self.options.shared:
            raise ConanInvalidConfiguration("This library doesn't support dll's on Windows")

    def source(self):
        sha256 = "619386766bc17a125bb1572f998df2ac9a26e1e43f8543167f0a8830b0623ec6"
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = "SQLiteCpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)


    def _patch(self):
        if self.is_mingw_windows:
            tools.replace_in_file(os.path.join(self._source_subfolder, 'CMakeLists.txt'),
                                  'add_compile_options(-fstack-protector -Wall -Wextra -Wpedantic -Wno-long-long -Wswitch-enum -Wshadow -Winline)',
                                  """if (MINGW)
        MESSAGE ( STATUS "Running on MinGW - no -fstack-protector" )
        add_compile_options(-Wall -Wextra -Wpedantic -Wno-long-long -Wswitch-enum -Wshadow -Winline)
    else ()
        add_compile_options(-fstack-protector -Wall -Wextra -Wpedantic -Wno-long-long -Wswitch-enum -Wshadow -Winline)
    endif ()""")

        tools.replace_in_file(os.path.join(self._source_subfolder, 'CMakeLists.txt'),
                              'endif (SQLITECPP_INTERNAL_SQLITE)',
                              """else (SQLITECPP_INTERNAL_SQLITE)
    target_link_libraries(SQLiteCpp PUBLIC CONAN_PKG::sqlite3)
endif (SQLITECPP_INTERNAL_SQLITE)
""")
        if self.settings.compiler == "clang" and \
           Version(self.settings.compiler.version.value) < "6.0" and \
           self.settings.compiler.libcxx == "libc++":
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "include", "SQLiteCpp", "Utils.h"),
                "const nullptr_t nullptr = {};",
                "")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SQLITECPP_INTERNAL_SQLITE"] = False
        if self.options.lint:
            cmake.definitions["SQLITECPP_RUN_CPPLINT"] = 1
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
