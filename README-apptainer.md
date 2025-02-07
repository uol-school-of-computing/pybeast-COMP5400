## Installation

Build the apptainer container from the `Apptainer.def` by running the
following command from this directory:
```
apptainer build pybeast_latest.sif Apptainer.def
```

## Using prebuilt containers

Both Docker and Apptainer images are prebuilt and hosted in GHCR.  You can
pull these down instead of building from scratch:

### Docker
docker pull ghcr.io/uol-school-of-computing/pybeast:main

### Apptainer
apptainer pull oras://ghcr.io/uol-school-of-computing/pybeast:latest

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

## Notes

If you're looking to develop code with Apptainer, it's in some ways much more
convenient than doing it in Docker on Linux.  Apptainer by default maps the
current directory and /tmp from the host system into the container, so you're
free to store your work directly in a backed up home directory whilst working
in the container, which remains read-only.
