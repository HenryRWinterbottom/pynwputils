# =========================================================================

# Module: launch/container_interface.py

# Author: Henry R. Winterbottom

# Email: henry.winterbottom@noaa.gov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the respective public license published by the
# Free Software Foundation and included with the repository within
# which this application is contained.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

# =========================================================================

"""

Requirements
------------

- docker; https://github.com/docker

- golang; https://github.com/golang/go

- singularity; https://github.com/sylabs/singularity

Author(s)
---------

    Henry R. Winterbottom; 09 December 2022

History
-------

    2022-12-09: Henry Winterbottom -- Initial implementation.

"""

# ----


# ----

import os
from schema import Optional
import subprocess

from execute import subprocess_interface
from utils import schema_interface
from utils.error_interface import msg_except_handle
from utils.exceptions_interface import ContainerInterfaceError
from utils.logger_interface import Logger
from tools import parser_interface
from tools import system_interface

# ----

# Define all available functions.
__all__ = ["build_sfd_local"]

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----

# Define the schema attributes for the respective functions.
sfd_local_schema = {
    "docker_image": str,
    "sif_name": str,
    Optional("build_sandbox", default=False): bool,
    Optional("docker_tag", default="latest"): str,
    Optional("docker_image", default=None): str,
    Optional("sandbox_name", default=None): str,
    Optional("sif_group", default=None): str,
    Optional("sif_user", default=None): str,
    Optional("update_owner", default=False): bool,
}

# ----

logger = Logger()

# ----


@msg_except_handle(ContainerInterfaceError)
def __error__(msg: str = None) -> None:
    """
    Description
    -----------

    This function is the exception handler for the respective module.

    Parameters
    ----------

    msg: str

        A Python string containing a message to accompany the
        exception.

    """


# ----


def __sandbox__():
    """ """


# ----


def _check_docker_env() -> str:
    """
    Description
    -----------

    This function checks whether the Docker environment has been
    loaded; if not, an ContainerInterfaceError will be thrown; if so,
    the path to the Docker executable (docker) will be defined and
    returned.

    Returns
    -------

    docker: str

        A Python string specifying the path to the Docker executable
        (docker).

    Raises
    ------

    ContainerInterfaceError:

        * raised if the Docker executable path cannot be determined.

    """

    docker = system_interface.app_path(app="docker")

    if docker is None:
        msg = (
            "The Docker application could not be determined; "
            "either install the application or if it is already install, "
            "update the runtime PATH environment variable. Aborting!!!"
        )
        __error__(msg=msg)

    return docker


# ----


def _check_singularity_env() -> str:
    """
    Description
    -----------

    This function checks whether the Singularity environment has been
    loaded; if not, an ContainerInterfaceError will be thrown; if so,
    the path to the Singularity executable (singularity) will be
    defined and returned.

    Returns
    -------

    singularity: str

        A Python string specifying the path to the Singularity
        executable (singularity).

    Raises
    ------

    ContainerInterfaceError:

        * raised if the Singularity executable path cannot be
          determined.

    """

    singularity = system_interface.app_path(app="singularity")
    if singularity is None:
        msg = (
            "The singularity application could not be determined; "
            "either install the application or if it is already install, "
            "update the runtime PATH environment variable. Aborting!!!"
        )
        __error__(msg=msg)

    return singularity


# ----


def build_sandbox_local(build_dict: dict):
    """ """


# ----


def build_sfd_local(build_dict: dict, stderr: str = None, stdout: str = None) -> None:
    """
    Description
    -----------

    This method builds a Singularity image from am exiting Docker
    containerized image using the attributes provided upon entry.

    Parameters
    ----------

    build_dict: dict

        A Python dictionary containing the attributes necessary to
        build a Singularity image from an existing Docker
        containerized image.

    """

    # Define and validate the schema for the Singularity container
    # build configuration; proceed accordingly.
    cls_opts = build_dict
    schema_interface.validate_opts(cls_schema=sfd_local_schema, cls_opts=cls_opts)

    # Define the attributes and the respective default values required
    # to build the Singularity image from the respective Docker
    # containerized image.
    sfd_attrs_dict = {
        "build_sandbox": False,
        "docker_tag": "latest",
        "docker_image": None,
        "sandbox_name": None,
        "sif_group": None,
        "sif_name": None,
        "sif_user": None,
        "update_owner": False,
    }

    # Define the mandatory attributes required to build the
    # Singularity image.
    sfd_manattrs_list = ["docker_image", "sif_name"]

    # Parse the attributes provided upon entry and build the local
    # Python object; proceed accordingly.
    sfd_obj = parser_interface.object_define()
    for sfd_key, sfd_value in sfd_attrs_dict.items():
        # Define the attribute value, if any passed, provided upon
        # entry; proceed accordingly.
        attr_value = parser_interface.dict_key_value(
            dict_in=build_dict, key=sfd_key, force=True, no_split=True
        )

        if (sfd_key in sfd_manattrs_list) and (attr_value is None):
            msg = (
                f"The attribute {sfd_key} must not be NoneType when "
                "building Singularity images from Docker containerized "
                "images. Aborting!!!"
            )
            __error__(msg=msg)

        sfd_obj = parser_interface.object_setattr(
            object_in=sfd_obj, key=sfd_key, value=attr_value
        )

    # Establish the respective platform singularity application
    # executable.
    singularity = _check_singularity_env()

    # Build the Singularity image locally.
    args = ["build"]
    if sfd_obj.build_sandbox:
        args = args + ["--sandbox"]
    kwargs = {
        "args": args
        + [f"{sfd_obj.sif_name}", f"{sfd_obj.docker_image}:{sfd_obj.docker_tag}"],
        "job_type": "app",
        "errlog": stderr,
        "outlog": stdout,
    }

    subprocess_interface.run(exe=singularity, **kwargs)

    # Check whether permissions are to be assigned for the respective
    # Singularity containerized image; proceed accordingly.
    if sfd_obj.update_owner:
        # Define the user to be defined as the container owner.
        if sfd_obj.sif_user is None:
            sfd_obj.sif_user = system_interface.user()

        # Change the ownership of the container to the respective
        # user.
        msg = (
            f"Changing owner of Singularity containerized image {sfd_obj.sif_name} "
            f"to {sfd_obj.sif_user}."
        )
        logger.warn(msg=msg)
        system_interface.chown(
            path=sfd_obj.sif_name, user=sfd_obj.sif_user, group=sfd_obj.sif_group
        )

    return sfd_obj.sif_name
