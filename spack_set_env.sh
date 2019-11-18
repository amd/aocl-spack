#!/usr/bin/bash

#------------------------------------------------------------------------------
#
# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
#
# Copyright (c) 2019 Advanced Micro Devices, Inc. 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Advanced Micro Devices, Inc. nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#------------------------------------------------------------------------------


#{Function to print command execution status by checking it's return value
execute_and_check()
{
        cmd="$1"
        $cmd
        retVal=$?

        if [[ $retVal -eq 0 ]]; then
                echo "********************************************************"
                echo "Executed : $cmd" >> "${WORKSPACE}/command_executed.txt"
                echo "Executed : $cmd"
                echo "********************************************************"
        else
                echo "########################################################"
                echo "Execution of command : $cmd - was failed"
                echo "Please check ${WORKSPACE}/command_executed.txt file for commands executed till now"
                exit 1
                echo "########################################################"
        fi
}
#}

#{prerequisites
cat << EOF

Spack prerequisites are:

			1) Python 2 (2.6 or 2.7) or 3 (3.5 - 3.8) to run Spack
			2) A C/C++ compiler for building
			3) The make executable for building
			4) The git and curl commands for fetching
			5) If using the gpg subcommand, gnupg2 is required

Make sure you have all these prerequisites in your machine
Check whether spack is installed or not

EOF
#}

#{Declaration and initialization of variables
WORKSPACE=${WORKSPACE:-$PWD}
execute_and_check "rm -rf ${WORKSPACE}/command_executed.txt"
spack_path=""
#}

#{ getopts - For option processing
while getopts :t:s:a:c: opt; do
  case $opt in
    t)
      spack_recipes_tar_path="${OPTARG}"
      echo "AOCL tar path is - ${spack_recipes_tar_path}"
    ;;
    s)
      spack_path="${OPTARG}"
      echo "spack path provided is - ${spack_path}"
    ;;
    h)
      help="${OPTARG}"
      echo "Usage: spack_set_env.sh -t <Path of spack_recipes.tar tar package> -s <Path of Spack path if it is already installed>"
    ;;
    *)
      echo "Usage: spack_set_env.sh -t <Path of spack_recipes.tar tar package> -s <Spack path if it is already installed>"
    ;;
  esac
done
#}

#{ Option processing validation
if [ -z "${spack_recipes_tar_path}" ]; then
	execute_and_check "echo \"Path of AOCL Spack recipe tar file is not given\""
	echo "Usage: spack_set_env.sh -t <Path of spack_recipes.tar tar package> -s <Spack path if it is already installed>"
	exit 1
else
	if [[ "$spack_recipes_tar_path" = /* ]]; then
		spack_recipes_tar_path=${spack_recipes_tar_path}
	else
		spack_recipes_tar_path=${PWD}/${spack_recipes_tar_path}
	fi
fi
#}

if [ -z "${spack_path}" ]; then
	execute_and_check "echo \"spack path value is not given, so setting spack workspace from scratch\""
	if [ ! -d SPACK_SRC ]; then
		execute_and_check "mkdir -p SPACK_SRC"
		execute_and_check "cd SPACK_SRC"
		execute_and_check "git clone https://github.com/spack/spack.git"
		execute_and_check "cd spack"
		export SPACK_ROOT=$PWD
		execute_and_check "git checkout releases/v0.12"
		execute_and_check "cd ../"
		spack_base_path=$PWD
	fi
	echo "****${spack_base_path}****"
else
	export SPACK_ROOT=${spack_path}
	spack_base_path=$(dirname ${spack_path})
	execute_and_check "echo \"We are using existing spack tool, kindly note, AOCL spack recipes are tested with v0.12 release version\""
fi

source ${SPACK_ROOT}/share/spack/setup-env.sh
spack_cmd="${spack_base_path}/spack/bin/spack"
eval "export PATH=${spack_cmd}:$PATH"

execute_and_check "echo \"gcc compiler for AOCL is GCC-9.2.0\""
execute_and_check "echo \"check whether GCC-9.2.0 is installed or not\""
spack_gcc_check=$(${spack_cmd} find gcc@9.2.0)
string_to_look="No package matches the query: gcc@9.2.0"
if [[ ${spack_gcc_check} == *"${string_to_look}"* ]]; then
	echo "GCC-9.2.0 is not installed, so installing"
	execute_and_check "${spack_cmd} install --no-checksum gcc@9.2.0"
	gcc_9_2_0=$(${spack_cmd} location --install-dir gcc@9.2.0)
	execute_and_check "${spack_cmd} compiler find ${gcc_9_2_0}"
fi

execute_and_check "echo \"For Spack load <product> feature, environment-modules are required, so installing...\""
execute_and_check "${spack_cmd} install environment-modules"
module_path=$(${spack_cmd} location --install-dir environment-modules)
execute_and_check "cd ${module_path}/Modules"
execute_and_check "source init/bash"

execute_and_check "echo \"spack root value is - ${spack_base_path}\""
execute_and_check "cd ${spack_base_path}"
execute_and_check "cp -v ${spack_recipes_tar_path} ${spack_base_path}"
execute_and_check "echo \"Extracting ${spack_recipes_tar_path}...\""
execute_and_check "tar -xvf ${spack_recipes_tar_path}"
execute_and_check "${spack_cmd} repo add ${SPACK_ROOT}/var/spack/repos/amd/"
# vim: foldmethod=marker foldmarker=#{,#}
