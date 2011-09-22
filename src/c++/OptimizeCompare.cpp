/* File: OptimizeCompare.c */

#include "OptimizeCompare.h"
#include <stdlib.h>
#include <iostream>
#include <fstream>

bool moduleworking()
{	return true;
}

float compare(HashSequence &hs, HashLookupTable &hl, const int meaningful_length, const int allowed_consecutive_errors, const int allowed_distance_errors)
{	int totalscore = 0;
	int bestpossible = hs.size();
	int currentscore = 0;
	int nextexpected = -100;
	HashLookupTable::iterator h2 = hl.find(hs[0]); //Set initial value for nextexpected
	if (h2 != hl.end())
	{	nextexpected = h2->second;
	}
	int errors_remain = -1; //If we hit an error, it isn't a "rollback" error
	for(int i1=0; i1 < hs.size(); i1++)
	{	h2 = hl.find(hs[i1]);
		if ((h2 != hl.end()) && (abs(h2->second - nextexpected) <= allowed_distance_errors))
		{	currentscore++; //We have a hit
			nextexpected = h2->second +1;
			errors_remain = allowed_consecutive_errors;
		}
		else //Not a hit (not found, or found too far)
		{
			if (errors_remain > 0) //Still allowed to miss
			{	currentscore++; //Pretend it's a hit for now; well rollback if not.
				if(h2 != hl.end())
				{	nextexpected = h2->second +1;
				}
				else
				{	nextexpected++;
				}
				errors_remain--;
			}
			else //not allowed to miss
			{
				if (0 == errors_remain) //Time to rollback!
				{	currentscore -= allowed_consecutive_errors;
					i1 -= allowed_consecutive_errors;
					errors_remain = -1;
					h2 = hl.find(hs[i1]);
					if (currentscore > meaningful_length)
					{	totalscore += currentscore;
					}
				}
				if(h2 != hl.end()) //Found, but was too far
				{	nextexpected = h2->second+1;
					currentscore = 1;
					errors_remain = allowed_consecutive_errors;
				}
				else //Not found at all
				{	nextexpected = -100;
					currentscore = 0;
				}
			}
		}
	}
	if(currentscore > meaningful_length)
	{	totalscore += currentscore;
	}
	return float(totalscore)/float(bestpossible);
}

