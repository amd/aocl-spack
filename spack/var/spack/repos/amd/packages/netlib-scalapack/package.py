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
import sys


class NetlibScalapack(CMakePackage):
    """ScaLAPACK[2] is a library of high-performance linear algebra routines for
    parallel distributed memory machines. It depends on libraries including BLIS 
    and LIBFLAME for Linear Algebra computations."""

    homepage = "http://www.netlib.org/scalapack/"
    url = "http://www.netlib.org/scalapack/scalapack-2.0.2.tgz"

    version('2.0.2', '2f75e600a2ba155ed9ce974a1c4b536f')
    version('2.0.1', '17b8cde589ea0423afe1ec43e7499161')
    version('2.0.0', '9e76ae7b291be27faaad47cfc256cbfe')
    # versions before 2.0.0 are not using cmake and requires blacs as
    # a separated package

    variant(
        'shared',
        default=True,
        description='Build the shared library version'
    )
    variant(
        'pic',
        default=False,
        description='Build position independent code'
    )

    provides('scalapack')

    depends_on('mpi')
    depends_on('libflame')
    depends_on('blis')
    depends_on('cmake', when='@2.0.0:', type='build')

    # See: https://github.com/Reference-ScaLAPACK/scalapack/issues/9
    patch("cmake_fortran_mangle.patch", when='@2.0.2:')
    # See: https://github.com/Reference-ScaLAPACK/scalapack/pull/10
    patch("mpi2-compatibility.patch", when='@2.0.2:')

    @property
    def libs(self):
        # Note that the default will be to search
        # for 'libnetlib-scalapack.<suffix>'
        shared = True if '+shared' in self.spec else False
        return find_libraries(
            'libscalapack', root=self.prefix, shared=shared, recursive=True
        )

    def cmake_args(self):
        spec = self.spec

        options = [
            "-DBUILD_SHARED_LIBS:BOOL=%s" % ('ON' if '+shared' in spec else
                                             'OFF'),
            "-DBUILD_STATIC_LIBS:BOOL=%s" % ('OFF' if '+shared' in spec else
                                             'ON')
        ]

        # Make sure we use AMD's libflame:
        blis = spec['blis'].libs
        libflame = spec['libflame'].libs
        options.extend([
            '-DLAPACK_FOUND=true',
            '-DLAPACK_INCLUDE_DIRS=%s' % spec['libflame'].prefix.include,
            '-DLAPACK_LIBRARIES=%s' % (libflame.joined(';')),
            '-DBLAS_LIBRARIES=%s' % (blis.joined(';'))
        ])

        if '+pic' in spec:
            options.extend([
                "-DCMAKE_C_FLAGS=%s" % self.compiler.pic_flag,
                "-DCMAKE_Fortran_FLAGS=%s" % self.compiler.pic_flag
            ])

        return options

    @run_after('install')
    def fix_darwin_install(self):
        # The shared libraries are not installed correctly on Darwin:
        if (sys.platform == 'darwin') and ('+shared' in self.spec):
            fix_darwin_install_name(self.spec.prefix.lib)

