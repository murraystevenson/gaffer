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

#ifndef GAFFERSCENE_EXPANSION_H
#define GAFFERSCENE_EXPANSION_H

#include "GafferScene/Export.h"

#include "IECore/PathMatcher.h"

using namespace IECore;

namespace GafferScene
{

class GAFFERSCENE_API Expansion : public IECore::RefCounted
{

	public : 
		
		IE_CORE_DECLAREMEMBERPTR( Expansion );

		// Expanded paths are typically those that users are interested in viewing in both the Viewer and HierarchyView.
		// At times, users may not want to have the same paths expanded in the Viewer and HierarchyView, so we introduce 
		// "pinned" and "locked" paths to allow users to manage this.
		void expand( const IECore::PathMatcher &paths, bool expandAncestors );
		void setExpandedPaths( const IECore::PathMatcher &paths );
		// getExpandedPaths() currently returns a PathMatcher containing the expanded paths as modified by any pinned or 
		// locked locations. This may be better to return m_expandedPaths unmmodified?
		IECore::PathMatcher getExpandedPaths();
		void clearExpansion();

		// Pinned paths and their descendants are expanded independently of the HierarchyView. 
		// Pins are independent of expanded paths to allow for decoupling of the HierarchyView expansion from the Viewer, 
		// allowing users to view specific branches of the scene hierarchy in the Viewer without also having to expand 
		// them in the HierarchyView.
		void pin( const IECore::PathMatcher &paths );
		void unpin( const IECore::PathMatcher &paths );
		void setPinnedPaths( const IECore::PathMatcher &paths );
		const IECore::PathMatcher &getPinnedPaths() const;
		void clearPinning();

		// Locked paths and their descendants are never expanded in the Viewer. Locks override both regular expansion 
		// and pins, allowing users to expand branches of the scene hierarchy in the HierarchyView without also having them 
		// expanded in the Viewer.
		void lock( const IECore::PathMatcher &paths );
		void unlock( const IECore::PathMatcher &paths );
		void setLockedPaths( const IECore::PathMatcher &paths );
		const IECore::PathMatcher &getLockedPaths() const;
		void clearLocking();

		// Given the current expansion state, returns whether the specified location should be expanded.
		bool shouldExpand( const std::string &path );
		bool shouldExpand( const std::vector<IECore::InternedString> &path );

		// Given the current expansion state, returns whether the specified location has descendants that should be expanded.
		bool hasExpandedDescendants( const std::string &path );
		bool hasExpandedDescendants( const std::vector<IECore::InternedString> &path );

	private :

		IECore::PathMatcher m_expandedPaths;
		IECore::PathMatcher m_pinnedPaths;
		IECore::PathMatcher m_lockedPaths;

};

} // namespace GafferScene

#endif // GAFFERSCENE_EXPANSION_H
