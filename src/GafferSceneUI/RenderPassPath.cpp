//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2024, Cinesite VFX Ltd. All rights reserved.
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

#include "GafferSceneUI/Private/RenderPassPath.h"

#include "GafferSceneUI/ContextAlgo.h"

#include "GafferScene/ScenePlug.h"

#include "Gaffer/Context.h"
#include "Gaffer/Node.h"
#include "Gaffer/Path.h"
#include "Gaffer/PathFilter.h"
#include "Gaffer/ScriptNode.h"
#include "Gaffer/Private/IECorePreview/LRUCache.h"

#include "boost/algorithm/string/predicate.hpp"
#include "boost/bind/bind.hpp"

using namespace std;
using namespace boost::placeholders;
using namespace IECore;
using namespace Gaffer;
using namespace GafferScene;
using namespace GafferSceneUI;

namespace
{

//////////////////////////////////////////////////////////////////////////
// LRU cache of PathMatchers built from render passes
//////////////////////////////////////////////////////////////////////////

struct PathMatcherCacheGetterKey
{

	PathMatcherCacheGetterKey()
		:	renderPassNames( nullptr ), grouped( false )
	{
	}

	PathMatcherCacheGetterKey( ConstStringVectorDataPtr renderPassNames, bool grouped )
		:	renderPassNames( renderPassNames ), grouped( grouped )
	{
		renderPassNames->hash( hash );
		hash.append( grouped );
	}

	operator const IECore::MurmurHash & () const
	{
		return hash;
	}

	MurmurHash hash;
	const ConstStringVectorDataPtr renderPassNames;
	const bool grouped;

};

PathMatcher pathMatcherCacheGetter( const PathMatcherCacheGetterKey &key, size_t &cost, const IECore::Canceller *canceller )
{
	cost = 1;

	PathMatcher result;

	if( key.grouped && RenderPassPath::pathGroupingFunction() )
	{
		for( const auto &renderPass : key.renderPassNames->readable() )
		{
			std::vector<InternedString> path = RenderPassPath::pathGroupingFunction()( renderPass );
			path.push_back( renderPass );
			result.addPath( path );
		}
	}
	else
	{
		for( const auto &renderPass : key.renderPassNames->readable() )
		{
			result.addPath( renderPass );
		}
	}

	return result;
}

using PathMatcherCache = IECorePreview::LRUCache<IECore::MurmurHash, IECore::PathMatcher, IECorePreview::LRUCachePolicy::Parallel, PathMatcherCacheGetterKey>;
PathMatcherCache g_pathMatcherCache( pathMatcherCacheGetter, 25 );

const InternedString g_renderPassContextName( "renderPass" );
const InternedString g_renderPassNamePropertyName( "renderPassPath:name" );
const InternedString g_renderPassEnabledPropertyName( "renderPassPath:enabled" );
const InternedString g_renderPassNamesOption( "option:renderPass:names" );
const InternedString g_renderPassEnabledOption( "option:renderPass:enabled" );

} // namespace

//////////////////////////////////////////////////////////////////////////
// RenderPassPath
//////////////////////////////////////////////////////////////////////////

IE_CORE_DEFINERUNTIMETYPED( RenderPassPath );

RenderPassPath::RenderPassPath( ScenePlugPtr scene, Gaffer::ContextPtr context, Gaffer::PathFilterPtr filter, const bool grouped )
	:	Path( filter ), m_grouped( grouped )
{
	setScene( scene );
	setContext( context );
}

RenderPassPath::RenderPassPath( ScenePlugPtr scene, Gaffer::ContextPtr context, const Names &names, const IECore::InternedString &root, Gaffer::PathFilterPtr filter, const bool grouped )
	:	Path( names, root, filter ), m_grouped( grouped )
{
	setScene( scene );
	setContext( context );
}

RenderPassPath::~RenderPassPath()
{
}

void RenderPassPath::setScene( ScenePlugPtr scene )
{
	if( m_scene == scene )
	{
		return;
	}

	m_scene = scene;
	m_plugDirtiedConnection = scene->node()->plugDirtiedSignal().connect( boost::bind( &RenderPassPath::plugDirtied, this, ::_1 ) );

	emitPathChanged();
}

ScenePlug *RenderPassPath::getScene()
{
	return m_scene.get();
}

const ScenePlug *RenderPassPath::getScene() const
{
	return m_scene.get();
}

void RenderPassPath::setContext( Gaffer::ContextPtr context )
{
	if( m_context == context )
	{
		return;
	}

	m_context = context;
	m_contextChangedConnection = context->changedSignal().connect( boost::bind( &RenderPassPath::contextChanged, this, ::_2 ) );

	emitPathChanged();
}

Gaffer::Context *RenderPassPath::getContext()
{
	return m_context.get();
}

const Gaffer::Context *RenderPassPath::getContext() const
{
	return m_context.get();
}

bool RenderPassPath::isValid( const IECore::Canceller *canceller ) const
{
	if( !Path::isValid() )
	{
		return false;
	}

	const PathMatcher p = pathMatcher( canceller );
	return p.match( names() ) & ( PathMatcher::ExactMatch | PathMatcher::DescendantMatch );
}

bool RenderPassPath::isLeaf( const IECore::Canceller *canceller ) const
{
	const PathMatcher p = pathMatcher( canceller );
	const unsigned match = p.match( names() );
	return match & PathMatcher::ExactMatch && !( match & PathMatcher::DescendantMatch );
}

PathPtr RenderPassPath::copy() const
{
	return new RenderPassPath( m_scene, m_context, names(), root(), const_cast<PathFilter *>( getFilter() ), m_grouped );
}

void RenderPassPath::propertyNames( std::vector<IECore::InternedString> &names, const IECore::Canceller *canceller ) const
{
	Path::propertyNames( names, canceller );
	names.push_back( g_renderPassNamePropertyName );
	names.push_back( g_renderPassEnabledPropertyName );
}

IECore::ConstRunTimeTypedPtr RenderPassPath::property( const IECore::InternedString &name, const IECore::Canceller *canceller ) const
{
	if( name == g_renderPassNamePropertyName )
	{
		const PathMatcher p = pathMatcher( canceller );
		if( p.match( names() ) & PathMatcher::ExactMatch )
		{
			return new StringData( names().back().string() );
		}
	}
	else if( name == g_renderPassEnabledPropertyName )
	{
		const PathMatcher p = pathMatcher( canceller );
		if( p.match( names() ) & PathMatcher::ExactMatch )
		{
			Context::EditableScope scopedContext( getContext() );
			if( canceller )
			{
				scopedContext.setCanceller( canceller );
			}
			scopedContext.set( g_renderPassContextName, &( names().back().string() ) );
			ConstBoolDataPtr enabledData = getScene()->globals()->member<BoolData>( g_renderPassEnabledOption );
			return new BoolData( enabledData ? enabledData->readable() : true );
		}
	}

	return Path::property( name, canceller );
}

const Gaffer::Plug *RenderPassPath::cancellationSubject() const
{
	return m_scene.get();
}

void RenderPassPath::doChildren( std::vector<PathPtr> &children, const IECore::Canceller *canceller ) const
{
	const PathMatcher p = pathMatcher( canceller );

	auto it = p.find( names() );
	if( it == p.end() )
	{
		return;
	}

	++it;
	while( it != p.end() && it->size() == names().size() + 1 )
	{
		children.push_back( new RenderPassPath( m_scene, m_context, *it, root(), const_cast<PathFilter *>( getFilter() ), m_grouped ) );
		it.prune();
		++it;
	}

	std::sort(
		children.begin(), children.end(),
		[]( const PathPtr &a, const PathPtr &b ) {
			return a->names().back().string() < b->names().back().string();
		}
	);
}

// We construct our path from a pathMatcher as we anticipate users requiring render passes to be organised
// hierarchically, with the last part of the path representing the render pass name. While it's technically
// possible to create a render pass name containing one or more '/' characters, we don't expect this to be
// practical as render pass names are used in output file paths where the included '/' characters would be
// interpreted as subdirectories. Validation in the UI will prevent users from inserting invalid characters
// such as '/' into render pass names.
const IECore::PathMatcher RenderPassPath::pathMatcher( const IECore::Canceller *canceller ) const
{
	Context::EditableScope scopedContext( m_context.get() );
	if( canceller )
	{
		scopedContext.setCanceller( canceller );
	}

	if( ConstStringVectorDataPtr renderPassData = m_scene.get()->globals()->member<StringVectorData>( g_renderPassNamesOption ) )
	{
		const PathMatcherCacheGetterKey key( renderPassData, m_grouped );
		return g_pathMatcherCache.get( key );
	}

	return IECore::PathMatcher();
}

void RenderPassPath::contextChanged( const IECore::InternedString &key )
{
	if( !boost::starts_with( key.c_str(), "ui:" ) )
	{
		emitPathChanged();
	}
}

void RenderPassPath::plugDirtied( Gaffer::Plug *plug )
{
	if( plug == m_scene->globalsPlug() )
	{
		emitPathChanged();
	}
}

RenderPassPath::PathGroupingFunction &RenderPassPath::pathGroupingFunction()
{
	// We deliberately make no attempt to free this, because typically a python
	// function is registered here, and we can't free that at exit because python
	// is already shut down by then.
	static RenderPassPath::PathGroupingFunction *g_pathGroupingFunction = new RenderPassPath::PathGroupingFunction;
	return *g_pathGroupingFunction;
}

void RenderPassPath::registerPathGroupingFunction( RenderPassPath::PathGroupingFunction f )
{
	pathGroupingFunction() = f;
}
