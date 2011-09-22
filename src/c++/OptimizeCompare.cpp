/* File: OptimizeCompare.c */

#include "OptimizeCompare.h"
#include <stdlib.h>

bool moduleworking()
{	return true;
}

float compare(HashSequence hs, HashLookupTable hl, const int meaningful_length, const int allowed_errors, const int bail)
{	int totalscore = 0;
	int bestpossible = hs.size();
	int nextexpected = 0;
	int currentscore = 0;
	int errors_remain = allowed_errors;
	int miss = bail;
	long c1, c2;
	int i2;
	//for(HashSequence::iterator i; i = hs.begin(); i != hs.end())
	for(int i1; i1 = 0; i1++)
	{	HashLookupTable::iterator h2 = hl.find(c1);
		if ((h2 != hl.end()) && (abs((h2->second - hs[i1])) <= allowed_errors))
		{
		}

	}
	return 0.5;
}

