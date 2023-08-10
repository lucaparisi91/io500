# IO 500 benchmark
The folder `io500` contains the reframe io500 benchmarks.The io500 suite gets downloaded and built each time the test runs.


The benchmarks run the io500 benchmark suite, including ior tests and metadata tests.

Ior tests are not equivalent to benchio as they do not make use of collectives and are designed to test to filesystem and not the mpi layer.

It should be possible to tun tests off by settings the corresponding run entry to false in the configuration file `configBase.ini`. 

The settings which are more likely to change are in `settings.json` file. You can define multiple settings files by setting the  `settings` parameter in `io500.py`. File size Units are in GiB. 
When setting up the test care must be taken in not filling up your quota or overrun the metadata server. The `.json` file also contains the path of the directories where to save the data files and the results. You are responsible for creating the directories and setting up the desired striping.
