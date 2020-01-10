#
# Copyright (c) 2019 Advanced Micro Devices, Inc. 
# All rights reserved.
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
    for the AMD EPYC processor family, libFLAME enables running 
    high performing LAPACK functionalities on AMD platform."""

    homepage = "https://github.com/amd/libflame"
    url      = "https://github.com/amd/libflame/archive/2.0.tar.gz"
    git      = "https://github.com/amd/libflame.git"

    version('2.0', tag='2.0')
    version('1.3', tag='1.3')
    version('1.0', tag='1.0')

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
