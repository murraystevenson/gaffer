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

#include "boost/python.hpp"

#include "ExpansionBinding.h"

#include "GafferScene/Expansion.h"

#include "IECorePython/RefCountedBinding.h"
#include "IECorePython/ScopedGILRelease.h"

using namespace boost::python;
using namespace IECore;
using namespace GafferScene;

namespace
{

void expandWrapper( Expansion &e, const IECore::PathMatcher &paths, bool expandAncestors )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.expand( paths, expandAncestors );
}

void setExpandedPathsWrapper( Expansion &e, const IECore::PathMatcher &paths )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.setExpandedPaths( paths );
}

void clearExpansionWrapper( Expansion &e )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.clearExpansion();
}

void setPinnedPathsWrapper( Expansion &e, const IECore::PathMatcher &paths )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.setPinnedPaths( paths );
}

void pinWrapper( Expansion &e, const IECore::PathMatcher &paths )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.pin( paths );
}

void unpinWrapper( Expansion &e, const IECore::PathMatcher &paths )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.unpin( paths );
}

void clearPinningWrapper( Expansion &e )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.clearPinning();
}

void setLockedPathsWrapper( Expansion &e, const IECore::PathMatcher &paths )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.setLockedPaths( paths );
}

void lockWrapper( Expansion &e, const IECore::PathMatcher &paths )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.lock( paths );
}

void unlockWrapper( Expansion &e, const IECore::PathMatcher &paths )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.unlock( paths );
}

bool shouldExpandWrapper( Expansion &e, const std::string &path )
{
	return e.shouldExpand( path );
}

bool hasExpandedDescendantsWrapper( Expansion &e, const std::string &path )
{
	return e.hasExpandedDescendants( path );
}

void clearLockingWrapper( Expansion &e )
{
	IECorePython::ScopedGILRelease gilRelease;
	e.clearLocking();
}

} // namespace

void GafferSceneModule::bindExpansion()
{

	IECorePython::RefCountedClass<Expansion, IECore::RefCounted>( "Expansion" )
		.def( init<>() )
		.def( "expand", &expandWrapper, ( arg( "expandAncestors" ) = true ) )
		.def( "setExpandedPaths", &setExpandedPathsWrapper )
		.def( "getExpandedPaths", &Expansion::getExpandedPaths )
		.def( "clearExpansion", &clearExpansionWrapper )
		.def( "pin", &pinWrapper )
		.def( "unpin", &unpinWrapper )
		.def( "setPinnedPaths", &setPinnedPathsWrapper )
		.def( "getPinnedPaths", &Expansion::getPinnedPaths, return_value_policy<copy_const_reference>() )
		.def( "clearPinning", &clearPinningWrapper )
		.def( "lock", &lockWrapper )
		.def( "unlock", &unlockWrapper )
		.def( "setLockedPaths", &setLockedPathsWrapper )
		.def( "getLockedPaths", &Expansion::getLockedPaths, return_value_policy<copy_const_reference>() )
		.def( "clearLocking", &clearLockingWrapper )
		.def( "shouldExpand", &shouldExpandWrapper )
		.def( "hasExpandedDescendants", &hasExpandedDescendantsWrapper )
	;

}
