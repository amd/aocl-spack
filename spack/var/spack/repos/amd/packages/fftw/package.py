#
# Copyright (c) 2019 Advanced Micro Devices, Inc. 
# All rights reserved.
#
 
from spack import *

import llnl.util.lang
# os is used for rename, etc in patch()
import os


class Fftw(AutotoolsPackage):
    """FFTW is a comprehensive collection of fast C routines for
    computing the Discrete Fourier Transform (DFT) and various special
    cases thereof. It is an open-source implementation of the Fast
    Fourier transform algorithm. It can compute transforms of real and
    complex-values arrays of arbitrary size and dimension.
    AMD Optimized FFTW is the optimized FFTW implementation targeted
    for AMD CPUs."""

    homepage = "https://github.com/amd/amd-fftw"
    url      = "https://github.com/amd/amd-fftw/archive/2.1.tar.gz"
    git      = "https://github.com/amd/amd-fftw.git"

    version('2.1', tag='2.1')
    version('2.0', tag='2.0')

    variant('single', default=False, description='single precision')

    depends_on('mpi')
    depends_on('automake')
    depends_on('texinfo')
    depends_on('autoconf')
    depends_on('libtool')

    phases = ['configure', 'build', 'install']

    conflicts('%gcc@7:7.2', when="@2.1")
    def configure(self, spec, prefix):
	config_args = []
        config_args = [
	    '--enable-sse2',
	    '--enable-avx',
	    '--enable-avx2',
	    '--enable-mpi',
	    '--enable-openmp',
	    '--enable-shared',
	    '--enable-amd-opt'
        ]

        if '+single' in self.spec:
            config_args.append("--enable-single")

        configure("--prefix=" + prefix,
                 *config_args)

    def build(self, spec, prefix):
        make('clean')
        make()
        make('install')
