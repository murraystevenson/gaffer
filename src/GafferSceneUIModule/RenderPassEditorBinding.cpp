//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2023, Cinesite VFX Ltd. All rights reserved.
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

#include "RenderPassEditorBinding.h"

#include "GafferSceneUI/Private/Inspector.h"
#include "GafferSceneUI/Private/OptionInspector.h"
#include "GafferSceneUI/Private/RenderPassPath.h"

#include "GafferSceneUI/ContextAlgo.h"

#include "GafferUI/PathColumn.h"

#include "Gaffer/Context.h"
#include "Gaffer/Path.h"
#include "Gaffer/PathFilter.h"
#include "Gaffer/ScriptNode.h"

#include "IECorePython/RefCountedBinding.h"

#include "IECore/CamelCase.h"
#include "IECore/StringAlgo.h"

using namespace std;
using namespace boost::placeholders;
using namespace boost::python;
using namespace IECore;
using namespace IECorePython;
using namespace Gaffer;
using namespace GafferUI;
using namespace GafferScene;
using namespace GafferSceneUI;
using namespace GafferSceneUI::Private;

namespace
{

const InternedString g_renderPassContextName( "renderPass" );
const InternedString g_renderPassNamePropertyName( "renderPassPath:name" );
const InternedString g_renderPassEnabledPropertyName( "renderPassPath:enabled" );

//////////////////////////////////////////////////////////////////////////
// RenderPassNameColumn
//////////////////////////////////////////////////////////////////////////

ConstStringDataPtr g_disabledRenderPassIcon = new StringData( "disabledRenderPass.png" );
ConstStringDataPtr g_renderPassIcon = new StringData( "renderPass.png" );
ConstStringDataPtr g_renderPassFolderIcon = new StringData( "renderPassFolder.png" );
const Color4fDataPtr g_dimmedForegroundColor = new Color4fData( Imath::Color4f( 152, 152, 152, 255 ) / 255.0f );

class RenderPassNameColumn : public StandardPathColumn
{

	public :

		IE_CORE_DECLAREMEMBERPTR( RenderPassNameColumn )

		RenderPassNameColumn()
			:	StandardPathColumn( "Name", "name" )
		{
		}

		CellData cellData( const Gaffer::Path &path, const IECore::Canceller *canceller ) const override
		{
			CellData result = StandardPathColumn::cellData( path, canceller );

			const auto renderPassName = runTimeCast<const IECore::StringData>( path.property( g_renderPassNamePropertyName, canceller ) );
			if( !renderPassName )
			{
				result.icon = g_renderPassFolderIcon;
			}
			else
			{
				if( const auto renderPassEnabled = runTimeCast<const IECore::BoolData>( path.property( g_renderPassEnabledPropertyName, canceller ) ) )
				{
					result.icon = renderPassEnabled->readable() ? g_renderPassIcon : g_disabledRenderPassIcon;
					result.foreground = renderPassEnabled->readable() ? nullptr : g_dimmedForegroundColor;
				}
				else
				{
					result.icon = g_renderPassIcon;
				}
			}

			return result;
		}

};

//////////////////////////////////////////////////////////////////////////
// RenderPassActiveColumn
//////////////////////////////////////////////////////////////////////////

class RenderPassActiveColumn : public PathColumn
{

	public :

		IE_CORE_DECLAREMEMBERPTR( RenderPassActiveColumn )

		RenderPassActiveColumn()
			:	PathColumn()
		{
		}

		CellData cellData( const Gaffer::Path &path, const IECore::Canceller *canceller ) const override
		{
			CellData result;

			auto renderPassPath = runTimeCast<const RenderPassPath>( &path );
			if( !renderPassPath )
			{
				return result;
			}

			const auto renderPassName = runTimeCast<const IECore::StringData>( path.property( g_renderPassNamePropertyName, canceller ) );
			if( !renderPassName )
			{
				return result;
			}

			auto iconData = new CompoundData;
			result.icon = iconData;

			if( const std::string *currentPassName = renderPassPath->getContext()->getIfExists< std::string >( g_renderPassContextName ) )
			{
				if( *currentPassName == renderPassName->readable() )
				{
					iconData->writable()["state:normal"] = g_activeRenderPassIcon;
					/// \todo This is only to allow sorting, replace with `CellData::sortValue` in Gaffer 1.4
					result.value = new StringData( " " );
					result.toolTip = new StringData( fmt::format( "{} is the currently active render pass.", renderPassName->readable() ) );

					return result;
				}
			}

			iconData->writable()["state:highlighted"] = g_activeRenderPassFadedHighlightedIcon;
			result.toolTip = new StringData( fmt::format( "Double-click to set {} as the active render pass.", renderPassName->readable() ) );

			return result;
		}

		CellData headerData( const IECore::Canceller *canceller ) const override
		{
			return CellData( nullptr, /* icon = */ g_activeRenderPassIcon, /* background = */ nullptr, new IECore::StringData( "The currently active render pass." ) );
		}

		static IECore::StringDataPtr g_activeRenderPassIcon;
		static IECore::StringDataPtr g_activeRenderPassFadedHighlightedIcon;

};

StringDataPtr RenderPassActiveColumn::g_activeRenderPassIcon = new StringData( "activeRenderPass.png" );
StringDataPtr RenderPassActiveColumn::g_activeRenderPassFadedHighlightedIcon = new StringData( "activeRenderPassFadedHighlighted.png" );

//////////////////////////////////////////////////////////////////////////
// OptionInspectorColumn
//////////////////////////////////////////////////////////////////////////

/// \todo This map of SourceType colours is a duplicate of the one in LightEditorBinding.cpp.
/// We should consolidate these in the future.
const boost::container::flat_map<int, ConstColor4fDataPtr> g_sourceTypeColors = {
	{ (int)Inspector::Result::SourceType::Upstream, nullptr },
	{ (int)Inspector::Result::SourceType::EditScope, new Color4fData( Imath::Color4f( 48, 100, 153, 150 ) / 255.0f ) },
	{ (int)Inspector::Result::SourceType::Downstream, new Color4fData( Imath::Color4f( 239, 198, 24, 104 ) / 255.0f ) },
	{ (int)Inspector::Result::SourceType::Other, nullptr },
	{ (int)Inspector::Result::SourceType::Fallback, nullptr },
};
const Color4fDataPtr g_fallbackValueForegroundColor = new Color4fData( Imath::Color4f( 163, 163, 163, 255 ) / 255.0f );

class OptionInspectorColumn : public PathColumn
{

	public :

		IE_CORE_DECLAREMEMBERPTR( OptionInspectorColumn )

		OptionInspectorColumn( GafferSceneUI::Private::OptionInspectorPtr inspector, const std::string &columnName, const std::string &columnToolTip )
			:	m_inspector( inspector ), m_headerValue( columnName != "" ? new StringData( columnName ) : headerValue( inspector->name() ) ), m_headerToolTip( new IECore::StringData( columnToolTip ) )
		{
			m_inspector->dirtiedSignal().connect( boost::bind( &OptionInspectorColumn::inspectorDirtied, this ) );
		}

		GafferSceneUI::Private::Inspector *inspector()
		{
			return m_inspector.get();
		}

		CellData cellData( const Gaffer::Path &path, const IECore::Canceller *canceller ) const override
		{
			CellData result;

			auto renderPassPath = runTimeCast<const RenderPassPath>( &path );
			if( !renderPassPath )
			{
				return result;
			}

			const auto renderPassName = runTimeCast<const IECore::StringData>( path.property( g_renderPassNamePropertyName, canceller ) );
			if( !renderPassName )
			{
				return result;
			}

			Context::EditableScope scope( renderPassPath->getContext() );
			scope.setCanceller( canceller );
			scope.set( g_renderPassContextName, &( renderPassName->readable() ) );

			Inspector::ConstResultPtr inspectorResult = m_inspector->inspect();
			if( !inspectorResult )
			{
				return result;
			}

			result.value = runTimeCast<const IECore::Data>( inspectorResult->value() );
			/// \todo Should PathModel create a decoration automatically when we
			/// return a colour for `Role::Value`?
			result.icon = runTimeCast<const Color3fData>( inspectorResult->value() );
			result.background = g_sourceTypeColors.at( (int)inspectorResult->sourceType() );
			std::string toolTip;
			if( inspectorResult->sourceType() == Inspector::Result::SourceType::Fallback )
			{
				toolTip = "Source : Default value";
				result.foreground = g_fallbackValueForegroundColor;
			}
			else if( const auto source = inspectorResult->source() )
			{
				toolTip = "Source : " + source->relativeName( source->ancestor<ScriptNode>() );
			}

			if( inspectorResult->editable() )
			{
				toolTip += !toolTip.empty() ? "\n\n" : "";
				if( runTimeCast<const IECore::BoolData>( result.value ) )
				{
					toolTip += "Double-click to toggle";
				}
				else
				{
					toolTip += "Double-click to edit";
				}
			}

			if( !toolTip.empty() )
			{
				result.toolTip = new StringData( toolTip );
			}

			return result;
		}

		CellData headerData( const IECore::Canceller *canceller ) const override
		{
			return CellData( m_headerValue, /* icon = */ nullptr, /* background = */ nullptr, m_headerToolTip );
		}

	private :

		void inspectorDirtied()
		{
			changedSignal()( this );
		}

		static IECore::ConstStringDataPtr headerValue( const std::string &inspectorName )
		{
			std::string name = inspectorName;
			// Convert from snake case and/or camel case to UI case.
			if( name.find( '_' ) != std::string::npos )
			{
				std::replace( name.begin(), name.end(), '_', ' ' );
			}
			if( name.find( ' ' ) != std::string::npos )
			{
				name = CamelCase::fromSpaced( name );
			}
			return new StringData( CamelCase::toSpaced( name ) );
		}

		const OptionInspectorPtr m_inspector;
		const ConstStringDataPtr m_headerValue;
		const ConstStringDataPtr m_headerToolTip;

};

PathColumn::CellData headerDataWrapper( PathColumn &pathColumn, const Canceller *canceller )
{
	IECorePython::ScopedGILRelease gilRelease;
	return pathColumn.headerData( canceller );
}

//////////////////////////////////////////////////////////////////////////
// RenderPassEditorSearchFilter - filters based on a match pattern. This
// removes non-leaf paths if all their children have also been
// removed by the filter.
//////////////////////////////////////////////////////////////////////////

/// \todo This is the same as the SetEditorSearchFilter, we'll need the non-leaf
/// path removal functionality when we start grouping render passes by category.
/// Could be worth turning into common functionality?
class RenderPassEditorSearchFilter : public Gaffer::PathFilter
{

	public :

		IE_CORE_DECLAREMEMBERPTR( RenderPassEditorSearchFilter )

		RenderPassEditorSearchFilter( IECore::CompoundDataPtr userData = nullptr )
			:	PathFilter( userData )
		{
		}

		void setMatchPattern( const string &matchPattern )
		{
			if( m_matchPattern == matchPattern )
			{
				return;
			}
			m_matchPattern = matchPattern;
			m_wildcardPattern = IECore::StringAlgo::hasWildcards( matchPattern ) ? matchPattern : "*" + matchPattern + "*";

			changedSignal()( this );
		}

		const string &getMatchPattern() const
		{
			return m_matchPattern;
		}

		void doFilter( std::vector<PathPtr> &paths, const IECore::Canceller *canceller ) const override
		{
			if( m_matchPattern.empty() || paths.empty() )
			{
				return;
			}

			paths.erase(
				std::remove_if(
					paths.begin(),
					paths.end(),
					[this] ( const auto &p ) { return remove( p ); }
				),
				paths.end()
			);
		}

		bool remove( PathPtr path ) const
		{
			if( !path->names().size() )
			{
				return true;
			}

			bool leaf = path->isLeaf();
			if( !leaf )
			{
				std::vector<PathPtr> c;
				path->children( c );

				leaf = std::all_of( c.begin(), c.end(), [this] ( const auto &p ) { return remove( p ); } );
			}

			const bool match = IECore::StringAlgo::matchMultiple( path->names().back().string(), m_wildcardPattern );

			return leaf && !match;
		}

	private:

		std::string m_matchPattern;
		std::string m_wildcardPattern;

};

//////////////////////////////////////////////////////////////////////////
// DisabledRenderPassFilter - filters out paths with a renderPassPath:enabled
// property value of `false`. This also removes non-leaf paths if all their
// children have been removed by the filter.
//////////////////////////////////////////////////////////////////////////

class DisabledRenderPassFilter : public Gaffer::PathFilter
{

	public :

		IE_CORE_DECLAREMEMBERPTR( DisabledRenderPassFilter )

		DisabledRenderPassFilter( IECore::CompoundDataPtr userData = nullptr )
			:	PathFilter( userData )
		{
		}

		void doFilter( std::vector<PathPtr> &paths, const IECore::Canceller *canceller ) const override
		{
			paths.erase(
				std::remove_if(
					paths.begin(),
					paths.end(),
					[this, canceller] ( auto &p ) { return remove( p, canceller ); }
				),
				paths.end()
			);
		}

		bool remove( PathPtr path, const IECore::Canceller *canceller ) const
		{
			if( !path->names().size() )
			{
				return true;
			}

			bool leaf = path->isLeaf();
			if( !leaf )
			{
				std::vector<PathPtr> c;
				path->children( c );

				leaf = std::all_of( c.begin(), c.end(), [this, canceller] ( const auto &p ) { return remove( p, canceller ); } );
			}

			bool enabled = false;
			if( runTimeCast<const IECore::StringData>( path->property( g_renderPassNamePropertyName, canceller ) ) )
			{
				if( const auto enabledData = IECore::runTimeCast<const IECore::BoolData>( path->property( g_renderPassEnabledPropertyName, canceller ) ) )
				{
					enabled = enabledData->readable();
				}
				else
				{
					enabled = true;
				}
			}

			return leaf && !enabled;
		}

};

} // namespace

//////////////////////////////////////////////////////////////////////////
// Bindings
//////////////////////////////////////////////////////////////////////////

void GafferSceneUIModule::bindRenderPassEditor()
{

	object module( borrowed( PyImport_AddModule( "GafferSceneUI._RenderPassEditor" ) ) );
	scope().attr( "_RenderPassEditor" ) = module;
	scope moduleScope( module );

	RefCountedClass<RenderPassNameColumn, GafferUI::PathColumn>( "RenderPassNameColumn" )
		.def( init<>() )
	;

	RefCountedClass<RenderPassActiveColumn, GafferUI::PathColumn>( "RenderPassActiveColumn" )
		.def( init<>() )
	;

	RefCountedClass<OptionInspectorColumn, GafferUI::PathColumn>( "OptionInspectorColumn" )
		.def( init<GafferSceneUI::Private::OptionInspectorPtr, const std::string &, const std::string &>(
			(
				arg_( "inspector" ),
				arg_( "columName" ) = "",
				arg_( "columnToolTip" ) = ""
			)
		) )
		.def( "inspector", &OptionInspectorColumn::inspector, return_value_policy<IECorePython::CastToIntrusivePtr>() )
		.def( "headerData", &headerDataWrapper, ( arg_( "canceller" ) = object() ) )
	;

	RefCountedClass<RenderPassEditorSearchFilter, PathFilter>( "SearchFilter" )
		.def( init<IECore::CompoundDataPtr>( ( boost::python::arg( "userData" ) = object() ) ) )
		.def( "setMatchPattern", &RenderPassEditorSearchFilter::setMatchPattern )
		.def( "getMatchPattern", &RenderPassEditorSearchFilter::getMatchPattern, return_value_policy<copy_const_reference>() )
	;

	RefCountedClass<DisabledRenderPassFilter, PathFilter>( "DisabledRenderPassFilter" )
		.def( init<IECore::CompoundDataPtr>( ( boost::python::arg( "userData" ) = object() ) ) )
	;

}
