from conans import ConanFile, CMake, tools
import shutil
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
    license = "https://github.com/libssh2/libssh2/blob/master/COPYING"
    short_paths = True
    exports = "exports/*"
    generators = "cmake", "txt"

    def source(self):
        tools.get("https://www.libssh2.org/download/libssh2-%s.tar.gz" % (self.version))
        os.rename("libssh2-%s" % (self.version), self.name)

        cmakefile = os.path.join(self.name, "CMakeLists.txt")
        shutil.move(cmakefile, os.path.join(self.name, "CMakeListsOriginal.cmake"))
        shutil.move("exports/CMakeLists.txt", cmakefile)

        if self.settings.os == "Linux":
            # Workaround for dl not found by FindOpenSSL for static openssl
            #
            # Although conan-openssl provides 'dl' in the cpp_info,
            # cmake's FindOpenSSL and libssh do not add dl to the OPENSSL_LIBRARIES
            # so linking examples and detecting features does not work.
            #
            # Moreover dl must be added to the end of library list
            self.run("patch -d libssh2 -p0 < exports/dl.patch")

    def requirements(self):
        if self.options.with_zlib:
            self.requires.add("zlib/[~=1.2]@conan/stable", private=False)
            self.options["zlib"].shared = self.options.shared
        if self.options.with_openssl:
            self.requires.add("OpenSSL/[>1.0.2a,<1.0.3]@conan/stable", private=False)
            self.options["OpenSSL"].shared = self.options.shared

    def build(self):
        cmake = CMake(self)

        defs = dict()
        defs['BUILD_SHARED_LIBS'] = self.options.shared
        defs['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.with_pic
        defs['ENABLE_ZLIB_COMPRESSION'] = self.options.with_zlib
        defs['ENABLE_CRYPT_NONE'] = self.options.enable_crypt_none
        defs['ENABLE_MAC_NONE'] = self.options.enable_mac_none
        if self.options.with_openssl:
            defs['CRYPTO_BACKEND'] = 'OpenSSL'
        else:
            raise Exception("Crypto backend must be specified")
        defs['CMAKE_INSTALL_PREFIX'] = 'install'
        if self.options.with_openssl:
            defs['OPENSSL_ADDITIONAL_LIBRARIES'] = 'dl'

        cmake.configure(source_dir=self.name, build_dir="./", defs=defs)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="*", dst="include", src="install/include")
        self.copy(pattern="*.dll", dst="bin", src="install/bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="install/lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="install/lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="install/lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="install/lib", keep_path=False)
        self.copy("*.*", dst="lib/cmake/libssh2", src="install/lib/cmake/libssh2")
        self.copy("*.*", dst="lib/pkgconfig", src="install/lib/pkgconfig")

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()

        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.libs.append('ws2_32')
        elif self.settings.os == "Linux":
            # Needed to build bundled examples with openssl
            self.cpp_info.libs.append('dl')
