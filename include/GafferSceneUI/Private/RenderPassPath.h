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

#pragma once

#include "GafferSceneUI/Export.h"
#include "GafferSceneUI/TypeIds.h"

#include "GafferScene/ScenePlug.h"

#include "Gaffer/Path.h"

#include "IECore/PathMatcher.h"

namespace GafferSceneUI
{

class GAFFERSCENEUI_API RenderPassPath : public Gaffer::Path
{

	public :

		explicit RenderPassPath( GafferScene::ScenePlugPtr scene, Gaffer::ContextPtr context, Gaffer::PathFilterPtr filter = nullptr, const bool grouped = false );
		RenderPassPath( GafferScene::ScenePlugPtr scene, Gaffer::ContextPtr context, const Names &names, const IECore::InternedString &root = "/", Gaffer::PathFilterPtr filter = nullptr, const bool grouped = false );

		IE_CORE_DECLARERUNTIMETYPEDEXTENSION( GafferSceneUI::RenderPassPath, RenderPassPathTypeId, Gaffer::Path );

		~RenderPassPath() override;

		void setScene( GafferScene::ScenePlugPtr scene );
		GafferScene::ScenePlug *getScene();
		const GafferScene::ScenePlug *getScene() const;

		void setContext( Gaffer::ContextPtr context );
		Gaffer::Context *getContext();
		const Gaffer::Context *getContext() const;

		bool isValid( const IECore::Canceller *canceller = nullptr ) const override;
		bool isLeaf( const IECore::Canceller *canceller = nullptr ) const override;
		Gaffer::PathPtr copy() const override;

		void propertyNames( std::vector<IECore::InternedString> &names, const IECore::Canceller *canceller = nullptr ) const override;
		IECore::ConstRunTimeTypedPtr property( const IECore::InternedString &name, const IECore::Canceller *canceller = nullptr ) const override;

		const Gaffer::Plug *cancellationSubject() const override;

		using PathGroupingFunction = std::function<std::vector<IECore::InternedString> ( const std::string &renderPassName )>;
		static PathGroupingFunction &pathGroupingFunction();
		static void registerPathGroupingFunction( PathGroupingFunction f );

	protected :

		void doChildren( std::vector<Gaffer::PathPtr> &children, const IECore::Canceller *canceller ) const override;

	private :

		const IECore::PathMatcher pathMatcher( const IECore::Canceller *canceller ) const;
		void contextChanged( const IECore::InternedString &key );
		void plugDirtied( Gaffer::Plug *plug );

		Gaffer::NodePtr m_node;
		GafferScene::ScenePlugPtr m_scene;
		Gaffer::ContextPtr m_context;
		Gaffer::Signals::ScopedConnection m_plugDirtiedConnection;
		Gaffer::Signals::ScopedConnection m_contextChangedConnection;
		bool m_grouped;

};

IE_CORE_DECLAREPTR( RenderPassPath )

} // namespace GafferSceneUI
