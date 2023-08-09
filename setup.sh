SETUP=main
if [ ${#} == 1 ]; then
    SETUP=${1}
fi

export WORKDIR=$(realpath $(dirname ${BASH_SOURCE[0]}))

# Powertool utilities
export PATH=${WORKDIR}/powertools/build/bin:${HOME}/powertools/scripts:${PATH}
export LD_LIBRARY_PATH=${WORKDIR}/powertools/build/lib:${LD_LIBRARY_PATH}

# ITSDAQ configuration files
export SCTDAQ_ROOT=${WORKDIR}/itsdaq-sw
export SCTDAQ_VAR=${WORKDIR}/itsdaq-cfg/${SETUP}
export SCTDB_USER=FU
export ITSDAQ_LOCATION=BHAM_COLDJIG

# Database
if [ -e ${WORKDIR}/setup_db.sh ]; then
    source ${WORKDIR}/setup_db.sh
fi

export PS1="(${SETUP}) ${PS1}"
