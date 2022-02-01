from setuptools import setup, find_packages

setup(name="ni660x",
    version='0.9.2',
    description="RPC server for NI660X counter application",
    author="Alba sincotron",
    install_requires=["nidaqmx", "click", "pyyaml"],
    entry_points={
      'console_scripts': [
          'ni660x-rpc-server=ni660x.rpc.server:main',
      ]
    },
    packages=find_packages(exclude=['test']),
    test_suite="test",
    classifiers=["License :: OSI Approved :: GNU General Public License v3 (GPLv3)",],
    license="GNU General Public License v3",
    python_requires='<=3.10'
)
