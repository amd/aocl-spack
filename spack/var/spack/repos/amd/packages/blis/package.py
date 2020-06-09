#
# Copyright (c) 2019 Advanced Micro Devices, Inc. 
# All rights reserved.
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
    AMD EPYC processor family by AMD and others"""

    homepage = "https://github.com/amd/blis"
    url      = "https://github.com/amd/blis/archive/2.1.tar.gz"
    git      = "https://github.com/amd/blis.git"

    version('2.1', tag='2.1')
    version('2.0', tag='2.0')
    version('1.3', tag='1.3')
    version('1.2', tag='1.2')
    version('1.0', tag='1.0')

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
    def check(self):
        make('check')

    def install(self, spec, prefix):
        make('install')
