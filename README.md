[![Build status](https://ci.appveyor.com/api/projects/status/lexeak2ohlyqa4gh?svg=true)](https://ci.appveyor.com/project/Wi3ard/conan-libssh2)
[![Build Status](https://travis-ci.org/Wi3ard/conan-libssh2.svg?branch=release%2F1.8.0)](https://travis-ci.org/Wi3ard/conan-libssh2)

# conan-libssh2

[Conan.io](https://conan.io) package for [libssh2](https://github.com/libssh2/libssh2) library

The packages generated with this **conanfile** can be found in [conan.io](https://www.conan.io/source/libssh2/1.8.0/Wi3ard/stable).

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py

## Upload packages to server

    $ conan upload libssh2/1.8.0@Wi3ard/stable --all

## Reuse the packages

### Basic setup

    $ conan install libssh2/1.8.0@Wi3ard/stable
    
### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    libssh2/1.8.0@Wi3ard/stable

    [options]
    libssh2:shared=True # False
    
    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:

    conan install . 

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.
