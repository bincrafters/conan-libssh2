from conans import ConanFile, CMake
import os
import shutil

class libssh2Conan(ConanFile):
    name = "libssh2"
    version = "1.8.0"
    url="https://github.com/Wi3ard/conan-libssh2"
    generators = "cmake", "txt"
    settings = "os", "compiler", "build_type", "arch"
    exports = "cmake/*"
    short_paths = True
    options = {"shared": [True, False],
               "enable_zlib": [True, False],
               "enable_crypt_none": [True, False],
               "enable_mac_none": [True, False],
               "crypto_backend": ["none", "OpenSSL"],
               }
    default_options = "shared=False", \
        "enable_zlib=True", \
        "enable_crypt_none=False", \
        "enable_mac_none=False", \
        "crypto_backend=OpenSSL"

    def source(self):
        self.run("git clone https://github.com/libssh2/libssh2.git")
        self.run("cd libssh2 && git checkout tags/libssh2-1.8.0")

        self.output.info("Copying CMakeLists.txt")
        os.unlink("libssh2/CMakeLists.txt")
        shutil.move("cmake/CMakeLists.txt", "libssh2")

    def config(self):
        if self.options.enable_zlib:
            self.requires.add("zlib/1.2.8@lasote/stable", private=False)
        if self.options.crypto_backend == "OpenSSL":
            self.requires.add("OpenSSL/1.0.2i@lasote/stable", private=False)

    def build(self):
        cmake = CMake(self.settings)

        cmake_options = []
        for option_name in self.options.values.fields:
            activated = getattr(self.options, option_name)
            the_option = "%s=" % option_name.upper()
            if option_name == "shared":
               the_option = "BUILD_SHARED_LIBS=ON" if activated else "BUILD_SHARED_LIBS=OFF"
            elif option_name == "enable_zlib":
               the_option = "ENABLE_ZLIB_COMPRESSION=ON" if activated else "ENABLE_ZLIB_COMPRESSION=OFF"
            elif option_name == "enable_crypt_none":
               the_option = "ENABLE_CRYPT_NONE=ON" if activated else "ENABLE_CRYPT_NONE=OFF"
            elif option_name == "enable_mac_none":
               the_option = "ENABLE_MAC_NONE=ON" if activated else "ENABLE_MAC_NONE=OFF"
            elif option_name == "crypto_backend":
                if activated == "OpenSSL":
                    the_option = "CRYPTO_BACKEND=OpenSSL" if activated else "CRYPTO_BACKEND="
            else:
               the_option += "ON" if activated else "OFF"
            cmake_options.append(the_option)

        cmake_cmd_options = " -D".join(cmake_options)

        cmake_conf_command = 'cmake %s/libssh2 %s -DCMAKE_INSTALL_PREFIX:PATH=install -D%s' % (self.conanfile_directory, cmake.command_line, cmake_cmd_options)
        self.output.warn(cmake_conf_command)
        self.run(cmake_conf_command)

        self.run("cmake --build . --target install %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="install/include")
        self.copy("*.dll", dst="bin", src="install/bin")
        self.copy("*.lib", dst="lib", src="install/lib")
        self.copy("*.a", dst="lib", src="install/lib")
        self.copy("*.so", dst="lib", src="install/lib")
        self.copy("*.*", dst="lib/cmake/libssh2", src="install/lib/cmake/libssh2")
        self.copy("*.*", dst="lib/pkgconfig", src="install/lib/pkgconfig")

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["libssh2"]
        else:
            self.cpp_info.libs = ["ssh2"]

        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.libs.append('ws2_32')
