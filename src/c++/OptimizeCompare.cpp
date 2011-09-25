/* File: OptimizeCompare.c */

#include "OptimizeCompare.h"
#include <stdlib.h>
#include <iostream>
#include <fstream>

bool moduleworking()
{	std::cout << "Test" << std::endl;
	return true;
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

//This does the same thing as python's tupple hash - on 64 bit platforms only!
long long mash_shingles(const HashSequence::iterator s, const int shingle_size)
{	long long value = 0x345678;
	long long mul = 1000003;
	long long len = shingle_size;	
	HashSequence::iterator e = s + shingle_size;
	for(HashSequence::iterator i = s; i != e; i++)
	{	value = mul * (value ^ *i);
		--len;
		mul += (82520 + (len << 1));
	}
	value += 97531;
	if(value == -1)
	{	value = -2;
	}
	return value;
}

//It is assumed that hash_family size is at least as large as L_table size, but no checks are done!
HashSequence shingle_and_hash(HashSequence& word_hashes, 
						HashSequence& hash_family, 
						const int L_table_size, 
						const int shingle_size)
{	HashSequence minhashes(L_table_size, 9223372036854775807);
	if(word_hashes.size() < 2)
	{	std::cout << "This should be impossible." << std::endl;//TODO: raise an error or something.
	}
	HashSequence::iterator stop = word_hashes.end() - shingle_size;
	for(HashSequence::iterator i = word_hashes.begin(); i != stop; i++)
	{	long long hshingle = mash_shingles(i, shingle_size);
		//std::cout << count++ << " of " << word_hashes.size() << std::endl;
		for(unsigned int h = 0; h < hash_family.size(); h++)
		{	long long myhash = hshingle ^ hash_family[h];
			if(minhashes[h] > myhash)
			{	minhashes[h] = myhash;
			}
		}
	}
	return minhashes;
}
