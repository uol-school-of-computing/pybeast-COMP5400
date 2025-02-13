## Installation
The following instructions have been tested on Linux RHL9. Please note, we recommend the **Apptainer instructions**.

Build the apptainer container from the `Apptainer.def` by running the
following command from this directory:
```
apptainer build pybeast_latest.sif Apptainer.def
```
### Apptainer
apptainer pull oras://ghcr.io/uol-school-of-computing/pybeast:latest

## Using prebuilt containers

Both Docker and Apptainer images are prebuilt and hosted in GHCR.  You can
pull these down instead of building from scratch:

### Docker
docker pull ghcr.io/uol-school-of-computing/pybeast:main

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

If you modify the code, you need to run the following commands before rerunning pyBEAST:

```
cd pybeast-COMP5400
module add comp5400
runBEAST
```

## Notes

If you're looking to develop code with Apptainer, it's in some ways much more
convenient than doing it in Docker on Linux.  Apptainer by default maps the
current directory and /tmp from the host system into the container, so you're
free to store your work directly in a backed up home directory whilst working
in the container, which remains read-only.

pyBEAST can be run locally or remotely. 
