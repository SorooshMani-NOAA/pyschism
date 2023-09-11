import tempfile
from datetime import timedelta, datetime
from pathlib import Path

import f90nml

from pyschism.mesh import Hgrid
from pyschism.driver import ModelConfig


def _util_create_driver(crs):
    # For the sake of test it doesn't matter if the grid dims are 
    # REALLY geographic or not, we can fake it as such by passing
    # the crs we want!
    hgrid = Hgrid.open(
        'https://raw.githubusercontent.com/geomesh/test-data/main/NWM/hgrid.ll',
        crs=crs,
    )

    config = ModelConfig(
        hgrid=hgrid,
        vgrid=None,
        fgrid=None,
        iettype=None,
        ifltype=None,
        nws=None,
    )

    driver = config.coldstart(
        start_date=datetime(2023, 9, 2),
        end_date=datetime(2023, 9, 18),
        timestep=timedelta(seconds=300),
        nspool=24,
    )

    return driver


def test_ncor_is_written_for_0():

    driver = _util_create_driver('epsg:3857')
    with tempfile.TemporaryDirectory() as dirname:
        tmpdir = Path(dirname)
        driver.write(tmpdir / 'ncor_0', overwrite=True)
       
        nml = f90nml.read(tmpdir / 'ncor_0' / 'param.nml')

        assert('ncor' in nml['opt']) # ncor is written
        assert(nml['opt']['ncor'] == 0) # projected grid


def test_ncor_is_written_for_1():

    driver = _util_create_driver('epsg:4326')
    with tempfile.TemporaryDirectory() as dirname:
        tmpdir = Path(dirname)
        driver.write(tmpdir / 'ncor_0', overwrite=True)
        
        nml = f90nml.read(tmpdir / 'ncor_0' / 'param.nml')

        assert('ncor' in nml['opt']) # ncor is written
        assert(nml['opt']['ncor'] == 1) # geoegrpahic grid
