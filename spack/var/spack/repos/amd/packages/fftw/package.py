# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
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
    url      = "https://github.com/amd/amd-fftw/archive/2.0.tar.gz"
    git      = "https://github.com/amd/amd-fftw.git"


    version('2.0', tag='2.0')

    variant(
        'float', default=True,
        description='Produces a single precision version of the library')
    variant(
        'double', default=True,
        description='Produces a double precision version of the library')
    variant(
        'long_double', default=True,
        description='Produces a long double precision version of the library')
    variant(
        'quad', default=False,
        description='Produces a quad precision version of the library '
                    '(works only with GCC and libquadmath)')
    variant('openmp', default=False, description="Enable OpenMP support.")
    variant('mpi', default=True, description='Activate MPI support')
    variant(
        'pfft_patches', default=False,
        description='Add extra transpose functions for PFFT compatibility')

    variant(
        'simd',
        default='sse2,avx,avx2',
        values=(
            'sse', 'sse2', 'avx', 'avx2', 'avx512',  # Intel
            'avx-128-fma', 'kcvi',  # Intel
            'altivec', 'vsx',  # IBM
            'neon',  # ARM
            'generic-simd128', 'generic-simd256'  # Generic
        ),
        description='Optimizations that are enabled in this build',
        multi=True
    )
    variant('fma', default=False, description='Activate support for fma')

    depends_on('mpi', when='+mpi')
    depends_on('automake', type='build', when='+pfft_patches')
    depends_on('autoconf', type='build', when='+pfft_patches')
    depends_on('libtool', type='build', when='+pfft_patches')
    # https://github.com/FFTW/fftw3/commit/902d0982522cdf6f0acd60f01f59203824e8e6f3
    conflicts('%gcc@8:8.9999', when="@3.3.7")

    provides('fftw-api@2', when='@2.1.5')
    provides('fftw-api@3', when='@3:')

    @property
    def libs(self):

        # Reduce repetitions of entries
        query_parameters = list(llnl.util.lang.dedupe(
            self.spec.last_query.extra_parameters
        ))

        # List of all the suffixes associated with float precisions
        precisions = [
            ('float', 'f'),
            ('double', ''),
            ('long_double', 'l'),
            ('quad', 'q')
        ]

        # Retrieve the correct suffixes, or use double as a default
        suffixes = [v for k, v in precisions if k in query_parameters] or ['']

        # Construct the list of libraries that needs to be found
        libraries = []
        for sfx in suffixes:
            if 'mpi' in query_parameters and '+mpi' in self.spec:
                libraries.append('libfftw3' + sfx + '_mpi')

            if 'openmp' in query_parameters and '+openmp' in self.spec:
                libraries.append('libfftw3' + sfx + '_omp')

            libraries.append('libfftw3' + sfx)

        return find_libraries(libraries, root=self.prefix, recursive=True)

    def patch(self):
        # If fftw/config.h exists in the source tree, it will take precedence
        # over the copy in build dir.  As only the latter has proper config
        # for our build, this is a problem.  See e.g. issue #7372 on github
        if os.path.isfile('fftw/config.h'):
            os.rename('fftw/config.h', 'fftw/config.h.SPACK_RENAMED')

    def autoreconf(self, spec, prefix):
        if '+pfft_patches' in spec:
            autoreconf = which('autoreconf')
            autoreconf('-ifv')

    def configure(self, spec, prefix):
        # Base options
        options = [
            '--prefix={0}'.format(prefix),
            '--enable-shared',
            '--enable-amd-opt'
        ]
        if not self.compiler.f77 or not self.compiler.fc:
            options.append("--disable-fortran")
        if spec.satisfies('@:2'):
            options.append('--enable-type-prefix')

        # Variants that affect every precision
        if '+openmp' in spec:
            # Note: Apple's Clang does not support OpenMP.
            if spec.satisfies('%clang'):
                ver = str(self.compiler.version)
                if ver.endswith('-apple'):
                    raise InstallError("Apple's clang does not support OpenMP")
            options.append('--enable-openmp')
            if spec.satisfies('@:2'):
                # TODO: libtool strips CFLAGS, so 2.x libxfftw_threads
                #       isn't linked to the openmp library. Patch Makefile?
                options.insert(0, 'CFLAGS=' + self.compiler.openmp_flag)
        if '+mpi' in spec:
            options.append('--enable-mpi')

        # SIMD support
        float_options, double_options = [], []
        if spec.satisfies('@3:', strict=True):
            for opts in (float_options, double_options):
                opts += self.enable_or_disable('simd')
                opts += self.enable_or_disable('fma')

        configure = Executable('../configure')

        # Build double/float/long double/quad variants
        if '+double' in spec:
            with working_dir('double', create=True):
                configure(*(options + double_options))
        if '+float' in spec:
            with working_dir('float', create=True):
                configure('--enable-float', *(options + float_options))
        if spec.satisfies('@3:+long_double'):
            with working_dir('long-double', create=True):
                configure('--enable-long-double', *options)
        if spec.satisfies('@3:+quad'):
            with working_dir('quad', create=True):
                configure('--enable-quad-precision', *options)

    def build(self, spec, prefix):
        if '+double' in spec:
            with working_dir('double'):
                make()
        if '+float' in spec:
            with working_dir('float'):
                make()
        if spec.satisfies('@3:+long_double'):
            with working_dir('long-double'):
                make()
        if spec.satisfies('@3:+quad'):
            with working_dir('quad'):
                make()

    def check(self):
        spec = self.spec
        if '+double' in spec:
            with working_dir('double'):
                make("check")
        if '+float' in spec:
            with working_dir('float'):
                make("check")
        if spec.satisfies('@3:+long_double'):
            with working_dir('long-double'):
                make("check")
        if spec.satisfies('@3:+quad'):
            with working_dir('quad'):
                make("check")

    def install(self, spec, prefix):
        if '+double' in spec:
            with working_dir('double'):
                make("install")
        if '+float' in spec:
            with working_dir('float'):
                make("install")
        if spec.satisfies('@3:+long_double'):
            with working_dir('long-double'):
                make("install")
        if spec.satisfies('@3:+quad'):
            with working_dir('quad'):
                make("install")
