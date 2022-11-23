//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2022, Cinesite VFX Ltd. All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//      * Redistributions of source code must retain the above
//        copyright notice, this list of conditions and the following
//        disclaimer.
//
//      * Redistributions in binary form must reproduce the above
//        copyright notice, this list of conditions and the following
//        disclaimer in the documentation and/or other materials provided with
//        the distribution.
//
//      * Neither the name of John Haddon nor the names of
//        any other contributors to this software may be used to endorse or
//        promote products derived from this software without specific prior
//        written permission.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#ifndef GAFFERSCENE_VISIBLESET_INL
#define GAFFERSCENE_VISIBLESET_INL

#include "IECore/PathMatcher.h"

namespace GafferScene
{

inline PathMatcher::Result VisibleSet::match( const std::vector<InternedString> &path, const size_t minimumExpansionDepth ) const
{

	if( exclusions.match( path ) & ( PathMatcher::ExactMatch | PathMatcher::AncestorMatch ) )
	{
		// Exclusions override all other potential matches for the excluded path and all of its descendants
		return PathMatcher::Result::NoMatch;
	}

	unsigned result = PathMatcher::NoMatch;
	if( minimumExpansionDepth >= path.size() )
	{
		// Paths within minimumExpansionDepth are considered visible and having visible children
		/// \todo Return AncestorMatch for locations with ancestors within the minimumExpansionDepth. We should
		/// also be able to return early and avoid testing inclusions and expansions for these paths.
		result |= ( PathMatcher::ExactMatch | PathMatcher::DescendantMatch );
	}
	else if( minimumExpansionDepth + 1 == path.size() )
	{
		result |= PathMatcher::ExactMatch;
	}

	const unsigned inclusionsMatch = inclusions.match( path );
	result |= inclusionsMatch;
	if( inclusionsMatch & ( PathMatcher::ExactMatch | PathMatcher::AncestorMatch ) )
	{
		// An ancestor in inclusions will cause this path and its descendants to be visible
		result |= ( PathMatcher::ExactMatch | PathMatcher::DescendantMatch );
	}

	const unsigned expansionsMatch = expansions.match( path );
	if( path.size() > 1 )
	{
		std::vector<InternedString> parentPath = path; parentPath.pop_back();
		// Expansions also require an expanded parent to be visible
		/// \todo This would be improved by testing all ancestors rather than only the immediate parent.
		/// We'll need to consider how to handle `/` as the root location is implicitly expanded and would
		/// need to be present in expansions for a successful AllAncestorsMatch.
		if( expansions.match( parentPath ) & PathMatcher::ExactMatch )
		{
			result |= ( PathMatcher::ExactMatch | PathMatcher::AncestorMatch );
			if( expansionsMatch & PathMatcher::ExactMatch )
			{
				result |= PathMatcher::DescendantMatch;
			}
		}
	}
	else if( path.size() == 1 && expansionsMatch & PathMatcher::ExactMatch )
	{
		result |= PathMatcher::DescendantMatch;
	}

	return (PathMatcher::Result)result;

}

inline bool VisibleSet::operator == ( const VisibleSet& rhs ) const
{
	return expansions == rhs.expansions && inclusions == rhs.inclusions && exclusions == rhs.exclusions;
}

inline bool VisibleSet::operator != ( const VisibleSet& rhs ) const
{
	return expansions != rhs.expansions || inclusions != rhs.inclusions || exclusions != rhs.exclusions;
}

inline void murmurHashAppend( MurmurHash &h, const VisibleSet &data )
{
	h.append( data.expansions );
	h.append( data.inclusions );
	h.append( data.exclusions );
}

} // namespace GafferScene

#endif // GAFFERSCENE_VISIBLESET_INL
