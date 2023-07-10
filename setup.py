from setuptools import setup, find_packages, Extension
from setuptools.command.build_py import build_py

from distutils import dist
import distutils.command.install as dist_install
import os, sys, glob, shutil, pathlib, sysconfig

API_VER = os.environ.get('API_VER', '6.6.9')

# Get the long description from relevant files
with open('README.md', encoding='utf-8') as f:
    readme = f.read()

if sys.platform.startswith('darwin'):
    if API_VER < '6.6.9':
        print('Error: Platform', sys.platform, 'API Version <', API_VER,
              'not supported')
        sys.exit(-1)
    API_DIR = os.path.join('api', API_VER, 'darwin')
    API_LIBS = glob.glob(API_DIR + '/*.a')
    LIB_NAMES = [pathlib.Path(path).stem[3:] for path in API_LIBS]
    INC_DIRS = [API_DIR]
    LIB_DIRS = [API_DIR]
    LINK_ARGS = ['-Wl,-rpath,$ORIGIN']
    COMPILE_ARGS = []
    # COMPILE_ARGS=['-mmacosx-version-min=11.3']
elif sys.platform.startswith('linux'):
    API_DIR = os.path.join('api', API_VER, 'linux')
    API_LIBS = glob.glob(API_DIR + '/*.so')
    LIB_NAMES = [pathlib.Path(path).stem[3:] for path in API_LIBS]
    INC_DIRS = [API_DIR]
    LIB_DIRS = [API_DIR]
    LINK_ARGS = ['-Wl,-rpath,$ORIGIN']
    COMPILE_ARGS = []
elif sys.platform.startswith('win'):
    if API_VER < '6.6.9':
        print('Error: Platform', sys.platform, 'API Version <', API_VER,
              'not supported')
        sys.exit(-1)
    API_DIR = os.path.join('api', API_VER, 'windows')
    API_LIBS = glob.glob(API_DIR + '/*.dll')
    LIB_NAMES = [pathlib.Path(path).stem for path in API_LIBS] + ['iconv']
    INC_DIRS = [
        API_DIR,
        os.path.join(sysconfig.get_config_var('base'), 'Library', 'include')
    ]
    LIB_DIRS = [
        API_DIR,
        os.path.join(sysconfig.get_config_var('base'), 'Library', 'lib')
    ]
    LINK_ARGS = []
    COMPILE_ARGS = ['/utf-8', '/wd4101']
else:
    print('Error: Platform', sys.platform, 'not supported')
    sys.exit(-1)


def get_install_data_dir():
    d = dist.Distribution()
    install_cmd = dist_install.install(d)
    install_cmd.finalize_options()
    return install_cmd.install_data


class BuildPy(build_py):

    def run(self):
        self.run_command('build_ext')
        return super().run()


CTP_EXT = Extension(
    '_ctp',
    ['ctp.i'],
    # ['ctp_wrap.cpp'],
    include_dirs=INC_DIRS,
    library_dirs=LIB_DIRS,
    extra_link_args=LINK_ARGS,
    extra_compile_args=COMPILE_ARGS,
    libraries=LIB_NAMES,
    language='c++',
    swig_opts=['-py3', '-c++', '-threads', '-I' + API_DIR],
)

try:
    for path in glob.glob(API_DIR + '/*.so'):
        shutil.copy(path, './')
    for path in glob.glob(API_DIR + '/*.dll'):
        shutil.copy(path, './')
    setup(
        name='ctp',
        version=API_VER,
        author='Keli Hu',
        author_email='dev@keli.hu',
        description="""CTP for python""",
        long_description=readme,
        url='https://github.com/keli/ctp-python',
        ext_modules=[CTP_EXT],
        py_modules=['ctp'],
        packages=[''],
        package_dir={'': '.'},
        package_data={'': glob.glob('*.so') + glob.glob('*.dll')},
        classifiers=[
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: Implementation :: CPython',
        ],
        cmdclass={
            'build_py': BuildPy,
        },
    )
finally:
    for path in glob.glob('*.so'):
        os.remove(path)
    for path in glob.glob('*.dll'):
        os.remove(path)
