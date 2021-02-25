Ni660x
===============

- The purpose of the project
- How to install
- [`How to use`](#How-to-use).

The purpose of the project
---------------

How to install
---------------


How to use
---------------

#### 1. Create your config.yalm file
The configuration file is necessary
to configure the connections, timer, counter and other parameters to start the device.

The program need a .yaml file.

##### Example:
In the directory "/config" you have some examples about how to write this file.

#### 2. Init the program

##### Example:
> python -m ni660x config/config03.yaml
#### 3. Execute
##### Example:
> python test_scan.py 100 0.1 1
