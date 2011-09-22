/* File: OptimizeCompare.i */
%module OptimizeCompare
%include <std_map.i>
%include <std_vector.i>

%{
#define SWIG_FILE_WITH_INIT
#include "OptimizeCompare.h"
%}

%template(HashLookupTable) ::std::map<long long, long int>;
%template(HashSequence) ::std::vector<long long>;


float compare(std::vector<long long>, std::map<long long, long int>, const int, const int, const int);
bool moduleworking();



