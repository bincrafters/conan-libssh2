from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="libssh2:shared", pure_c=True)
    noefence_builds = []
    for settings, options in builder.builds:
        noefence_builds.append([settings, dict(options.items() + [('OpenSSL:no_electric_fence', True)])])
    builder.builds = noefence_builds
    builder.run()
