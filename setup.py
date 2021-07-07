from setuptools import setup, find_packages

setup(name="ni660x_rpc",
    version="version='0.2.0'",
    description="RPC server for NI660X counter application",
    author="Alba sincotron",
    install_requires=["nidaqmx", "click", "pyyaml",],
    entry_points={
      'console_scripts': [
          'ni660x-rpc-server=ni660x_rpc.rpc.server:main',
      ]
    },
    packages=find_packages(),
    test_suite="test",
    classifiers=["License :: OSI Approved :: GNU General Public License v3 (GPLv3)",],
    license="GNU General Public License v3"
)
