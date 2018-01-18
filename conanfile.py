#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class Libssh2Conan(ConanFile):
    name = "libssh2"
    version = "1.8.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "with_pic": [True, False],
               "with_zlib": [True, False],
               "enable_crypt_none": [True, False],
               "enable_mac_none": [True, False],
               "with_openssl": [True, False]
              }
    default_options = "shared=False", \
        "with_pic=True", \
        "with_zlib=True", \
        "enable_crypt_none=False", \
        "enable_mac_none=False", \
        "with_openssl=True"
    url = "https://github.com/bincrafters/conan-libssh2"
    description = "libssh2 is a client-side C library implementing the SSH2 protocol"
    homepage = "https://libssh2.org"
    license = "https://github.com/libssh2/libssh2/blob/master/COPYING"
    short_paths = True
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "dl.patch"]
    generators = "cmake", "txt"
    author = "Bincrafters <bincrafters@gmail.com>"

    def source(self):
        tools.get("https://www.libssh2.org/download/libssh2-%s.tar.gz" % (self.version))
        os.rename("libssh2-%s" % (self.version), "sources")

        if self.settings.compiler != "Visual Studio":
            # Workaround for dl not found by FindOpenSSL for static openssl
            #
            # Although conan-openssl provides 'dl' in the cpp_info,
            # cmake's FindOpenSSL and libssh do not add dl to the OPENSSL_LIBRARIES
            # so linking examples and detecting features does not work.
            #
            # Moreover dl must be added to the end of library list
            tools.patch(patch_file='dl.patch', base_path='sources')

    def requirements(self):
        if self.options.with_zlib:
            self.requires.add("zlib/[~=1.2]@conan/stable", private=False)
        if self.options.with_openssl:
            self.requires.add("OpenSSL/[>1.0.2a,<1.0.3]@conan/stable", private=False)

    def build(self):
        cmake = CMake(self)

        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.with_pic
        cmake.definitions['ENABLE_ZLIB_COMPRESSION'] = self.options.with_zlib
        cmake.definitions['ENABLE_CRYPT_NONE'] = self.options.enable_crypt_none
        cmake.definitions['ENABLE_MAC_NONE'] = self.options.enable_mac_none
        if self.options.with_openssl:
            cmake.definitions['CRYPTO_BACKEND'] = 'OpenSSL'
            cmake.definitions['OPENSSL_ROOT_DIR'] = self.deps_cpp_info['OpenSSL'].rootpath
            cmake.definitions['OPENSSL_ADDITIONAL_LIBRARIES'] = 'dl'
        else:
            raise Exception("Crypto backend must be specified")
        cmake.definitions['BUILD_EXAMPLES'] = False
        cmake.definitions['BUILD_TESTING'] = False
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = 'install'

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("sources/COPYING", dst="licenses", ignore_case=True, keep_path=False)
        self.copy(pattern="*", dst="include", src="install/include")
        self.copy(pattern="*.dll", dst="bin", src="install/bin", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="install/lib", keep_path=False)
        # rhel installs libraries into lib64
        for libarch in ['lib', 'lib64']:
            self.copy(pattern="*.lib", dst="lib", src="install/%s" % libarch, keep_path=False)
            self.copy(pattern="*.a", dst="lib", src="install/%s" % libarch, keep_path=False)
            self.copy(pattern="*.so*", dst="lib", src="install/%s" % libarch, keep_path=False)
            self.copy("*.*", dst="lib/cmake/libssh2", src="install/%s/cmake/libssh2" % libarch)
            self.copy("*.*", dst="lib/pkgconfig", src="install/%s/pkgconfig" % libarch)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.libs.append('ws2_32')
        elif self.settings.os == "Linux":
            # Needed to build bundled examples with openssl
            self.cpp_info.libs.append('dl')
