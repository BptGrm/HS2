from setuptools import setup, Extension, find_packages
import os
import io
from shutil import copyfile
import platform
import numpy
from distutils.version import LooseVersion

import sys

FOLDER = "herdingspikes/detection_localisation/"

def get_pkg_version():
    version = {}
    version['__file__'] = __file__

    # Because __init__.py in herdingspikes loads packages we may not have installed yet, we need to parse version.py directly
    # (see https://packaging.python.org/guides/single-sourcing-package-version/)
    with open("herdingspikes/version.py") as fp:
        exec(fp.read(), version)

    # Store the commit hash for when we don't have access to git
    with open("herdingspikes/.commit_version", 'w') as cf:
        cf.write(version['__commit__'])

    # Public versions should not contain local identifiers (inspired from mypy)
    if any(cmd in sys.argv[1:] for cmd in ('install', 'bdist_wheel', 'sdist')):
        return version['base_version']
    else:
        return version['__version__']

use_cython = True
# do not use it if cython is not installed
try:
    from Cython.Build import cythonize
    print('Using Cython')
except ImportError:
    use_cython = False
    print('Not using Cython')

if not use_cython:
    copyfile(os.path.join(FOLDER, "detect_python3.cpp"),
             os.path.join(FOLDER, "detect.cpp"))

here = os.path.abspath(os.path.dirname(__file__))
# Get the long description from the README file
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

sources = ["SpkDonline.cpp",
           "SpikeHandler.cpp",
           "ProcessSpikes.cpp",
           "FilterSpikes.cpp",
           "LocalizeSpikes.cpp"]

# if cython and the pyx file are available, compile pyx -> cpp
# otherwise, use the available cpp
if use_cython:
    sources.append("detect.pyx")
else:
    sources.append("detect.cpp")
sources = [FOLDER + s for s in sources]

# OS X support
extra_compile_args = ['-std=c++11', '-O3']
link_extra_args = []
if platform.system() == 'Darwin':
    extra_compile_args += ['-mmacosx-version-min=10.9', '-F.']
    link_extra_args = ["-stdlib=libc++", "-mmacosx-version-min=10.9"]

# compilation of Cython files
detect_ext = Extension(name="herdingspikes.detection_localisation.detect",
                       sources=sources,
                       language="c++",
                       extra_compile_args=extra_compile_args,
                       extra_link_args=link_extra_args,
                       include_dirs=[numpy.get_include(), FOLDER])
if use_cython:
    detect_ext_ready = cythonize(detect_ext)
else:
    detect_ext_ready = [detect_ext]

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.
setup(
    # This is the name of your project. The first time you publish this
    # package, this name will be registered for you. It will determine how
    # users can install this project, e.g.:
    #
    # $ pip install sampleproject
    #
    # And where it will live on PyPI: https://pypi.org/project/sampleproject/
    #
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name='herdingspikes',  # Required

    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=get_pkg_version(),  # Required

    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='Efficient spike detection and sorting for dense MEA',

    # This is an optional longer description of your project that represents
    # the body of text which users will see when they visit PyPI.
    #
    # Often, this is the same as your README, so you can just read it in from
    # that file directly (as we have already done above)
    #
    # This field corresponds to the "Description" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-optional
    long_description=long_description,  # Optional

    # Denotes that our long_description is in Markdown; valid values are
    # text/plain, text/x-rst, and text/markdown
    #
    # Optional if long_description is written in reStructuredText (rst) but
    # required for plain-text or Markdown; if unspecified, "applications should
    # attempt to render [the long_description] as text/x-rst; charset=UTF-8 and
    # fall back to text/plain if it is not valid rst" (see link below)
    #
    # This field corresponds to the "Description-Content-Type" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
    long_description_content_type='text/markdown',  # Optional (see note above)

    # This should be a valid link to your project's main homepage.
    #
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    url='https://github.com/mhhennig/HS2',  # Optional

    # This should be your name or the name of the organization which owns the
    # project.
    author='Matthias Hennig Lab, University of Edinburgh',

    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='m.hennig@ed.ac.uk',  # Optional

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='spikes sorting electrophysiology detection',  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    # py_modules=['herdingspikes/hs2',
    #             'herdingspikes/detection_localisation/detect',
    #             'herdingspikes/probe',
    #             'herdingspikes/parameter_optimisation',
    #             'herdingspikes/clustering/mean_shift_',
    #             'herdingspikes/probe_functions/readUtils'],  # Required
    packages=find_packages(exclude=['contrib', 'documentation', 'tests']),

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    setup_requires=['numpy >= 1.14', 'scipy','cython >= 3.0.0'],
    install_requires=['h5py', 'matplotlib >= 2.0',
                      'pandas', 'scikit-learn >= 0.19.1',
                      'joblib', 'six'],
    python_requires='>=3.6',

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    # extras_require={  # Optional
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    #
    # If using Python 2.6 or earlier, then these have to be included in
    # MANIFEST.in as well.
    package_data={  # Optional
        'herdingspikes': ['.commit_version',
                          'probe_info/neighbormatrix*',  # probe data
                          'probe_info/positions*',
                          # needed for setup's long_description
                          '../README.md',
                          # so that both cpp and pyx come, independently of
                          # use_cython; and headers are also included
                          'detection_localisation/*'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    #
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],  # Optional

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
    ext_modules=detect_ext_ready,
    zip_safe=False,

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={  # Optional
        'Source': 'https://github.com/mhhennig/HS2/',
    },
)

os.remove(os.path.join(FOLDER, "detect.cpp"))
os.remove("herdingspikes/.commit_version")
