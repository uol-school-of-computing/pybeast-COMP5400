# pybeast

Python implementation of Bioinspired Evolutionary Agent Simulation Toolkit (BEAST). BEAST is an educational tool to help students to explore concepts of bio-inspired computing and game developement. BEAST provides a modular framework that allows the user to design simple objects and agents within a 2D environment. Agents could for example be representations of animals, robots, or other abstract objects.

## Installation

Build docker container from the `Dockfile` running the following command from this directory

```
docker build -t pybeast:latest .
```

## Usage
After you have build the image you run the container using the command 
```
docker run -it --rm pybeast:latest
```
Within `pybeast` project directory run
```
python test/test_all.py 
```
to check if everything works as expected. To use the pybeast GUI we need to give the container access to the display of our host machine. 

### Linux 

On Linux, this can be achieved by passing additional flags to `docker run` command. First, we need to give docker access to the XDisplayServer of our host machine

```
xhost +local:docker
```

After that run

```
docker run -it --rm --env DISPLAY=$DISPLAY --volume /tmp/.X11-unix:/tmp/.X11-unix pybeast:latest
```
To check if you can display the pybeast GUI on your host machine try to start the beast app from within the container pybeast directory 
```
python pybeast/beast.py
```

To check that the GUI works as expected try to run the Braitenberg demo by selecting the corresponding item in Demos dropdown menu.  



To do the coursework you need to mount the Jupyter notebook into the container so that your changes will be preserved. To achieve this run the following command from within the `pybeast` directory on your host machine    

```
docker run -it --rm --env DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $(pwd)/coursework:/home/student/pybeast/coursework pybeast:latest

```

### Windows & Mac

On windows we need run in XServer through a third party software and connect it to our Linux container.  TODO

## Code Structure

The core functionality of `pybeast` is provided by the packages implemented in the `pybeast/core` directory. All GUI-related code can be found in the `pybeast/gui` directory. Demo experiments are defined in the modules within the `pybeast/demos` directory. To include new demo, simply add a python module to this directory and configure the required flags.

## TODOs

- Implement parallelization: Parallelize runs to enhance runtime performance, as the current code is slow.
- Profile runs and identify bottlenecks: Improve runtime by profiling the code, then optimizing critical subroutines by rewriting them in a low-level language and interfacing with Python.
- Implement automated unit testing: Set up automated unit tests to ensure code maintainability.
- Polish coursework: Refine and finalize the coursework.
- Migrate outstanding demo projects from the C++ codebase: Transition existing demo projects from C++ to Python.

## License Type: 

The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

## Authors and Acknowledgments

  - Orginal codebase developed by TODO
  - Translation and extension to python done by Dr. Lukas Deutz
  - Project maintainers TODO
