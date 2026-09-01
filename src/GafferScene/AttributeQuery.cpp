//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2021, Cinesite VFX Ltd. All rights reserved.
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

#include "GafferScene/AttributeQuery.h"

#include "Gaffer/Metadata.h"
#include "Gaffer/NumericPlug.h"
#include "Gaffer/PlugAlgo.h"

#include "IECore/CompoundObject.h"
#include "IECore/Exception.h"
#include "IECore/SimpleTypedData.h"

#include "boost/algorithm/string/predicate.hpp"
#include "boost/container/small_vector.hpp"

#include <cassert>
#include <limits>
#include <string>

using namespace IECore;
using namespace Gaffer;
using namespace GafferScene;

namespace
{

const size_t g_existsPlugIndex = 0;
const size_t g_sourcePlugIndex = 1;
const size_t g_valuePlugIndex = 2;
const std::string g_attributePrefix( "attribute:" );
const InternedString g_defaultValue( "defaultValue" );
const IntDataPtr g_sourceNone = new IntData( (int)GafferScene::AttributeQuery::Source::None );
const IntDataPtr g_sourceLocal = new IntData( (int)GafferScene::AttributeQuery::Source::Local );
const IntDataPtr g_sourceInherited = new IntData( (int)GafferScene::AttributeQuery::Source::Inherited );
const IntDataPtr g_sourceGlobals = new IntData( (int)GafferScene::AttributeQuery::Source::Globals );
const IntDataPtr g_sourceFallback = new IntData( (int)GafferScene::AttributeQuery::Source::Fallback );

const Gaffer::ValuePlug *correspondingPlug( const Gaffer::ValuePlug *parent, const Gaffer::ValuePlug *child, const Gaffer::ValuePlug *other )
{
	boost::container::small_vector<const Gaffer::ValuePlug*, 4> path;

	const Gaffer::ValuePlug *plug = child;

	while( plug != parent )
	{
		path.push_back( plug );
		plug = plug->parent<Gaffer::ValuePlug>();
	}

	plug = other;

	while( !path.empty() )
	{
		plug = plug->getChild<Gaffer::ValuePlug>( path.back()->getName() );
		path.pop_back();
	}

	return plug;
}

void addLeafPlugs( const Gaffer::Plug *plug, Gaffer::DependencyNode::AffectedPlugsContainer &outputs )
{
	if( plug->children().empty() )
	{
		outputs.push_back( plug );
	}
	else
	{
		for( const Gaffer::PlugPtr &child : Gaffer::Plug::OutputRange( *plug ) )
		{
			addLeafPlugs( child.get(), outputs );
		}
	}
}

/// Returns the index into the child vector of `parentPlug` that is
/// either the `childPlug` itself or an ancestor of childPlug.
/// Throws an Exception if the `childPlug` is not a descendant of `parentPlug`.
size_t getChildIndex( const Gaffer::Plug *parentPlug, const Gaffer::ValuePlug *descendantPlug )
{
	const GraphComponent *p = descendantPlug;
	while( p )
	{
		if( p->parent() == parentPlug )
		{
			for( size_t i = 0, eI = parentPlug->children().size(); i < eI; ++i )
			{
				if( parentPlug->getChild( i ) == p )
				{
					return i;
				}
			}
		}
		p = p->parent();
	}

	throw IECore::Exception( "AttributeQuery : Plug not in hierarchy." );
}

} // namespace

GAFFER_NODE_DEFINE_TYPE( AttributeQuery );

size_t AttributeQuery::g_firstPlugIndex = 0;

AttributeQuery::AttributeQuery( const std::string &name )
: Gaffer::ComputeNode( name )
{
	storeIndexOfNextChild( g_firstPlugIndex );
	addChild( new ScenePlug( "scene" ) );
	addChild( new StringPlug( "location" ) );
	addChild( new BoolPlug( "inherit", Plug::In, false ) );
	addChild( new BoolPlug( "useMetadata", Plug::In, false ) );
	/// \todo See notes in `ShaderQuery::ShaderQuery`.
	addChild( new ArrayPlug( "queries", Plug::In, nullptr, 0, std::numeric_limits<size_t>::max(), Plug::Default, false ) );
	addChild( new ArrayPlug( "out", Plug::Out, nullptr, 0, std::numeric_limits<size_t>::max(), Plug::Default, false ) );
	addChild( new CompoundObjectPlug( "attributes", Plug::Out, new IECore::CompoundObject ) );
	addChild( new AtomicCompoundDataPlug( "__internalSources", Plug::Out, new IECore::CompoundData ) );
	addChild( new BoolPlug( "__internalLocationExists", Plug::Out, false ) );
}

AttributeQuery::~AttributeQuery()
{}

ScenePlug *AttributeQuery::scenePlug()
{
	return getChild<ScenePlug>( g_firstPlugIndex );
}

const ScenePlug *AttributeQuery::scenePlug() const
{
	return getChild<ScenePlug>( g_firstPlugIndex );
}

Gaffer::StringPlug *AttributeQuery::locationPlug()
{
	return getChild<StringPlug>( g_firstPlugIndex + 1 );
}

const Gaffer::StringPlug *AttributeQuery::locationPlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex + 1 );
}

Gaffer::BoolPlug *AttributeQuery::inheritPlug()
{
	return getChild<BoolPlug>( g_firstPlugIndex + 2 );
}

const Gaffer::BoolPlug *AttributeQuery::inheritPlug() const
{
	return getChild<BoolPlug>( g_firstPlugIndex + 2 );
}

Gaffer::BoolPlug *AttributeQuery::useMetadataPlug()
{
	return getChild<BoolPlug>( g_firstPlugIndex + 3 );
}

const Gaffer::BoolPlug *AttributeQuery::useMetadataPlug() const
{
	return getChild<BoolPlug>( g_firstPlugIndex + 3 );
}

Gaffer::ArrayPlug *AttributeQuery::queriesPlug()
{
	return getChild<ArrayPlug>( g_firstPlugIndex + 4 );
}

const Gaffer::ArrayPlug *AttributeQuery::queriesPlug() const
{
	return getChild<ArrayPlug>( g_firstPlugIndex + 4 );
}

Gaffer::ArrayPlug *AttributeQuery::outPlug()
{
	return getChild<ArrayPlug>( g_firstPlugIndex + 5 );
}

const Gaffer::ArrayPlug *AttributeQuery::outPlug() const
{
	return getChild<ArrayPlug>( g_firstPlugIndex + 5 );
}

Gaffer::CompoundObjectPlug *AttributeQuery::attributesPlug()
{
	return getChild<CompoundObjectPlug>( g_firstPlugIndex + 6 );
}

const Gaffer::CompoundObjectPlug *AttributeQuery::attributesPlug() const
{
	return getChild<CompoundObjectPlug>( g_firstPlugIndex + 6 );
}

Gaffer::AtomicCompoundDataPlug *AttributeQuery::internalSourcesPlug()
{
	return getChild<AtomicCompoundDataPlug>( g_firstPlugIndex + 7 );
}

const Gaffer::AtomicCompoundDataPlug *AttributeQuery::internalSourcesPlug() const
{
	return getChild<AtomicCompoundDataPlug>( g_firstPlugIndex + 7 );
}

Gaffer::BoolPlug *AttributeQuery::internalLocationExistsPlug()
{
	return getChild<BoolPlug>( g_firstPlugIndex + 8 );
}

const Gaffer::BoolPlug *AttributeQuery::internalLocationExistsPlug() const
{
	return getChild<BoolPlug>( g_firstPlugIndex + 8 );
}

Gaffer::NameValuePlug *AttributeQuery::addQuery( const Gaffer::ValuePlug *plug, const std::string &attribute )
{
	NameValuePlugPtr childQueryPlug = new NameValuePlug( "", plug->createCounterpart( "query0", Plug::In ), "query0", Plug::Default );
	childQueryPlug->namePlug()->setValue( attribute );

	ValuePlugPtr newOutPlug = new ValuePlug( "out0", Plug::Out );
	newOutPlug->addChild( new BoolPlug( "exists", Plug::Out, false ) );
	newOutPlug->addChild( new IntPlug( "source", Plug::Out, (int)Source::None, (int)Source::None, (int)Source::Fallback ) );
	newOutPlug->addChild( plug->createCounterpart( "value", Plug::Out ) );

	outPlug()->addChild( newOutPlug );
	queriesPlug()->addChild( childQueryPlug );

	return childQueryPlug.get();
}

void AttributeQuery::removeQuery( Gaffer::NameValuePlug *plug )
{
	const ValuePlug *oPlug = outPlugFromQuery( plug );

	queriesPlug()->removeChild( plug );
	outPlug()->removeChild( const_cast<ValuePlug *>( oPlug ) );
}

void AttributeQuery::affects( const Gaffer::Plug *input, AffectedPlugsContainer &outputs ) const
{
	ComputeNode::affects( input, outputs );

	if( input == attributesPlug() )
	{
		for( const Gaffer::PlugPtr &child : Gaffer::Plug::OutputRange( *outPlug() ) )
		{
			outputs.push_back( child->getChild<const Gaffer::BoolPlug>( g_existsPlugIndex ) );
			addLeafPlugs( child->getChild<const Gaffer::ValuePlug>( g_valuePlugIndex ), outputs );
		}
	}
	else if( input == internalSourcesPlug() )
	{
		for( const Gaffer::PlugPtr &child : Gaffer::Plug::OutputRange( *outPlug() ) )
		{
			outputs.push_back( child->getChild<const Gaffer::IntPlug>( g_sourcePlugIndex ) );
		}
	}
	else if( input == useMetadataPlug() || input == internalLocationExistsPlug() )
	{
		for( const Gaffer::PlugPtr &child : Gaffer::Plug::OutputRange( *outPlug() ) )
		{
			outputs.push_back( child->getChild<const Gaffer::IntPlug>( g_sourcePlugIndex ) );
			addLeafPlugs( child->getChild<const Gaffer::ValuePlug>( g_valuePlugIndex ), outputs );
		}
	}
	else if(
		( input == inheritPlug() ) ||
		( input == locationPlug() ) ||
		( input == scenePlug()->existsPlug() ) ||
		( input == scenePlug()->attributesPlug() ) ||
		( input == scenePlug()->globalsPlug() && !inheritPlug()->isSetToDefault() ) )
	{
		outputs.push_back( attributesPlug() );
		outputs.push_back( internalSourcesPlug() );
		if( input == locationPlug() || input == scenePlug()->existsPlug() )
		{
			outputs.push_back( internalLocationExistsPlug() );
		}
	}
	else if( queriesPlug()->isAncestorOf( input ) )
	{
		const NameValuePlug *childQueryPlug = input->ancestor<NameValuePlug>();
		if( childQueryPlug == nullptr )
		{
			throw IECore::Exception( "AttributeQuery::affects : Query plugs must be \"NameValuePlug\"" );
		}

		const ValuePlug *valuePlug = valuePlugFromQuery( childQueryPlug );
		if( input == childQueryPlug->namePlug() )
		{
			addLeafPlugs( valuePlug, outputs );
			outputs.push_back( existsPlugFromQuery( childQueryPlug ) );
			outputs.push_back( sourcePlugFromQuery( childQueryPlug ) );
		}
		else if( childQueryPlug->valuePlug() == input || childQueryPlug->valuePlug()->isAncestorOf( input ) )
		{
			outputs.push_back(
				correspondingPlug( childQueryPlug->valuePlug<ValuePlug>(), runTimeCast<const ValuePlug>( input ), valuePlug )
			);
		}
	}
}

void AttributeQuery::hash( const Gaffer::ValuePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ComputeNode::hash( output, context, h );

	if( output == attributesPlug() || output == internalSourcesPlug() )
	{
		const std::string location = locationPlug()->getValue();
		if( !location.empty() )
		{
			const ScenePlug::ScenePath path = ScenePlug::stringToPath( location );
			if( scenePlug()->exists( path ) )
			{
				const bool inherit = inheritPlug()->getValue();
				h.append( inherit );
				h.append( inherit ? scenePlug()->fullAttributesHash( path, /* withGlobalAttributes = */ true ) : scenePlug()->attributesHash( path ) );
			}
		}
	}
	else if( output == internalLocationExistsPlug() )
	{
		const std::string location = locationPlug()->getValue();
		h.append( !location.empty() && scenePlug()->exists( ScenePlug::stringToPath( location ) ) );
	}
	else if( outPlug()->isAncestorOf( output ) )
	{
		const Gaffer::ValuePlug *outputPlug = outPlug( output );
		const Gaffer::NameValuePlug *childQueryPlug = queryPlug( output );

		if( output == outputPlug->getChild( g_sourcePlugIndex ) )
		{
			internalSourcesPlug()->hash( h );
			childQueryPlug->namePlug()->hash( h );
			useMetadataPlug()->hash( h );
			internalLocationExistsPlug()->hash( h );
		}
		else if( output == outputPlug->getChild( g_existsPlugIndex ) )
		{
			attributesPlug()->hash( h );
			childQueryPlug->namePlug()->hash( h );
		}
		else if(
			output == outputPlug->getChild( g_valuePlugIndex ) ||
			outputPlug->getChild( g_valuePlugIndex )->isAncestorOf( output )
		)
		{
			attributesPlug()->hash( h );
			childQueryPlug->namePlug()->hash( h );
			useMetadataPlug()->hash( h );
			internalLocationExistsPlug()->hash( h );
			correspondingPlug(
				valuePlugFromQuery( childQueryPlug ),
				output,
				static_cast<const ValuePlug *>( childQueryPlug->valuePlug() )
			)->hash( h );
		}
	}
}

void AttributeQuery::compute( Gaffer::ValuePlug *output, const Gaffer::Context *context ) const
{
	if( output == attributesPlug() )
	{
		const std::string location = locationPlug()->getValue();
		if( !location.empty() )
		{
			const ScenePlug::ScenePath path = ScenePlug::stringToPath( location );
			if( scenePlug()->exists( path ) )
			{
				const IECore::ConstCompoundObjectPtr attributes = inheritPlug()->getValue() ? scenePlug()->fullAttributes( path, /* withGlobalAttributes = */ true ) : scenePlug()->attributes( path );
				static_cast<CompoundObjectPlug *>( output )->setValue( attributes );
				return;
			}
		}

		output->setToDefault();
		return;
	}
	else if( output == internalSourcesPlug() )
	{
		IECore::CompoundDataPtr resultData = new IECore::CompoundData;
		IECore::CompoundDataMap &result = resultData->writable();

		const std::string location = locationPlug()->getValue();
		if( !location.empty() )
		{
			const ScenePlug::ScenePath path = ScenePlug::stringToPath( location );
			if( scenePlug()->exists( path ) )
			{
				const IECore::ConstCompoundObjectPtr local = scenePlug()->attributes( path );
				for( const auto &a : local->members() )
				{
					result[ a.first ] = g_sourceLocal;
				}

				if( inheritPlug()->getValue() )
				{
					const IECore::ConstCompoundObjectPtr inherited = scenePlug()->fullAttributes( path );
					for( const auto &a : inherited->members() )
					{
						result.insert( { a.first, g_sourceInherited } );
					}

					const IECore::ConstCompoundObjectPtr globals = scenePlug()->globals();
					for( const auto &g : globals->members() )
					{
						if( boost::starts_with( g.first.string(), g_attributePrefix ) )
						{
							result.insert( {
								g.first.string().substr( g_attributePrefix.size() ),
								g_sourceGlobals
							} );
						}
					}
				}
			}
		}

		static_cast<AtomicCompoundDataPlug *>( output )->setValue( resultData );
		return;
	}
	else if( output == internalLocationExistsPlug() )
	{
		const std::string location = locationPlug()->getValue();
		static_cast<Gaffer::BoolPlug *>( output )->setValue(
			!location.empty() && scenePlug()->exists( ScenePlug::stringToPath( location ) )
		);
		return;
	}
	else if( outPlug()->isAncestorOf( output ) )
	{
		const ValuePlug *outputPlug = outPlug( output );
		const NameValuePlug *childQueryPlug = queryPlug( output );
		const std::string attributeName = childQueryPlug->namePlug()->getValue();

		if( output == outputPlug->getChild( g_sourcePlugIndex ) )
		{
			int source = g_sourceNone->readable();
			if( !attributeName.empty() )
			{
				const IECore::ConstCompoundDataPtr sources = internalSourcesPlug()->getValue();
				assert( sources );
				if( const auto s = sources->member<IECore::IntData>( attributeName ) )
				{
					source = s->readable();
				}
				else if(
					useMetadataPlug()->getValue() && internalLocationExistsPlug()->getValue() &&
					Metadata::value( g_attributePrefix + attributeName, g_defaultValue )
				)
				{
					source = g_sourceFallback->readable();
				}
			}
			static_cast<Gaffer::IntPlug *>( output )->setValue( source );
			return;
		}

		const auto attributes = attributesPlug()->getValue();
		assert( attributes );

		if( output == outputPlug->getChild( g_existsPlugIndex ) )
		{
			bool exists = false;
			if( !attributeName.empty() )
			{
				exists = attributes->members().count( attributeName );
			}
			static_cast<Gaffer::BoolPlug *>( output )->setValue( exists );
			return;
		}

		const ValuePlug *valuePlug = outputPlug->getChild<ValuePlug>( g_valuePlugIndex );
		if( output == valuePlug || valuePlug->isAncestorOf( output ) )
		{
			if( const Object *attribute = attributes->member<Object>( attributeName ) )
			{
				if( auto objectPlug = runTimeCast<ObjectPlug>( output ) )
				{
					objectPlug->setValue( attribute );
					return;
				}
				if( const auto data = runTimeCast<const Data>( attribute ) )
				{
					if( PlugAlgo::setValueFromData( valuePlug, output, data ) )
					{
						return;
					}
				}
			}

			if( useMetadataPlug()->getValue() && internalLocationExistsPlug()->getValue() )
			{
				if( const auto defaultValue = Metadata::value( g_attributePrefix + attributeName, g_defaultValue ) )
				{
					if( PlugAlgo::setValueFromData( valuePlug, output, defaultValue.get() ) )
					{
						return;
					}
				}
			}

			output->setFrom(
				correspondingPlug( valuePlug, output, childQueryPlug->valuePlug<ValuePlug>() )
			);
			return;
		}
	}

	ComputeNode::compute( output, context );
}

const Gaffer::BoolPlug *AttributeQuery::existsPlugFromQuery( const Gaffer::NameValuePlug *queryPlug ) const
{
	if( const ValuePlug *oPlug = outPlugFromQuery( queryPlug ) )
	{
		return oPlug->getChild<BoolPlug>( g_existsPlugIndex );
	}

	throw IECore::Exception( "AttributeQuery : \"exists\" plug is missing or of the wrong type." );
}

const Gaffer::IntPlug *AttributeQuery::sourcePlugFromQuery( const Gaffer::NameValuePlug *queryPlug ) const
{
	if( const ValuePlug *oPlug = outPlugFromQuery( queryPlug ) )
	{
		return oPlug->getChild<IntPlug>( g_sourcePlugIndex );
	}

	throw IECore::Exception( "AttributeQuery : \"source\" plug is missing or of the wrong type." );
}

const Gaffer::ValuePlug *AttributeQuery::valuePlugFromQuery( const Gaffer::NameValuePlug *queryPlug ) const
{
	if( const ValuePlug *oPlug = outPlugFromQuery( queryPlug ) )
	{
		return oPlug->getChild<const ValuePlug>( g_valuePlugIndex );
	}

	throw IECore::Exception( "AttributeQuery : \"value\" plug is missing." );
}

const Gaffer::ValuePlug *AttributeQuery::outPlugFromQuery( const Gaffer::NameValuePlug *queryPlug ) const
{
	size_t childIndex = getChildIndex( queriesPlug(), queryPlug );

	if( childIndex < outPlug()->children().size() )
	{
		const ValuePlug *oPlug = outPlug()->getChild<const ValuePlug>( childIndex );
		if( oPlug != nullptr && oPlug->typeId() != Gaffer::ValuePlug::staticTypeId() )
		{
			throw IECore::Exception( "AttributeQuery : \"outPlug\" must be a `ValuePlug`." );
		}
		return outPlug()->getChild<ValuePlug>( childIndex );
	}

	throw IECore::Exception( "AttributeQuery : \"outPlug\" is missing." );
}

const Gaffer::NameValuePlug *AttributeQuery::queryPlug( const Gaffer::ValuePlug *outputPlug ) const
{
	const size_t childIndex = getChildIndex( outPlug(), outputPlug );

	if( childIndex >= queriesPlug()->children().size() )
	{
		throw IECore::Exception( "AttributeQuery : \"query\" plug is missing." );
	}

	if( const NameValuePlug *childQueryPlug = queriesPlug()->getChild<NameValuePlug>( childIndex ) )
	{
		return childQueryPlug;
	}

	throw IECore::Exception( "AttributeQuery::queryPlug : Queries must be a \"NameValuePlug\"." );
}

const Gaffer::ValuePlug *AttributeQuery::outPlug( const Gaffer::ValuePlug *outputPlug ) const
{
	size_t childIndex = getChildIndex( outPlug(), outputPlug );

	if( const ValuePlug *result = outPlug()->getChild<const ValuePlug>( childIndex ) )
	{
		return result;
	}

	throw IECore::Exception( "AttributeQuery : \"out\" plug is missing or of the wrong type." );
}
