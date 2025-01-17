import distutils.command.install as dist_install
import glob
import os
import pathlib
import shutil
import sys
import sysconfig
from distutils import dist

from setuptools import Extension, find_packages, setup
from setuptools.command.build_py import build_py

API_VER = os.environ.get("API_VER", "6.7.7")
REVISION = ""
BUILD_VER = API_VER + "." + REVISION if REVISION else API_VER

# Get the long description from relevant files
with open("README.md", encoding="utf-8") as f:
    readme = f.read()

if sys.platform.startswith("darwin"):
    if API_VER < "6.6.9":
        print(
            "Error: Platform", sys.platform, "API Version <", API_VER, "not supported"
        )
        sys.exit(-1)
    API_DIR = os.path.join("api", API_VER, "darwin")
    if API_VER >= "6.7.7":
        # Handle macOS frameworks
        INC_DIRS = [
            os.path.join(API_DIR, "thostmduserapi_se.framework/Versions/A/Headers"),
            os.path.join(API_DIR, "thosttraderapi_se.framework/Versions/A/Headers"),
        ]
        LIB_DIRS = [API_DIR]
        LIB_NAMES = []
        # Get direct paths to the framework libraries
        MD_LIB = os.path.join(
            API_DIR, "thostmduserapi_se.framework/Versions/A/thostmduserapi_se"
        )
        TRADER_LIB = os.path.join(
            API_DIR, "thosttraderapi_se.framework/Versions/A/thosttraderapi_se"
        )
        API_LIBS = [MD_LIB, TRADER_LIB]
        LINK_ARGS = [
            "-Wl,-rpath,@loader_path",
            MD_LIB,
            TRADER_LIB,
        ]
        COMPILE_ARGS = []
        # Define framework files for package_data
        FRAMEWORK_FILES = ["*.framework", "*.framework/**/*"]
    else:
        # Handle older versions with static libraries
        API_LIBS = glob.glob(API_DIR + "/*.a")
        INC_DIRS = [API_DIR]
        LIB_DIRS = [API_DIR]
        LIB_NAMES = []
        LINK_ARGS = ["-Wl,-rpath,$ORIGIN"]
        LINK_ARGS.extend(API_LIBS)
        COMPILE_ARGS = []
elif sys.platform.startswith("linux"):
    API_DIR = os.path.join("api", API_VER, "linux")
    API_LIBS = glob.glob(API_DIR + "/*.so")
    LIB_NAMES = [pathlib.Path(path).stem[3:] for path in API_LIBS]
    INC_DIRS = [API_DIR]
    LIB_DIRS = [API_DIR]
    LINK_ARGS = ["-Wl,-rpath,$ORIGIN"]
    COMPILE_ARGS = []
elif sys.platform.startswith("win"):
    if API_VER < "6.6.9":
        print(
            "Error: Platform", sys.platform, "API Version <", API_VER, "not supported"
        )
        sys.exit(-1)
    API_DIR = os.path.join("api", API_VER, "windows")
    API_LIBS = glob.glob(API_DIR + "/*.dll")
    LIB_NAMES = [pathlib.Path(path).stem for path in API_LIBS] + ["iconv"]
    INC_DIRS = [
        API_DIR,
        os.path.join(sysconfig.get_config_var("base"), "Library", "include"),
    ]
    LIB_DIRS = [
        API_DIR,
        os.path.join(sysconfig.get_config_var("base"), "Library", "lib"),
    ]
    LINK_ARGS = []
    COMPILE_ARGS = ["/utf-8", "/wd4101"]
else:
    print("Error: Platform", sys.platform, "not supported")
    sys.exit(-1)


def get_install_data_dir():
    d = dist.Distribution()
    install_cmd = dist_install.install(d)
    install_cmd.finalize_options()
    return install_cmd.install_data


package_data = []
if not sys.platform.startswith("darwin"):
    package_data = [os.path.basename(lib) for lib in API_LIBS]
else:
    if API_VER >= "6.7.7":
        package_data = FRAMEWORK_FILES
    else:
        package_data = []


class BuildPy(build_py):
    def run(self):
        # Create the ctp package directory first
        ctp_dir = os.path.join("ctp")
        os.makedirs(ctp_dir, exist_ok=True)

        # Create an empty __init__.py to make it a valid package
        init_path = os.path.join(ctp_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                pass

        self.run_command("build_ext")
        result = super().run()

        # Get the build directory
        build_lib = self.get_finalized_command("build").build_lib
        build_ctp_dir = os.path.join(build_lib, "ctp")

        # Create build ctp directory if it doesn't exist
        os.makedirs(build_ctp_dir, exist_ok=True)

        # Move SWIG-generated ctp.py from current directory to the package directory
        if os.path.exists("ctp.py"):
            shutil.move("ctp.py", os.path.join(build_ctp_dir, "ctp.py"))

        # Update __init__.py content - change the import order
        build_init_path = os.path.join(build_ctp_dir, "__init__.py")
        with open(build_init_path, "w") as f:
            f.write("from ._ctp import *\n")  # Import _ctp first
            f.write("from .ctp import *\n")  # Then import ctp

        # Copy API libraries
        if package_data:
            for lib in API_LIBS:
                lib_name = os.path.basename(lib)
                dst = os.path.join(build_ctp_dir, lib_name)
                if not sys.platform.startswith("darwin"):
                    shutil.copy2(lib, dst)
                else:
                    # Copy the framework to the package directory
                    framework_name = f"{lib_name}.framework"
                    framework_path = os.path.join(API_DIR, framework_name)
                    dst_framework = os.path.join(build_ctp_dir, framework_name)
                    if os.path.exists(dst_framework):
                        shutil.rmtree(dst_framework)

                    def ignore_dsstore(dir, files):
                        return [f for f in files if f == ".DS_Store"]

                    shutil.copytree(
                        framework_path,
                        dst_framework,
                        symlinks=True,
                        ignore=ignore_dsstore,
                    )
        return result


CTP_EXT = Extension(
    "ctp._ctp",
    ["ctp.i"],
    # ['ctp_wrap.cpp'],
    include_dirs=INC_DIRS,
    library_dirs=LIB_DIRS,
    extra_link_args=LINK_ARGS,
    extra_compile_args=COMPILE_ARGS,
    libraries=LIB_NAMES,
    language="c++",
    swig_opts=["-py3", "-c++", "-threads"] + ["-I" + inc for inc in INC_DIRS],
)

try:
    setup(
        name="ctp-python",
        version=BUILD_VER,
        author="Keli Hu",
        author_email="dev@keli.hu",
        description="""CTP for python""",
        long_description=readme,
        long_description_content_type="text/markdown",
        url="https://github.com/keli/ctp-python",
        ext_modules=[CTP_EXT],
        packages=["ctp"],  # Define ctp as a package
        package_data={"ctp": package_data},
        classifiers=[
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "Programming Language :: Python :: Implementation :: CPython",
        ],
        cmdclass={
            "build_py": BuildPy,
        },
    )
finally:
    pass
