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

#include "GafferScene/Expansion.h"

#include "IECore/PathMatcher.h"

using namespace IECore;

using namespace GafferScene;

void Expansion::expand( const IECore::PathMatcher &paths, bool expandAncestors )
{
	if( expandAncestors )
	{
		for( IECore::PathMatcher::RawIterator it = paths.begin(), eIt = paths.end(); it != eIt; ++it )
		{
			m_expandedPaths.addPath( *it );
		}
	}
	else
	{
		for( IECore::PathMatcher::Iterator it = paths.begin(), eIt = paths.end(); it != eIt; ++it )
		{
			m_expandedPaths.addPath( *it );
		}
	}
}

void Expansion::setExpandedPaths( const IECore::PathMatcher &paths )
{
	m_expandedPaths = paths;
}

IECore::PathMatcher Expansion::getExpandedPaths()
{
	IECore::PathMatcher pinnedPaths = IECore::PathMatcher( m_pinnedPaths );

	// Locked paths are never expanded, we allow these to override pinned paths 
	for( IECore::PathMatcher::Iterator it = m_lockedPaths.begin(), eIt = m_lockedPaths.end(); it != eIt; ++it )
	{
		pinnedPaths.prune( *it );
	}
	
	IECore::PathMatcher expanded = IECore::PathMatcher();
	for( IECore::PathMatcher::Iterator it = pinnedPaths.begin(), eIt = pinnedPaths.end(); it != eIt; ++it )
	{
		expanded.addPath( *it );
	}

	for( IECore::PathMatcher::Iterator it = m_expandedPaths.begin(), eIt = m_expandedPaths.end(); it != eIt; ++it )
	{
		// Limit expansion of new locations to those that aren't currently locked or a descendant of a locked location
		if( !(m_lockedPaths.match( *it ) & (IECore::PathMatcher::Result::AncestorMatch | IECore::PathMatcher::Result::ExactMatch) ) )
		{
			expanded.addPath( *it );
		}
	}

	return expanded;
}

void Expansion::clearExpansion()
{
	m_expandedPaths = IECore::PathMatcher();
}

void Expansion::pin( const IECore::PathMatcher &paths )
{	
	for( IECore::PathMatcher::Iterator it = paths.begin(), eIt = paths.end(); it != eIt; ++it )
	{
		m_pinnedPaths.addPath( *it );
	}
}

void Expansion::unpin( const IECore::PathMatcher &paths )
{	
	if( m_pinnedPaths.isEmpty() )
	{
		return;
	}

	for( IECore::PathMatcher::Iterator it = paths.begin(), eIt = paths.end(); it != eIt; ++it )
	{
		m_pinnedPaths.removePath( *it );
	}
}

void Expansion::setPinnedPaths( const IECore::PathMatcher &paths )
{
	m_pinnedPaths = paths;
}

const IECore::PathMatcher &Expansion::getPinnedPaths() const
{
	return m_pinnedPaths;
}

void Expansion::clearPinning()
{
	if( m_pinnedPaths.isEmpty() )
	{
		return;
	}

	m_pinnedPaths = IECore::PathMatcher();
}

void Expansion::lock( const IECore::PathMatcher &paths )
{	
	for( IECore::PathMatcher::Iterator it = paths.begin(), eIt = paths.end(); it != eIt; ++it )
	{
		m_lockedPaths.addPath( *it );
	}
}

void Expansion::unlock( const IECore::PathMatcher &paths )
{	
	if( m_lockedPaths.isEmpty() )
	{
		return;
	}
	
	for( IECore::PathMatcher::Iterator it = paths.begin(), eIt = paths.end(); it != eIt; ++it )
	{
		m_lockedPaths.removePath( *it );
	}
}

void Expansion::setLockedPaths( const IECore::PathMatcher &paths )
{
	m_lockedPaths = paths;
}

const IECore::PathMatcher &Expansion::getLockedPaths() const
{
	return m_lockedPaths;
}

void Expansion::clearLocking()
{
	if( m_lockedPaths.isEmpty() )
	{
		return;
	}

	m_lockedPaths = IECore::PathMatcher();
}

bool Expansion::shouldExpand( const std::string &path )
{
	return ( m_expandedPaths.match( path ) & PathMatcher::ExactMatch || m_pinnedPaths.match( path ) & ( PathMatcher::ExactMatch | PathMatcher::AncestorMatch ) ) 
			&& !( m_lockedPaths.match( path ) & ( PathMatcher::ExactMatch | PathMatcher::AncestorMatch ) );
}

bool Expansion::shouldExpand( const std::vector<IECore::InternedString> &path )
{
	return ( m_expandedPaths.match( path ) & PathMatcher::ExactMatch || m_pinnedPaths.match( path ) & ( PathMatcher::ExactMatch | PathMatcher::AncestorMatch ) ) 
			&& !( m_lockedPaths.match( path ) & ( PathMatcher::ExactMatch | PathMatcher::AncestorMatch ) );
}

bool Expansion::hasExpandedDescendants( const std::string &path )
{
	return ( m_expandedPaths.match( path ) & PathMatcher::DescendantMatch || m_pinnedPaths.match( path ) & ( PathMatcher::ExactMatch | PathMatcher::DescendantMatch ) ) 
			&& !( m_lockedPaths.match( path ) & ( PathMatcher::ExactMatch | PathMatcher::AncestorMatch ) );
}

bool Expansion::hasExpandedDescendants( const std::vector<IECore::InternedString> &path )
{
	return ( m_expandedPaths.match( path ) & PathMatcher::DescendantMatch || m_pinnedPaths.match( path ) & ( PathMatcher::ExactMatch | PathMatcher::DescendantMatch ) ) 
			&& !( m_lockedPaths.match( path ) & ( PathMatcher::ExactMatch | PathMatcher::AncestorMatch ) );
}
