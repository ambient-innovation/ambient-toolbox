### STAGE 2: Setup ###
FROM python:3.11

# Update OS dependencies
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
ENV AI_CORE_SRC=.
# Directory in container for all project files
ENV AI_CORE_SRVHOME=/src/
# Allow flit to install stuff as root
ENV FLIT_ROOT_INSTALL=1

# Create application subdirectories
WORKDIR $AI_CORE_SRVHOME

# Install Python dependencies
COPY pyproject.toml README.md $AI_CORE_SRVHOME
COPY ambient_toolbox/__init__.py $AI_CORE_SRVHOME/ambient_toolbox/
RUN pip install -U pip flit
RUN flit install --deps all --extras all
# Install dev dependencies - it's ok to do it here because we never deploy this image
RUN pip install .[dev,drf,graphql,view-layer]

# Copy application source code to SRCDIR
COPY $AI_CORE_SRC $AI_CORE_SRVHOME
