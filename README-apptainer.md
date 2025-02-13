## Installation
The following instructions have been tested on Linux RHL9. Please note, we recommend the **Apptainer instructions**.

Build the apptainer container from the `Apptainer.def` by running the
following command from this directory:
```
apptainer build pybeast_latest.sif Apptainer.def
```
### Apptainer
apptainer pull oras://ghcr.io/uol-school-of-computing/pybeast-comp5400:latest

## Using prebuilt containers

Both Docker and Apptainer images are prebuilt and hosted in GHCR.  You can
pull these down instead of building from scratch:

### Docker
docker pull ghcr.io/uol-school-of-computing/pybeast-comp5400:main

## Usage

Once you have the container image, you can run commands directly in the
container like this:
```
apptainer run pybeast_latest.sif python /opt/pybeast/beast.py
```

If you wanted an shell within the container:

```
apptainer run pybeast_latest.sif bash -i
```

### School of Computer Science Linux systems
You can skip downloading or build in the container if you're running this on our
internal Linux systems, as it's already been downloaded, and is available in a module.
To use this, assuming you're within the directory of the checked out repository, you can do:

```
module add comp5400
runBEAST
```

This simple uses a wrapper script to run the beast.py entrypoint within the Apptainer container.

## Notes

If you're looking to develop code with Apptainer, it's in some ways much more
convenient than doing it in Docker on Linux.  Apptainer by default maps the
current directory and /tmp from the host system into the container, so you're
free to store your work directly in a backed up home directory whilst working
in the container, which remains read-only.

pyBEAST can be run locally or remotely. 
