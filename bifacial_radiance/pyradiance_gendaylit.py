# Monkey-patch pyradiance.gendaylit to include -ang functionality
import subprocess as sp
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
import os
import json
import tempfile
from typing import Sequence, NamedTuple
from enum import Enum
from pyradiance.anci import handle_called_process_error, BINPATH


@handle_called_process_error
def gendaylit(
    dt: None | datetime = None,
    latitude: None | float = None,
    longitude: None | float = None,
    timezone: None | int = None,
    altitude: None | float = None,
    azimuth: None | float = None,
    year: None | int = None,
    dirnorm: None | float = None,
    diffhor: None | float = None,
    dirhor: None | float = None,
    dirnorm_illum: None | float = None,
    diffhor_illum: None | float = None,
    solar: bool = False,
    sky_only: bool = False,
    silent: bool = False,
    grefl: None | float = None,
    interval: None | int = None,
) -> bytes:
    """Generates a RADIANCE description of the daylight sources using
    Perez models for direct and diffuse components.

    Args:
        dt: datetime object, mutally exclusive with altitude and azimuth
        latitude: latitude (degrees), only apply if dt is not None
        longitude: longitude (degrees), only apply if dt is not None
        timezone: standard meridian timezone, e.g., 120 for PST, only apply if dt is not None
        altitude: sun altitude, degrees above horizon, mutally exclusive with dt
        azimuth: sun azimuth, degrees west of south, mutally exclusive with dt
        year: Need to set it explicitly, won't use year in datetime object
        dirnorm: direct normal irradiance
        diffhor: diffuse horizontal irradiance
        dirhor: direct horizontal irradiance, either this or dirnorm
        dirnorm_illum: direct normal illuminance
        diffhor_illum: diffuse horizontal illuminance
        solar: if True, include solar position
        sky_only: sky description only
        silent: supress warnings,
        grefl: ground reflectance
        interval: interval for epw data

    Returns:
        output of gendaylit
    """
    cmd = [str(BINPATH / "gendaylit")]
    if dt is not None:
        cmd.append(str(dt.month))
        cmd.append(str(dt.day))
        cmd.append(str(dt.hour + dt.minute / 60 + dt.second / 3600))
        if latitude is not None:
            cmd.extend(["-a", str(latitude)])
        if longitude is not None:
            cmd.extend(["-o", str(longitude)])
        if timezone is not None:
            cmd.extend(["-m", str(timezone)])
        if year is not None:
            cmd += ["-y", str(year)]
    elif None not in (altitude, azimuth):
        cmd.extend(["-ang", str(altitude), str(azimuth)])
    else:
        raise ValueError("pyradiance.gendaylit: Must provide either dt or altitude and azimuth")
    if None not in (dirnorm, diffhor):
        cmd.extend(["-W", str(dirnorm), str(diffhor)])
    elif None not in (dirhor, diffhor):
        cmd.extend(["-G", str(dirhor), str(diffhor)])
    elif None not in (dirnorm_illum, diffhor_illum):
        cmd.extend(["-L", str(dirnorm_illum), str(diffhor_illum)])
    if solar:
        cmd.extend(["-O", "1"])
    if sky_only:
        cmd.append("-s")
    if silent:
        cmd.append("-w")
    if grefl is not None:
        cmd.extend(["-g", str(grefl)])
    if interval is not None:
        cmd.extend(["-i", str(interval)])
    return sp.run(cmd, stderr=sp.PIPE, stdout=sp.PIPE, check=True).stdout
