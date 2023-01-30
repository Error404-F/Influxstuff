# ITk Module Testing Workspace

Common code and configurations necessary for testing an ITk module.

Contains:
- Helpful setup scripts for all software.
- Working version ITSDAQ linked as a submodule.
- Working version of powertools linked as a submodule.
- Template ITSDAQ configuration.
- Configuration files for tested hybrids (from database).
- Configuration files for powerboards (tuned and calibrated).

Make sure to checkout the workspace recurively to get all of the necessary software.

## Instructions

### Compile ITSDAQ
Follow the usual instructions.

```shell
cd itsdaq-sw
python waf configure
python waf build
python waf install
```

### Compile Powertools
Following the usual instructions.

```shell
cmake3 -Spowertools -Bpowertools/build
cmake3 --build powertools/build
```

### Configure InfluxDB
Copy the `setup_db.sh.template` file into `setup_db.sh` and edit it to set the environmental variables corresponding to your setup. See the [ITSDAQ InfluxDB documentation](https://atlas-strips-itsdaq.web.cern.ch/influx.html) for their meaning.

### Setup Script
Source the `setup.sh` script at the start of every session to setup the workspace.

It does the following:
- Setup `SCTDAQ_ROOT` and `SCTDB_USER` variables.
- Set `SCTDAQ_VAR` to `itsdaq-cfg/main` (tracked in workspace).
- Add the Powertools binaries to `PATH`.
- Load InfluxDB configuration (`setup_db.sh`).
