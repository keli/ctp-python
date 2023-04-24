from setuptools import setup, find_packages, Extension
from setuptools.command.build_py import build_py

from distutils import dist
import distutils.command.install as dist_install
import os, sys, glob, shutil, pathlib

API_VER = os.environ.get('API_VER', '6.6.1')

if sys.platform.startswith('darwin'):
    if API_VER < '6.6.9':
        print('Error: Platform', sys.platform, 'API Version <', API_VER, 'not supported')
        sys.exit(-1)
    API_DIR='api/' + API_VER + '/darwin'
elif sys.platform.startswith('linux'):
    API_DIR='api/' + API_VER + '/linux'
else:
    print('Error: Platform', sys.platform, 'not supported')
    sys.exit(-1)

API_LIBS=glob.glob(API_DIR + '/*.so') + glob.glob(API_DIR + '/*.a')
API_NAMES=[pathlib.Path(path).stem[3:] for path in API_LIBS]

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
    include_dirs=[API_DIR],
    library_dirs=[API_DIR],
    extra_link_args=['-Wl,-rpath,$ORIGIN'],
    #extra_compile_args=['-mmacosx-version-min=11.3'],
    #libraries=['thostmduserapi', 'thosttraderapi'],
    libraries=API_NAMES,
    language='c++',
    swig_opts=['-py3', '-c++', '-threads', '-I./' + API_DIR],
)

try:
    for path in glob.glob(API_DIR + '/*.so'):
        shutil.copy(path, './')
    setup(
        name='ctp',
        version=API_VER,
        author='Keli Hu',
        author_email='dev@keli.hu',
        description="""CTP for python""",
        ext_modules=[CTP_EXT],
        py_modules=['ctp'],
        packages=[''],
        package_dir={'': '.'},
        package_data={'': glob.glob('*.so')},
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
