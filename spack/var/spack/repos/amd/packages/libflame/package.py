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
from spack import *


class Libflame(AutotoolsPackage):
    """libFLAME is a portable library for dense matrix computations,
    providing much of the functionality present in Linear Algebra 
    Package (LAPACK). It includes a compatibility layer, FLAPACK, 
    which includes complete LAPACK implementation. The library 
    provides scientific and numerical computing communities with a 
    modern, high-performance dense linear algebra library that is 
    extensible, easy to use, and available under an open source 
    license. libFLAME is a C-only implementation and does not 
    depend on any external FORTRAN libraries including LAPACK. 
    There is an optional backward compatibility layer, lapack2flame
    that maps LAPACK routine invocations to their corresponding 
    native C implementations in libFLAME. This allows legacy 
    applications to start taking advantage of libFLAME with 
    virtually no changes to their source code.
    In combination with BLIS library which includes optimizations
    for the AMD EPYCTM processor family, libFLAME enables running 
    high performing LAPACK functionalities on AMD platform."""

    homepage = "https://github.com/amd/libflame"
    url      = "https://github.com/amd/libflame/archive/2.0.tar.gz"
    git      = "https://github.com/amd/libflame.git"

    version('master', branch='master')
    version('2.0',   sha256='c80517b455df6763341f67654a6bda909f256a4927ffe9b4f0a2daed487d3739')
    version('1.3',   sha256='6821142bb877e5f92589f7d23e445519bb74922aef95486b27b90954032d80ef')
    version('1.0',   sha256='11e7b21b59849416ac372ef2c2b38beb73e62bead85d0ae3ffd0f4f1f6f760cf')

    depends_on('blis')
    phases = ['configure', 'build', 'install']

    def configure(self, spec, prefix):
        config_args = [
            '--enable-lapack2flame',
	    '--enable-cblas-interfaces',
	    '--enable-dynamic-build',
	    '--enable-max-arg-list-hack'
        ]

        configure("--prefix=" + prefix,
                  *config_args)

    def build(self, spec, prefix):
        make('clean')
        make()
        make('install')
