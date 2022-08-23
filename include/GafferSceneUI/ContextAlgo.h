//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2017, Image Engine Design Inc. All rights reserved.
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

#ifndef GAFFERSCENEUI_CONTEXTALGO_H
#define GAFFERSCENEUI_CONTEXTALGO_H

#include "GafferSceneUI/Export.h"

#include "IECore/PathMatcher.h"

#include "OpenEXR/ImathLimits.h"

namespace Gaffer
{

class Context;

} // namespace Gaffer

namespace GafferScene
{

class ScenePlug;

} // namespace GafferScene

namespace GafferSceneUI
{

namespace ContextAlgo
{

/// Path Expansion
/// ==============

/// The UI components coordinate with each other to perform on-demand scene
/// generation by using the Context to store paths to the currently expanded
/// locations within the scene. For instance, this allows the Viewer show the
/// objects from locations exposed by expansion performed in the HierarchyView,
/// and vice versa.
///
/// By convention, an expanded location is one whose children are visible,
/// meaning that they are listed below it in the HierarchyView and their objects
/// are drawn in the Viewer. Conversely, a collapsed location's children are
/// not listed in the HierarchyView and the location itself is drawn as a
/// the bounding box of the children.
///
/// As a consequence of this definition, it is not necessary to expand locations
/// without children. For a simple node such as Sphere, it is only necessary
/// to expand the root location ("/") to view the geometry. For nodes which
/// construct a deeper hierarchy, if the name of a location is visible in
/// the HierarchyView, then it's geometry will be displayed in the Viewer.

GAFFERSCENEUI_API void setExpandedPaths( Gaffer::Context *context, const IECore::PathMatcher &paths );
GAFFERSCENEUI_API IECore::PathMatcher getExpandedPaths( const Gaffer::Context *context );

/// Returns true if the named context variable affects the result of `getExpandedPaths()`.
/// This can be used from `Context::changedSignal()` to determine if the expansion has been
/// changed.
GAFFERSCENEUI_API bool affectsExpandedPaths( const IECore::InternedString &name );

/// Appends paths to the current expansion, optionally adding all ancestor paths too.
GAFFERSCENEUI_API void expand( Gaffer::Context *context, const IECore::PathMatcher &paths, bool expandAncestors = true );

/// Appends descendant paths to the current expansion up to a specified maximum depth.
/// Returns a new PathMatcher containing the new leafs of this expansion.
GAFFERSCENEUI_API IECore::PathMatcher expandDescendants( Gaffer::Context *context, const IECore::PathMatcher &paths, const GafferScene::ScenePlug *scene, int depth = Imath::limits<int>::max() );

/// Clears the currently expanded paths
GAFFERSCENEUI_API void clearExpansion( Gaffer::Context *context );

/// Path Pinning
/// ============

/// Pinned paths are locations considered to be always drawn in the Viewer, whether expanded or not
GAFFERSCENEUI_API void setPinnedPaths( Gaffer::Context *context, const IECore::PathMatcher &paths );
GAFFERSCENEUI_API IECore::PathMatcher getPinnedPaths( const Gaffer::Context *context );

/// Returns true if the named context variable affects the result of `getPinnedPaths()`.
/// This can be used from `Context::changedSignal()` to determine if the pinning has been
/// changed.
GAFFERSCENEUI_API bool affectsPinnedPaths( const IECore::InternedString &name );

/// Appends paths to the current pinning, optionally adding all ancestor paths too.
GAFFERSCENEUI_API void pin( Gaffer::Context *context, const IECore::PathMatcher &paths, bool pinAncestors = true );
/// Removes paths to the current pinning, optionally adding all ancestor paths too.
GAFFERSCENEUI_API void unpin( Gaffer::Context *context, const IECore::PathMatcher &paths, bool pinAncestors = true );

/// Clears the currently pinned paths
GAFFERSCENEUI_API void clearPinning( Gaffer::Context *context );

/// Path Selection
/// ==============

/// Similarly to Path Expansion, the UI components coordinate with each other
/// to perform scene selection, again using the Context to store paths to the
/// currently selected locations within the scene.
GAFFERSCENEUI_API void setSelectedPaths( Gaffer::Context *context, const IECore::PathMatcher &paths );
GAFFERSCENEUI_API IECore::PathMatcher getSelectedPaths( const Gaffer::Context *context );

/// Returns true if the named context variable affects the result of `getSelectedPaths()`.
/// This can be used from `Context::changedSignal()` to determine if the selection has been
/// changed.
GAFFERSCENEUI_API bool affectsSelectedPaths( const IECore::InternedString &name );

/// When multiple paths are selected, it can be useful to know which was the last path to be
/// added. Because `PathMatcher` is unordered, this must be specified separately.
///
/// > Note : The last selected path is synchronised automatically with the list of selected
/// > paths. When `setLastSelectedPath()` is called, it adds the path to the main selection list.
/// > When `setSelectedPaths()` is called, an arbitrary path becomes the last selected path.
/// >
/// > Note : An empty path is considered to mean that there is no last selected path, _not_
/// > that the scene root is selected.
GAFFERSCENEUI_API void setLastSelectedPath( Gaffer::Context *context, const std::vector<IECore::InternedString> &path );
GAFFERSCENEUI_API std::vector<IECore::InternedString> getLastSelectedPath( const Gaffer::Context *context );
GAFFERSCENEUI_API bool affectsLastSelectedPath( const IECore::InternedString &name );

} // namespace ContextAlgo

} // namespace GafferSceneUI

#endif // GAFFERSCENEUI_CONTEXTALGO_H
