export WORKDIR=$(realpath $(dirname ${BASH_SOURCE[0]}))

# Powertool utilities
export PATH=${WORKDIR}/powertools/build/bin:${HOME}/powertools/scripts:${PATH}
export LD_LIBRARY_PATH=${WORKDIR}/powertools/build/lib:${LD_LIBRARY_PATH}

# ITSDAQ configuration files
export SCTDAQ_ROOT=${WORKDIR}/itsdaq-sw
export SCTDAQ_VAR=${WORKDIR}/itsdaq-cfg/main
export SCTDB_USER=FU

# Database
if [ -e ${WORKDIR}/setup_db.sh ]; then
    source ${WORKDIR}/setup_db.sh
fi

name=$(basename ${SCTDAQ_VAR})

export PS1="(${name}) ${PS1}"
