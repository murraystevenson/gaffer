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

#include "GafferSceneUI/LightTool.h"

#include "GafferSceneUI/Private/MetadataValueParameterInspector.h"
#include "GafferSceneUI/Private/Inspector.h"
#include "GafferSceneUI/ContextAlgo.h"
#include "GafferSceneUI/SceneView.h"

#include "GafferScene/ScenePath.h"

#include "GafferUI/Handle.h"
#include "GafferUI/StandardStyle.h"

#include "Gaffer/Metadata.h"
#include "Gaffer/NameValuePlug.h"
#include "Gaffer/PathFilter.h"
#include "Gaffer/ScriptNode.h"
#include "Gaffer/TweakPlug.h"
#include "Gaffer/UndoScope.h"

#include "IECoreGL/CurvesPrimitive.h"
#include "IECoreGL/Group.h"
#include "IECoreGL/MeshPrimitive.h"
#include "IECoreGL/ShaderLoader.h"
#include "IECoreGL/ShaderStateComponent.h"
#include "IECoreGL/TextureLoader.h"
#include "IECoreGL/ToGLMeshConverter.h"

#include "IECoreScene/CurvesPrimitive.h"
#include "IECoreScene/MeshPrimitive.h"

#include "IECore/AngleConversion.h"

#include "boost/algorithm/string/predicate.hpp"
#include "boost/bind/bind.hpp"

#include "fmt/format.h"

using namespace boost::placeholders;
using namespace Imath;
using namespace IECoreScene;
using namespace IECoreGL;
using namespace Gaffer;
using namespace GafferUI;
using namespace GafferScene;
using namespace GafferSceneUI;
using namespace GafferSceneUI::Private;

namespace
{

const Color3f g_lightToolHandleColor = Color3f( 0.825, 0.720f, 0.230f );
const Color4f g_lightToolHandleColor4 = Color4f( g_lightToolHandleColor.x, g_lightToolHandleColor.y, g_lightToolHandleColor.z, 1.f );

// Color from `StandardLightVisualiser`
const Color3f g_lightToolHighlightColor = Color3f( 1.0f, 0.835f, 0.07f );
const Color4f g_lightToolHighlightColor4 = Color4f( g_lightToolHighlightColor.x, g_lightToolHighlightColor.y, g_lightToolHighlightColor.z, 1.f );

// Multiplied by the highlight color for drawing a parameter's previous value
const float g_highlightMultiplier = 0.8f;

const InternedString g_lightVisualiserScaleAttributeName( "gl:visualiser:scale" );
const InternedString g_frustumScaleAttributeName( "gl:light:frustumScale" );
const InternedString g_insetPenumbraType( "inset" );
const InternedString g_outsetPenumbraType( "outset" );
const InternedString g_absolutePenumbraType( "absolute" );
const float g_penumbraHandleZAxisRotation = 0.f;
const float g_spotLightHandleCubeScale = 0.5f;
const float g_minimumVisiblePenumbraAngle = 1.f;
const float g_coneSpokeLineWidth = 2.f;
const float g_penumbraSpokeLineWidth = 1.f;

// Return the plug that holds the value we need to edit, and make sure it's enabled.

/// \todo This currently does nothing to enable a row if is disabled. Is that worth doing?

Plug *activeValuePlug( Plug *sourcePlug )
{
	if( auto nameValuePlug = runTimeCast<NameValuePlug>( sourcePlug ) )
	{
		nameValuePlug->enabledPlug()->setValue( true );
		return nameValuePlug->valuePlug();
	}
	if( auto tweakPlug = runTimeCast<TweakPlug>( sourcePlug ) )
	{
		tweakPlug->enabledPlug()->setValue( true );
		return tweakPlug->valuePlug();
	}
	return sourcePlug;
}

const char *constantFragSource()
{
	return
		"#version 120\n"
		""
		"#if __VERSION__ <= 120\n"
		"#define in varying\n"
		"#endif\n"
		""
		"in vec3 fragmentCs;"
		""
		"void main()"
		"{"
			"gl_FragColor = vec4( fragmentCs, 1 );"
		"}"
	;
}

const char *translucentConstantFragSource()
{
	return
		"#if __VERSION__ <= 120\n"
		"#define in varying\n"
		"#endif\n"
		""
		"in vec3 fragmentCs;"
		""
		"void main()"
		"{"
		"	gl_FragColor = vec4( fragmentCs, 0.375 );"
		"}"
	;
}

IECoreGL::MeshPrimitivePtr cube()
{
	static IECoreGL::MeshPrimitivePtr result;
	if( result )
	{
		return result;
	}

	IECoreScene::MeshPrimitivePtr mesh = IECoreScene::MeshPrimitive::createBox(
		Box3f( V3f( -1 ), V3f( 1 ) )
	);

	ToGLMeshConverterPtr converter = new ToGLMeshConverter( mesh );
	result = runTimeCast<IECoreGL::MeshPrimitive>( converter->convert() );

	return result;
}

IECoreScene::MeshPrimitivePtr solidAngle( float radius, float startFraction, float stopFraction, Color3f color )
{
	IntVectorDataPtr vertsPerPolyData = new IntVectorData;
	IntVectorDataPtr vertIdsData = new IntVectorData;
	V3fVectorDataPtr pData = new V3fVectorData;

	std::vector<int> &vertsPerPoly = vertsPerPolyData->writable();
	std::vector<int> &vertIds = vertIdsData->writable();
	std::vector<V3f> &p = pData->writable();

	const int numCircleDivisions = 100;
	const int numSegments = std::max( 1, (int)ceil( abs( stopFraction - startFraction ) * numCircleDivisions ) );

	p.push_back( V3f( 0, 0, 0 ) );

	for( int i = 0; i < numSegments + 1; ++i )
	{
		const float a = ( startFraction + ( stopFraction - startFraction ) * (float)i / (float)numSegments ) * 2.f * M_PI;
		p.push_back( V3f( sin( a ), 0, cos( a ) ) * radius );
	}

	for( int i = 0; i < numSegments; ++i )
	{
		vertIds.push_back( i + 1 );
		vertIds.push_back( i + 2 );
		vertIds.push_back( 0 );
		vertsPerPoly.push_back( 3 );
	}

	IECoreScene::MeshPrimitivePtr solidArc = new IECoreScene::MeshPrimitive( vertsPerPolyData, vertIdsData, "linear", pData );
	solidArc->variables["N"] = IECoreScene::PrimitiveVariable( IECoreScene::PrimitiveVariable::Constant, new V3fData( V3f( 0, 1, 0 ) ) );
	solidArc->variables["Cs"] = IECoreScene::PrimitiveVariable( IECoreScene::PrimitiveVariable::Constant, new Color3fData( color ) );

	return solidArc;
}

class LightToolHandle : public Handle
{

	public :

		/// \todo SpotLightTool (below) is not using `metadataKey` because it knows what keys it needs.
		/// If that is going to be the case for other tools, we should remove it.
		LightToolHandle(
			const std::string &attributePattern,
			const InternedString &metadataKey,
			const std::string &name
		) :
			Handle( name ),
			m_attributePattern( attributePattern ),
			m_metadataKey( metadataKey ),
			m_lookThroughLight( false )
		{

		}
		~LightToolHandle()
		{

		}

		// Update inspectors and other data needed to display and interact with the tool.
		// Derived classes should call this parent method first, then implement custom logic.
		virtual void update( ScenePathPtr scenePath, const PlugPtr &editScope )
		{
			m_handleScenePath = scenePath;
			m_editScope = editScope;
		}

		const std::string attributePattern() const
		{
			return m_attributePattern;
		}

		ScenePath *handleScenePath() const
		{
			return m_handleScenePath.get();
		}

		Plug *editScope() const
		{
			return m_editScope.get();
		}

		void setLookThroughLight( bool lookThroughLight )
		{
			m_lookThroughLight = lookThroughLight;
		}

		bool getLookThroughLight() const
		{
			return m_lookThroughLight;
		}

		// Called at the beginning of a drag with the path to be inspected
		// set in the current context. Must be implemented by derived classes to collect
		// whatever data will be needed to implement the drag operation.
		virtual void addDragInspection() = 0;

		virtual bool handleDragMove( const GafferUI::DragDropEvent &event ) = 0;
		virtual bool handleDragEnd() = 0;

		// Must be implemented by derived classes to set the local transform of the handle
		// relative to the light.
		virtual void updateTransform() = 0;

		// Must be implemented by derived classes to return the visible and enabled state for
		// the `scenePath` in the current context.
		virtual bool visible() = 0;
		virtual bool enabled() = 0;

		// Must be implemented by derived classes to return all of the inspectors the handle uses.
		/// \todo Can this be removed? It's only used once now, to help get the script node for
		/// undo context.
		virtual std::vector<GafferSceneUI::Private::Inspector *> inspectors() const = 0;

	private :

		ScenePathPtr m_handleScenePath;

		const std::string m_attributePattern;
		const InternedString m_metadataKey;

		Gaffer::PlugPtr m_editScope;

		bool m_lookThroughLight;
};

class SpotLightHandle : public LightToolHandle
{

	public :

		enum class HandleType
		{
			Cone,
			Penumbra
		};

		SpotLightHandle(
			const std::string &attributePattern,
			const InternedString &metadataKey,
			HandleType handleType,
			SceneViewPtr view,
			const float zRotation,
			const std::string &name = "SpotLightHandle"
		) :
			LightToolHandle( attributePattern, metadataKey, name ),
			m_view( view ),
			m_zRotation( zRotation ),
			m_handleType( handleType ),
			m_visualiserScale( 1.f ),
			m_frustumScale( 1.f ),
			m_lensRadius( 0 )
		{

		}
		~SpotLightHandle() override
		{

		}

		void update( ScenePathPtr scenePath, const PlugPtr &editScope ) override
		{
			LightToolHandle::update( scenePath, editScope );

			if( !handleScenePath()->isValid() )
			{
				m_coneAngleInspector.reset();
				m_penumbraAngleInspector.reset();
				return;
			}

			m_coneAngleInspector = new MetadataValueParameterInspector(
				handleScenePath()->getScene(),
				this->editScope(),
				attributePattern(),
				"coneAngleParameter"
			);

			ConstCompoundObjectPtr attributes = handleScenePath()->getScene()->attributes( handleScenePath()->names() );

			auto visualiserScaleData = attributes->member<FloatData>( g_lightVisualiserScaleAttributeName );
			m_visualiserScale = visualiserScaleData ? visualiserScaleData->readable() : 1.f;

			auto frustumScaleData = attributes->member<FloatData>( g_frustumScaleAttributeName );
			m_frustumScale = frustumScaleData ? frustumScaleData->readable() : 1.f;

			/// \todo This is the same logic as `MetadataValueParameterInspector`, can it
			/// be removed when we transition to using UsdLux as our light representation?
			for( const auto &[attributeName, value] : attributes->members() )
			{
				if(
					StringAlgo::match( attributeName, attributePattern() ) &&
					value->typeId() == (IECore::TypeId)ShaderNetworkTypeId
				)
				{
					const auto shader = attributes->member<ShaderNetwork>( attributeName )->outputShader();
					std::string shaderAttribute = shader->getType() + ":" + shader->getName();

					auto penumbraTypeData = Metadata::value<StringData>( shaderAttribute, "penumbraType" );
					m_penumbraType = penumbraTypeData ? std::optional<InternedString>( InternedString( penumbraTypeData->readable() ) ) : std::nullopt;

					m_lensRadius = 0;
					if( auto lensRadiusParameterName = Metadata::value<StringData>( shaderAttribute, "lensRadiusParameter" ) )
					{
						if( auto lensRadiusData = shader->parametersData()->member<FloatData>( lensRadiusParameterName->readable() ) )
						{
							m_lensRadius = lensRadiusData->readable();
						}
					}

					m_penumbraAngleInspector.reset();
					if( auto penumbraParameterName = Metadata::value<StringData>( shaderAttribute, "penumbraAngleParameter" ) )
					{
						m_penumbraAngleInspector = new MetadataValueParameterInspector(
							handleScenePath()->getScene(),
							this->editScope(),
							attributePattern(),
							"penumbraAngleParameter"
						);
					}

					break;
				}
			}
		}

		void addDragInspection() override
		{
			Inspector::ResultPtr coneAngleInspection = m_coneAngleInspector->inspect();
			Inspector::ResultPtr penumbraAngleInspection = m_penumbraAngleInspector ? m_penumbraAngleInspector->inspect() : nullptr;

			ConstFloatDataPtr originalConeAngleData = runTimeCast<const IECore::FloatData>( coneAngleInspection->value() );
			assert( originalConeAngleData );  // Handle visibility and enabled state should ensure this is valid

			float originalPenumbraAngle = 0;
			if( penumbraAngleInspection )
			{
				ConstFloatDataPtr originalPenumbraAngleData = runTimeCast<const IECore::FloatData>( penumbraAngleInspection->value() );
				assert( originalPenumbraAngleData );

				originalPenumbraAngle = originalPenumbraAngleData->readable();
			}

			m_inspections.push_back(
				{
					coneAngleInspection,
					originalConeAngleData->readable(),
					penumbraAngleInspection,
					originalPenumbraAngle
				}
			);
		}

		bool handleDragMove( const GafferUI::DragDropEvent &event ) override
		{
			if( m_inspections.empty() )
			{
				return true;
			}

			float angleScale = 1.f;
			if( m_drag )
			{
				const float newAngle =  radiansToDegrees( m_drag.value().updatedRotation( event ) );

				// For inset penumbras, the value of `updatedRotation()` will be negative for
				// positive penumbra angles. The negative values work out to a positive value
				// when multiplying them together. To drag out of 0, we have to seed the value
				// with a similarly negative value to keep the computations consistent.
				float zeroAngle = !m_penumbraType || m_penumbraType.value() == g_insetPenumbraType ? -1.f : 1.f;
				angleScale = newAngle / ( m_dragStartAngle != 0 ? m_dragStartAngle : zeroAngle );
			}
			else
			{
				V2f endPosition = m_view->viewportGadget()->gadgetToRasterSpace( event.line.p1, this );
				V2f viewport = V2f( m_view->viewportGadget()->getViewport() );

				if(
					m_handleType == HandleType::Cone ||
					( m_handleType == HandleType::Penumbra && m_penumbraType == g_absolutePenumbraType )
				)
				{
					angleScale =  ( endPosition - viewport * 0.5f ).length2() / m_dragViewportStartLength2;
				}
				else
				{
					/// \todo These should be computed based on the raster space radius of the cone angle,
					/// but first we need a way to get that radius...
					if( !m_penumbraType || m_penumbraType == g_insetPenumbraType )
					{
						angleScale =  m_dragViewportStartLength2 / ( endPosition - viewport * 0.5f ).length2();
					}
					else if( m_penumbraType == g_outsetPenumbraType )
					{
						angleScale =  ( endPosition - viewport * 0.5f ).length2() / m_dragViewportStartLength2;
					}
				}
			}

			// Find an `angleScale` that all lights can use without going past limits for
			// penumbra and cone angles.

			for( auto &[coneInspection, originalConeAngle, penumbraInspection, originalPenumbraAngle] : m_inspections )
			{
				const float startConeAngle = originalConeAngle != 0 ? originalConeAngle : 1.f;
				const float startPenumbraAngle = originalPenumbraAngle != 0 ? originalPenumbraAngle : 1.f;

				if( m_handleType == HandleType::Penumbra && ( !m_penumbraType || m_penumbraType == g_insetPenumbraType ) )
				{
					angleScale = std::min( angleScale, ( originalConeAngle * 0.5f ) / startPenumbraAngle );
					angleScale = std::max( angleScale, 0.f );
				}
				else if( m_handleType == HandleType::Cone && ( !m_penumbraType || m_penumbraType == g_insetPenumbraType ) )
				{
					angleScale = std::min( angleScale, 180.f / startConeAngle );
					angleScale = std::max( angleScale, ( originalPenumbraAngle * 2.f ) / startConeAngle );
				}
				else if( m_handleType == HandleType::Penumbra && m_penumbraType == g_outsetPenumbraType )
				{
					angleScale = std::min( angleScale, ( 90.f - ( originalConeAngle * 0.5f ) ) / startPenumbraAngle );
					angleScale = std::max( angleScale, 0.f );
				}
				else if( m_handleType == HandleType::Cone && m_penumbraType == g_outsetPenumbraType )
				{
					angleScale = std::min( angleScale, ( 90.f - originalPenumbraAngle ) / ( startConeAngle * 0.5f ) );
					angleScale = std::max( angleScale, 0.f );
				}
				else if( m_handleType == HandleType::Penumbra && m_penumbraType == g_absolutePenumbraType )
				{
					angleScale = std::min( angleScale, originalConeAngle / startPenumbraAngle );
					angleScale = std::max( angleScale, 0.f );
				}
				else if( m_handleType == HandleType::Cone && m_penumbraType == g_absolutePenumbraType )
				{
					angleScale = std::min( angleScale, 180.f / startConeAngle );
					angleScale = std::max( angleScale, originalPenumbraAngle / startConeAngle );
				}
				else if( m_handleType == HandleType::Cone )
				{
					angleScale = std::min( angleScale, 180.f / startConeAngle );
					angleScale = std::max( angleScale, 0.f );
				}
			}

			for( auto &[coneInspection, originalConeAngle, penumbraInspection, originalPenumbraAngle] : m_inspections )
			{
				if( m_handleType == HandleType::Cone )
				{
					ValuePlugPtr conePlug = coneInspection->acquireEdit();
					auto coneFloatPlug = runTimeCast<FloatPlug>( activeValuePlug( conePlug.get() ) );
					if( !coneFloatPlug )
					{
						throw Exception( "Invalid type for \"coneAngleParameter\"" );
					}

					coneFloatPlug->setValue( ( originalConeAngle != 0 ? originalConeAngle : 1.f ) * angleScale );
				}

				if( m_handleType == HandleType::Penumbra )
				{
					ValuePlugPtr penumbraPlug = penumbraInspection->acquireEdit();
					auto penumbraFloatPlug = runTimeCast<FloatPlug>( activeValuePlug( penumbraPlug.get() ) );
					if( !penumbraFloatPlug )
					{
						throw Exception( "Inavlid type for \"penumbraAngleParameter\"" );
					}

					penumbraFloatPlug->setValue( ( originalPenumbraAngle != 0 ? originalPenumbraAngle : 1.f ) * angleScale );
				}
			}

			return true;
		}

		bool handleDragEnd() override
		{
			m_inspections.clear();
			m_drag = std::nullopt;

			return false;
		}

		void updateTransform() override
		{
			const auto &[coneAngle, penumbraAngle] = spotLightAngleValues();
			const float angle = degreesToRadians( handleAngle( coneAngle, penumbraAngle ) );

			M44f transform =
				M44f().rotate( V3f( 0, angle, 0 ) ) *
				M44f().translate( V3f( m_lensRadius, 0, 0 ) ) *
				M44f().rotate( V3f( 0, 0, degreesToRadians( m_zRotation ) ) )
			;

			if( m_handleType == HandleType::Penumbra )
			{
				transform *= M44f().rotate(  V3f( 0, 0, degreesToRadians( g_penumbraHandleZAxisRotation ) ) );
			}

			setTransform( transform );
		}

		bool visible() override
		{
			const auto &[coneAngle, penumbraAngle] = spotLightAngleValues();
			if( m_handleType == HandleType::Penumbra && penumbraAngle && penumbraAngle.value() < g_minimumVisiblePenumbraAngle )
			{
				return false;
			}

			bool visible = m_coneAngleInspector ? (bool)m_coneAngleInspector->inspect() : false;

			if( m_handleType == HandleType::Penumbra )
			{
				visible &= m_penumbraAngleInspector ? (bool)m_penumbraAngleInspector->inspect() : false;
			}

			return visible;
		}

		bool enabled() override
		{
			const auto &[coneAngle, penumbraAngle] = spotLightAngleValues();
			if( m_handleType == HandleType::Penumbra && penumbraAngle && penumbraAngle.value() < g_minimumVisiblePenumbraAngle )
			{
				return false;
			}

			bool enabled = (bool)m_coneAngleInspector;
			Inspector::ResultPtr coneAngleInspection = m_coneAngleInspector ? m_coneAngleInspector->inspect() : nullptr;

			enabled &= coneAngleInspection ? coneAngleInspection->editable() : false;

			if( m_handleType == HandleType::Penumbra )
			{
				enabled &= (bool)m_penumbraAngleInspector;
				Inspector::ResultPtr penumbraAngleInspection = m_penumbraAngleInspector ? m_penumbraAngleInspector->inspect() : nullptr;
				enabled &= penumbraAngleInspection ? penumbraAngleInspection->editable() : false;
			}

			return enabled;
		}

		std::vector<GafferSceneUI::Private::Inspector *> inspectors() const override
		{
			if( m_handleType == HandleType::Cone )
			{
				return {m_coneAngleInspector.get()};
			}
			if(
				(
					!m_penumbraType ||
					m_penumbraType == g_insetPenumbraType ||
					m_penumbraType == g_outsetPenumbraType
				)
			)
			{
				return {m_coneAngleInspector.get(), m_penumbraAngleInspector.get()};
			}
			return {m_penumbraAngleInspector.get()};
		}

	protected :

		void renderHandle( const Style *style, Style::State state ) const override
		{
			State::bindBaseState();
			State *glState = const_cast<State *>( State::defaultState() );

			IECoreGL::GroupPtr group = new IECoreGL::Group;

			GroupPtr wireGroup = new Group;

			wireGroup->getState()->add( new IECoreGL::Primitive::DrawWireframe( false ) );
			wireGroup->getState()->add( new IECoreGL::Primitive::DrawSolid( true ) );
			wireGroup->getState()->add( new IECoreGL::CurvesPrimitive::UseGLLines( true ) );
			wireGroup->getState()->add(
				new IECoreGL::CurvesPrimitive::GLLineWidth(
					m_handleType == HandleType::Cone ? g_coneSpokeLineWidth : g_penumbraSpokeLineWidth
				)
			);
			wireGroup->getState()->add( new IECoreGL::LineSmoothingStateComponent( true ) );

			wireGroup->getState()->add(
				new IECoreGL::ShaderStateComponent(
					ShaderLoader::defaultShaderLoader(),
					TextureLoader::defaultTextureLoader(),
					"",
					"",
					constantFragSource(),
					new CompoundObject
				)
			);

			const V3f rasterScale = rasterScaleFactor();

			IntVectorDataPtr vertsPerCurve = new IntVectorData( {2} );
			V3fVectorDataPtr p = new V3fVectorData(
				{
					V3f( 0 ),
					V3f( 0, 0, m_visualiserScale * m_frustumScale * -10.f ) / rasterScale
				}
			);

			IECoreGL::CurvesPrimitivePtr ray = new IECoreGL::CurvesPrimitive( IECore::CubicBasisf::linear(), false, vertsPerCurve );

			ray->addPrimitiveVariable( "P", IECoreScene::PrimitiveVariable( IECoreScene::PrimitiveVariable::Vertex, p ) );

			wireGroup->addChild( ray );

			group->addChild( wireGroup );

			IECoreGL::GroupPtr iconGroup = new IECoreGL::Group;

			iconGroup->getState()->add(
				new IECoreGL::ShaderStateComponent(
					ShaderLoader::defaultShaderLoader(),
					TextureLoader::defaultTextureLoader(),
					"",
					"",
					constantFragSource(),
					new CompoundObject
				)
			);

			IECoreGL::GroupPtr nearIconGroup = new IECoreGL::Group;
			nearIconGroup->addChild( cube() );
			nearIconGroup->setTransform(
				M44f().scale( V3f( g_spotLightHandleCubeScale * .5f / rasterScale.x ) ) * (
					M44f().translate( V3f( 0, 0, -m_visualiserScale ) / rasterScale )
				)
			);

			IECoreGL::GroupPtr farIconGroup = new IECoreGL::Group;
			farIconGroup->addChild( cube() );
			farIconGroup->setTransform(
				M44f().scale( V3f( g_spotLightHandleCubeScale / rasterScale.x ) ) * (
					M44f().translate( V3f( 0, 0, m_frustumScale * m_visualiserScale * -10.f ) / rasterScale )
				)
			);

			iconGroup->addChild( nearIconGroup );
			iconGroup->addChild( farIconGroup );

			group->addChild( iconGroup );

			auto standardStyle = runTimeCast<const StandardStyle>( style );
			assert( standardStyle );
			Color3f highlightColor3 = standardStyle->getColor( StandardStyle::Color::HighlightColor );
			Color4f highlightColor4 = Color4f( highlightColor3.x, highlightColor3.y, highlightColor3.z, 1.f );
			const bool highlighted = state == Style::State::HighlightedState || m_drag;

			iconGroup->getState()->add(
				new IECoreGL::Color(
					highlighted ? g_lightToolHighlightColor4 : g_lightToolHandleColor4
				)
			);

			wireGroup->getState()->add(
				new IECoreGL::Color(
					highlighted ? g_lightToolHighlightColor4 : highlightColor4
				)
			);

			if( m_drag )
			{
				const auto &[coneAngle, penumbraAngle] = spotLightAngleValues();
				float angle = angleToArcAngle( m_handleType == HandleType::Cone ? coneAngle : penumbraAngle.value() );

				float currentFraction = angle / 360.f;
				float previousFraction = !m_inspections.empty() ? m_dragStartAngle / 360.f : currentFraction;

				IECoreScene::MeshPrimitivePtr previousSolidAngle = nullptr;
				IECoreScene::MeshPrimitivePtr currentSolidAngle = nullptr;

				Color3f previousColor = g_lightToolHandleColor * g_highlightMultiplier;
				Color3f currentColor = g_lightToolHandleColor;

				if(
					(
						( m_handleType == HandleType::Cone || !( !m_penumbraType || m_penumbraType == g_insetPenumbraType ) ) &&
						currentFraction > previousFraction
					) ||
					(
						( m_handleType == HandleType::Penumbra && ( !m_penumbraType || m_penumbraType == g_insetPenumbraType ) ) &&
						currentFraction < previousFraction
					)
				)
				{
					previousSolidAngle = solidAngle( -m_arcRadius, 0, -( currentFraction - previousFraction ), currentColor );
					currentSolidAngle = solidAngle( -m_arcRadius, -( currentFraction - previousFraction ), -currentFraction, previousColor );
				}
				else if(
					(
						( m_handleType == HandleType::Cone || !( !m_penumbraType || m_penumbraType == g_insetPenumbraType ) ) &&
						currentFraction < previousFraction
					) ||
					(
						( m_handleType == HandleType::Penumbra && ( !m_penumbraType || m_penumbraType == g_insetPenumbraType ) ) &&
						currentFraction > previousFraction
					)
				)
				{
					previousSolidAngle = solidAngle( -m_arcRadius, 0, previousFraction - currentFraction, previousColor );
					currentSolidAngle = solidAngle( -m_arcRadius, 0, -currentFraction, currentColor );
				}
				else
				{
					currentSolidAngle = solidAngle( -m_arcRadius, 0, -currentFraction, previousColor );
				}

				IECoreGL::GroupPtr solidAngleGroup = new IECoreGL::Group;
				solidAngleGroup->getState()->add(
					new IECoreGL::ShaderStateComponent(
						ShaderLoader::defaultShaderLoader(),
						TextureLoader::defaultTextureLoader(),
						"",  // vertexSource
						"",  // geometrySource
						translucentConstantFragSource(),
						new CompoundObject
					)
				);

				if( currentSolidAngle )
				{
					ToGLMeshConverterPtr meshConverter = new ToGLMeshConverter( currentSolidAngle );
					solidAngleGroup->addChild( runTimeCast<IECoreGL::Renderable>( meshConverter->convert() ) );
				}
				if( previousSolidAngle )
				{
					ToGLMeshConverterPtr meshConverter = new ToGLMeshConverter( previousSolidAngle );
					solidAngleGroup->addChild( runTimeCast<IECoreGL::Renderable>( meshConverter->convert() ) );
				}

				group->addChild( solidAngleGroup );
			}

			group->render( glState );
		}

	private :

		void dragBegin( const DragDropEvent &event ) override
		{
			const auto &[coneAngle, penumbraAngle] = spotLightAngleValues();

			m_dragStartAngle = angleToArcAngle(
				m_handleType == HandleType::Cone ? coneAngle : penumbraAngle.value()
			);

			if( !getLookThroughLight() )
			{
				M44f r = M44f().rotate( V3f( 0, degreesToRadians( -m_dragStartAngle ), 0 ) );

				m_drag = AngularDrag(
					this,
					V3f( 0, 0, 0 ),
					V3f( 0, 1.f, 0 ),
					V3f( -m_visualiserScale, 0, 0 ) * r,
					event
				);

				const M44f worldTransform = fullTransform();
				const Line3f rayLine(
					V3f( 0 ) * worldTransform,
					V3f( 0, 0, m_visualiserScale * m_frustumScale * -10.f ) * worldTransform
				);
				const V3f dragPoint = rayLine.closestPointTo( Line3f( event.line.p0, event.line.p1 ) * worldTransform );
				m_arcRadius = ( V3f( 0 ) * worldTransform - dragPoint ).length() / rasterScaleFactor().x;
			}
			else
			{
				V2f position = m_view->viewportGadget()->gadgetToRasterSpace( event.line.p0, this );
				V2f viewport = V2f( m_view->viewportGadget()->getViewport() );

				m_dragViewportStartLength2 = ( position - viewport * 0.5f ).length2();

			}
		}

		std::pair<float, std::optional<float>> spotLightAngleValues() const
		{
			ScenePlug::PathScope pathScope( handleScenePath()->getContext() );
			pathScope.setPath( &handleScenePath()->names() );

			float coneAngle = 0;

			if( Inspector::ResultPtr coneInspection = m_coneAngleInspector->inspect() )
			{
				if( auto coneAngleData = runTimeCast<const FloatData>( coneInspection->value() ) )
				{
					coneAngle = coneAngleData->readable();
				}
			}

			std::optional<float> penumbraAngle = std::nullopt;

			if( Inspector::ResultPtr penumbraInspection = m_penumbraAngleInspector ? m_penumbraAngleInspector->inspect() : nullptr )
			{
				if( auto penumbraAngleData = runTimeCast<const FloatData>( penumbraInspection->value() ) )
				{
					penumbraAngle = penumbraAngleData->readable();
				}
			}

			return {coneAngle, penumbraAngle};
		}

		float handleAngle(const float coneAngle, const std::optional<float> penumbraAngle ) const
		{
			if( m_handleType == HandleType::Penumbra )
			{
				return ( !m_penumbraType || m_penumbraType == g_insetPenumbraType ) ? coneAngle * 0.5f - penumbraAngle.value() :
					m_penumbraType == g_outsetPenumbraType ? coneAngle * 0.5f + penumbraAngle.value() :
					penumbraAngle.value() * 0.5f
				;
			}

			return coneAngle * 0.5f;
		}

		// Given the native plug value in degrees, returns the angle the arc
		// for this handle covers, also in degrees.
		float angleToArcAngle( const float angle ) const
		{
			if( m_handleType == HandleType::Penumbra )
			{
				return ( !m_penumbraType || m_penumbraType == g_insetPenumbraType ) ? -angle :
					m_penumbraType == g_outsetPenumbraType ? angle :
					angle * 0.5f
				;
			}

			return angle * 0.5f;
		}

		MetadataValueParameterInspectorPtr m_coneAngleInspector;
		MetadataValueParameterInspectorPtr m_penumbraAngleInspector;

		struct ConePenumbraInspection
		{
			const Inspector::ResultPtr coneInspection;
			const float originalConeAngle;
			const Inspector::ResultPtr penumbraInspection;
			const float originalPenumbraAngle;
		};

		SceneViewPtr m_view;

		const float m_zRotation;

		std::vector<ConePenumbraInspection> m_inspections;

		std::optional<AngularDrag> m_drag;

		HandleType m_handleType;
		std::optional<InternedString> m_penumbraType;

		float m_visualiserScale;
		float m_frustumScale;
		float m_lensRadius;

		float m_dragStartAngle;
		float m_dragViewportStartLength2;
		float m_arcRadius;
};

class HandlesGadget : public Gadget
{

	public :

		HandlesGadget( const std::string &name="HandlesGadget" )
			:	Gadget( name )
		{
		}

	protected :

		Imath::Box3f renderBound() const override
		{
			// We need `renderLayer()` to be called any time it will
			// be called for one of our children. Our children claim
			// infinite bounds to account for their raster scale, so
			// we must too.
			Box3f b;
			b.makeInfinite();
			return b;
		}

		void renderLayer( Layer layer, const Style *style, RenderReason reason ) const override
		{
			if( layer != Layer::MidFront )
			{
				return;
			}

			// Clear the depth buffer so that the handles render
			// over the top of the SceneGadget. Otherwise they are
			// unusable when the object is larger than the handles.
			/// \todo Can we really justify this approach? Does it
			/// play well with new Gadgets we'll add over time? If
			/// so, then we should probably move the depth clearing
			/// to `Gadget::render()`, in between each layer. If
			/// not we'll need to come up with something else, perhaps
			/// going back to punching a hole in the depth buffer using
			/// `glDepthFunc( GL_GREATER )`. Or maybe an option to
			/// render gadgets in an offscreen buffer before compositing
			/// them over the current framebuffer?
			glClearDepth( 1.0f );
			glClear( GL_DEPTH_BUFFER_BIT );
			glEnable( GL_DEPTH_TEST );

		}

		unsigned layerMask() const override
		{
			return (unsigned)Layer::MidFront;
		}

};

}  // namespace

GAFFER_NODE_DEFINE_TYPE( LightTool );

LightTool::ToolDescription<LightTool, SceneView> LightTool::g_toolDescription;
size_t LightTool::g_firstPlugIndex = 0;

LightTool::LightTool( SceneView *view, const std::string &name ) :
	SelectionTool( view, name ),
	m_handles( new HandlesGadget() ),
	m_handleInspectionsDirty( true ),
	m_handleTransformsDirty( true ),
	m_selectionDirty( true ),
	m_priorityPathsDirty( true ),
	m_dragging( false ),
	m_scriptNode( nullptr ),
	m_mergeGroupId( 0 )
{
	view->viewportGadget()->addChild( m_handles );
	m_handles->setVisible( false );

	m_handles->addChild( new SpotLightHandle( "*light", "coneAngleParameter", SpotLightHandle::HandleType::Penumbra, view, 0, "westConeAngleParameter" ) );
	m_handles->addChild( new SpotLightHandle( "*light", "penumbraAngleParameter", SpotLightHandle::HandleType::Cone, view, 0, "westPenumbraAngleParameter" ) );
	m_handles->addChild( new SpotLightHandle( "*light", "coneAngleParameter", SpotLightHandle::HandleType::Penumbra, view, 90, "southConeAngleParameter" ) );
	m_handles->addChild( new SpotLightHandle( "*light", "penumbraAngleParameter", SpotLightHandle::HandleType::Cone, view, 90, "southPenumbraAngleParameter" ) );
	m_handles->addChild( new SpotLightHandle( "*light", "coneAngleParameter", SpotLightHandle::HandleType::Penumbra, view, 180, "eastConeAngleParameter" ) );
	m_handles->addChild( new SpotLightHandle( "*light", "penumbraAngleParameter", SpotLightHandle::HandleType::Cone, view, 180, "eastPenumbraAngleParameter" ) );		m_handles->addChild( new SpotLightHandle( "*light", "coneAngleParameter", SpotLightHandle::HandleType::Penumbra, view, 0, "coneAngleParameter" ) );
	m_handles->addChild( new SpotLightHandle( "*light", "coneAngleParameter", SpotLightHandle::HandleType::Penumbra, view, 270, "northConeAngleParameter" ) );
	m_handles->addChild( new SpotLightHandle( "*light", "penumbraAngleParameter", SpotLightHandle::HandleType::Cone, view, 270, "northPenumbraAngleParameter" ) );

	for( auto c : m_handles->children() )
	{
		auto handle = runTimeCast<Handle>( c );
		handle->setVisible( false );
		handle->dragBeginSignal().connectFront( boost::bind( &LightTool::dragBegin, this, ::_1 ) );
		handle->dragMoveSignal().connect( boost::bind( &LightTool::dragMove, this, ::_1, ::_2 ) );
		handle->dragEndSignal().connect( boost::bind( &LightTool::dragEnd, this, ::_1 ) );
	}

	storeIndexOfNextChild( g_firstPlugIndex );

	addChild( new ScenePlug( "__scene", Plug::In ) );

	scenePlug()->setInput( view->inPlug<ScenePlug>() );

	plugDirtiedSignal().connect( boost::bind( &LightTool::plugDirtied, this, ::_1 ) );
	view->plugDirtiedSignal().connect( boost::bind( &LightTool::plugDirtied, this, ::_1 ) );

	connectToViewContext();
	view->contextChangedSignal().connect( boost::bind( &LightTool::connectToViewContext, this ) );
}

LightTool::~LightTool()
{

}

const PathMatcher LightTool::selection() const
{
	updateSelection();
	return m_selection;
}

LightTool::SelectionChangedSignal &LightTool::selectionChangedSignal()
{
	return m_selectionChangedSignal;
}

ScenePlug *LightTool::scenePlug()
{
	return getChild<ScenePlug>( g_firstPlugIndex );
}

const ScenePlug *LightTool::scenePlug() const
{
	return getChild<ScenePlug>( g_firstPlugIndex );
}

void LightTool::connectToViewContext()
{
	m_contextChangedConnection = view()->getContext()->changedSignal().connect(
		boost::bind( &LightTool::contextChanged, this, ::_2 )
	);
}

void LightTool::contextChanged( const InternedString &name )
{
	if(
		ContextAlgo::affectsSelectedPaths( name ) ||
		ContextAlgo::affectsLastSelectedPath( name ) ||
		!boost::starts_with( name.string(), "ui:" )
	)
	{
		m_selectionDirty = true;
		m_handleInspectionsDirty = true;
		m_handleTransformsDirty = true;
		m_priorityPathsDirty = true;
		selectionChangedSignal()( *this );
	}
}

void LightTool::updateHandleInspections()
{
	auto scene = scenePlug()->getInput<ScenePlug>();
	scene = scene ? scene->getInput<ScenePlug>() : scene;
	if( !scene )
	{
		return;
	}

	m_inspectorsDirtiedConnection.clear();

	const PathMatcher selection = this->selection();
	if( selection.isEmpty() )
	{
		for( auto &c : m_handles->children() )
		{
			auto handle = runTimeCast<LightToolHandle>( c );
			handle->setVisible( false );
		}
		return;
	}

	ScenePlug::ScenePath lastSelectedPath = ContextAlgo::getLastSelectedPath( view()->getContext() );
	assert( selection.match( lastSelectedPath ) & PathMatcher::ExactMatch );

	ScenePlug::PathScope pathScope( view()->getContext() );

	for( auto &c : m_handles->children() )
	{
		auto handle = runTimeCast<LightToolHandle>( c );
		assert( handle );

		handle->update(
			new ScenePath( scene, view()->getContext(), lastSelectedPath ),
			view()->editScopePlug()
		);

		bool handleVisible = true;
		bool handleEnabled = true;

		for( PathMatcher::Iterator it = selection.begin(), eIt = selection.end(); it != eIt; ++it )
		{
			pathScope.setPath( &(*it) );

			handleVisible &= handle->visible();
			handleEnabled &= handle->enabled();
		}

		handle->setEnabled( handleEnabled );
		handle->setVisible( handleVisible );
	}
}

void LightTool::updateHandleTransforms( float rasterScale )
{
	auto scene = scenePlug()->getInput<ScenePlug>();
	scene = scene ? scene->getInput<ScenePlug>() : scene;
	if( !scene )
	{
		return;
	}

	const PathMatcher selection = this->selection();
	if( selection.isEmpty() )
	{
		return;
	}

	ScenePlug::ScenePath lastSelectedPath = ContextAlgo::getLastSelectedPath( view()->getContext() );
	assert( selection.match( lastSelectedPath ) & PathMatcher::Result::ExactMatch );
	if( !scene->exists( lastSelectedPath ) )
	{
		return;
	}

	m_handles->setTransform( scene->fullTransform( lastSelectedPath ) );

	for( auto &c : m_handles->children() )
	{
		auto handle = runTimeCast<LightToolHandle>( c );
		assert( handle );

		if( handle->getVisible() )
		{
			handle->updateTransform();
			handle->setRasterScale( rasterScale );
		}

	}
}

void LightTool::plugDirtied( const Plug *plug )
{

	// Note : This method is called not only when plugs
	// belonging to the TransformTool are dirtied, but
	// _also_ when plugs belonging to the View are dirtied.

	if(
		plug == activePlug() ||
		plug == scenePlug()->childNamesPlug() ||
		( plug->ancestor<View>() && plug == view()->editScopePlug() )
	)
	{
		m_selectionDirty = true;
		if( !m_dragging )
		{
			selectionChangedSignal()( *this );
		}
		m_handleInspectionsDirty = true;
		m_priorityPathsDirty = true;
	}

	if( plug == activePlug() )
	{
		if( activePlug()->getValue() )
		{
			m_preRenderConnection = view()->viewportGadget()->preRenderSignal().connect(
				boost::bind( &LightTool::preRender, this )
			);
		}
		else
		{
			m_preRenderConnection.disconnect();
			m_handles->setVisible( false );
		}
	}

	if( plug == scenePlug()->transformPlug() )
	{
		m_handleTransformsDirty = true;
	}

	/// \todo Checking for dirty attributes overlaps with the job of the inspector
	/// dirtied plug from `updateHandleInspections()`. Should we remove handling
	/// inspector dirtied signals? The `gl:visualiser:scale` attribute is used to
	/// place the handles, so we at least need to catch changes to that attribute.
	if( plug == scenePlug()->attributesPlug() )
	{
		m_handleInspectionsDirty = true;
		m_handleTransformsDirty = true;
	}
}

void LightTool::preRender()
{
	if( !m_dragging )
	{
		updateSelection();
		if( m_priorityPathsDirty )
		{
			m_priorityPathsDirty = false;
			SceneGadget *sceneGadget = static_cast<SceneGadget *>( view()->viewportGadget()->getPrimaryChild() );
			if( !selection().isEmpty() )
			{
				sceneGadget->setPriorityPaths( ContextAlgo::getSelectedPaths( view()->getContext() ) );
			}
			else
			{
				sceneGadget->setPriorityPaths( IECore::PathMatcher() );
			}
		}
	}

	if( m_handleInspectionsDirty )
	{
		updateHandleInspections();
		m_handleInspectionsDirty = false;

		for( auto &c : m_handles->children() )
		{
			auto handle = runTimeCast<LightToolHandle>( c );
			if( handle->getVisible() )
			{
				m_handles->setVisible( true );
				break;
			}
		}
	}

	if( m_handleTransformsDirty )
	{
		updateHandleTransforms( 75 );
		m_handleTransformsDirty = false;
	}
}

void LightTool::updateSelection() const
{
	if( !m_selectionDirty )
	{
		return;
	}

	if( m_dragging )
	{
		// In theory, an expression or some such could change the effective
		// transform plug while we're dragging (for instance, by driving the
		// enabled status of a downstream transform using the translate value
		// we're editing). But we ignore that on the grounds that it's unlikely,
		// and also that it would be very confusing for the selection to be
		// changed mid-drag.
		return;
	}

	m_selection.clear();
	m_selectionDirty = false;

	if( !activePlug()->getValue() )
	{
		return;
	}

	// If there's no input scene, then there's no need to
	// do anything. Our `scenePlug()` receives its input
	// from the View's input, but that doesn't count.
	auto scene = scenePlug()->getInput<ScenePlug>();
	scene = scene ? scene->getInput<ScenePlug>() : scene;
	if( !scene )
	{
		return;
	}

	m_selection = ContextAlgo::getSelectedPaths( view()->getContext() );
}

void LightTool::dirtyHandleTransforms()
{
	m_handleTransformsDirty = true;
}

RunTimeTypedPtr LightTool::dragBegin( Gadget *gadget )
{
	m_dragging = true;

	auto handle = runTimeCast<LightToolHandle>( gadget );
	assert( handle );
	const PathMatcher selection = this->selection();

	bool lookThroughLight = false;

	if( auto lookThroughEnabledPlug = view()->descendant<BoolPlug>( "camera.lookThroughEnabled") )
	{
		if( lookThroughEnabledPlug->getValue() )
		{
			std::string lookThroughCamera = view()->descendant<StringPlug>( "camera.lookThroughCamera" )->getValue();

			auto scene = scenePlug()->getInput<ScenePlug>();
			scene = scene ? scene->getInput<ScenePlug>() : scene;

			if( ConstPathMatcherDataPtr lightSetData = scene->set( "__lights" ) )
			{
				const PathMatcher &lightSet = lightSetData->readable();
				lookThroughLight = lightSet.match( lookThroughCamera ) == PathMatcher::Result::ExactMatch;
			}
		}
	}

	handle->setLookThroughLight( lookThroughLight );

	ScenePlug::PathScope pathScope( view()->getContext() );
	for( PathMatcher::Iterator it = selection.begin(), eIt = selection.end(); it != eIt; ++it )
	{
		pathScope.setPath( &(*it) );
		handle->addDragInspection();

		if( !m_scriptNode )
		{
			std::vector<Inspector *> inspectors = handle->inspectors();
			if( !inspectors.empty() )
			{
				Inspector::ResultPtr inspection = inspectors[0]->inspect();
				m_scriptNode = inspection->source()->ancestor<ScriptNode>();
			}
		}
	}

	return nullptr;
}

bool LightTool::dragMove( Gadget *gadget, const DragDropEvent &event )
{
	auto handle = runTimeCast<LightToolHandle>( gadget );
	assert( handle );

	UndoScope undoScope( m_scriptNode.get(), UndoScope::Enabled, undoMergeGroup() );

	handle->handleDragMove( event );

	return true;
}

bool LightTool::dragEnd( Gadget *gadget )
{
	m_dragging = false;
	m_mergeGroupId++;
	selectionChangedSignal()( *this );

	auto handle = runTimeCast<LightToolHandle>( gadget );
	handle->handleDragEnd();

	return false;
}

std::string LightTool::undoMergeGroup() const
{
	return fmt::format( "LightTool{}{}", fmt::ptr( this ), m_mergeGroupId );
}