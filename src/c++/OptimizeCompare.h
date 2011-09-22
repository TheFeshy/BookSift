/* File: OptimizeCompare.h */

#include <map>
#include <vector>

typedef std::map<long long, long int> HashLookupTable;
typedef std::vector<long long> HashSequence;

bool moduleworking();

float compare(HashSequence&, HashLookupTable&, const int, const int, const int);

