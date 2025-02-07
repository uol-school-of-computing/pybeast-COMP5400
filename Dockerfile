FROM centos:8

# Fix centos repo
RUN cd /etc/yum.repos.d/
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

# Install necessary system libraries for OpenGL rendering
RUN yum install -y mesa-libGL mesa-libGLU mesa-libEGL mesa-dri-drivers mesa-libxatracker
# To fetch conda/mamba miniforge
RUN yum install -y wget
# Install firefox to run notebooks
RUN yum install -y firefox
# Enable sudo user
RUN yum install -y passwd sudo
# Clean up
RUN yum clean all

# Set root pw
RUN echo "root:root" | chpasswd
# Create a non-root student user, set pw to "student" and add user to wheel group so that it can run commands as sudo
RUN useradd -ms /bin/bash student && echo "student:student" | chpasswd && usermod -aG wheel student
# Switch to the new user
USER student
# Go into user home dir
WORKDIR /home/student

# Install mamba miniforge
RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
RUN chmod +x Miniforge3-Linux-x86_64.sh
RUN bash Miniforge3-Linux-x86_64.sh -b -p ~/miniconda
RUN rm Miniforge3-Linux-x86_64.sh

# Add CONDA_DIR/bin to system path so that we can use conda/mamba commands
ENV CONDA_DIR=/home/student/miniconda
ENV PATH=$CONDA_DIR/bin:$PATH

# Copy pybeast in student user home dir
COPY --chown=student:student . pybeast
# Go into pybeast dir
WORKDIR /home/student/pybeast

# Create pybeast environment from yml file
RUN mamba env create -f environment.yml
# Register the new environment as a Jupyter kernel
RUN $CONDA_DIR/envs/pybeast/bin/python -m ipykernel install --user --name pybeast --display-name "Python (pybeast)"

# Add line to .bashrc which activates environment automatically when docker image is run
SHELL ["bash", "-c"]
RUN echo "source activate pybeast" >> ~/.bashrc

# CMD ["python", "./pybeast/besat.py"]

