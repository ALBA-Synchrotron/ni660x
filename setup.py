from setuptools import setup, find_packages

setup(name="ni660x",
    version="0.1",
    description="RPC server for NI660X counter application",
    author="Alba sincotron",
    install_requires=["nidaqmx", "click", "pyyaml",],
    entry_points={
      'console_scripts': [
          'ni660x_rpc=ni660x.application:main',
      ]
    },
    packages=find_packages(),
    test_suite="test",
    classifiers=["License :: OSI Approved :: GNU General Public License v3 (GPLv3)",],
    license="GNU General Public License v3"
)
