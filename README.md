Ni660x
===============

- [`The purpose of the project`](#The-purpose-of-the-project).
- [`How to install`](#How-to-install).
- [`How to use`](#How-to-use).

The purpose of the project
---------------
The purpose of this project is to translate the NI library from C to python. To use and make the devices compatible with the new systems.

How to install
---------------

#### 1. Install the drivers
[Download and Install NI Driver Software on Linux Desktop](https://www.ni.com/es-es/support/documentation/supplemental/18/downloading-and-installing-ni-driver-software-on-linux-desktop.html).

#### 2. Install the library

The project contains a setup.py. If you have the python3 environment installed, you only have to execute this file like that:

> python setup.py .

How to use
---------------

#### 1. Create your config.yalm file
The configuration file is necessary
to configure the connections, timer, counter and other parameters to start the device.

The program need a .yaml file.

##### Example:
In the directory "/config" you have some examples about how to write this file.

#### 2. Init the program
Run the program with your configuration file and leave it in background . After that you can execute your programs or test the operation.
You could run the program like this:
> python -m ni660x ['configuration file']
##### Example:
> python -m ni660x config/config03.yaml

#### 3. Execute
When the program is running you can execute the programs.

The arguments you need to execute the program depends of the own program.
##### Example:
> python test_scan.py 100 0.1 1

In this example the arguments are:
1. The number of samples.
2. The time in seconds you take one samples.
3. Number of repetitions of the scan