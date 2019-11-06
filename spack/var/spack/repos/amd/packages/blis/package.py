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

class Blis(Package):
    """BLIS is a portable open-source software framework for
    instantiating high-performance Basic Linear Algebra
    Subprograms (BLAS) - like dense linear algebra libraries.
    The framework was designed to isolate essential kernels of
    computation that, when optimized, immediately enable optimized
    implementations of most of its commonly used and computationally
    intensive operations. Select kernels have been optimized for the
    AMD EPYCTM processor family by AMD and others"""

    homepage = "https://github.com/amd/blis"
    url      = "https://github.com/amd/blis/archive/2.0.tar.gz"
    git      = "https://github.com/amd/blis.git"

    version('2.0', sha256='7469680ce955f39d8d6bb7f70d2cc854222e5ef92a39488e77421300a65fad83')
    version('1.3',   sha256='6ce42054d63564f57a7276e7c63f3d01ed96a64908b484a99e68309acc968745')
    version('1.2',   sha256='b2e7d055c37faa5bfda5a1be63a35d1e612108a9809d7726cedbdd4722d76b1d')
    version('1.0',   sha256='b8b86b1cc0c61ab5318102985dc3ccb34028ea2a110a354ea4e02e932fbaeeb9')

    variant(
        'threads', default='none',
        description='Multithreading support',
        values=('pthreads', 'openmp', 'none'),
        multi=False
    )

    phases = ['configure', 'build', 'install']

    def configure(self, spec, prefix):
	config_args = []

	config_args.append("--enable-threading=" +
                           spec.variants['threads'].value)

	config_args.append("--enable-cblas")
	config_args.append("auto")
        configure("--prefix=" + prefix,
                  *config_args)

    def build(self, spec, prefix):
        make('clean')
        make()

    @run_after('build')
    @on_package_attributes(run_tests=True)
    def check(self):
        make('check')

    def install(self, spec, prefix):
        make('install')
