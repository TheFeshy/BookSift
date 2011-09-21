/* File: OptimizeCompare.i */
%module OptimizeCompare
%include <std_map.i>

%{
#define SWIG_FILE_WITH_INIT
#include "OptimizeCompare.h"
%}

%template(FingerprintCDict) ::std::map<long long, long int>;


