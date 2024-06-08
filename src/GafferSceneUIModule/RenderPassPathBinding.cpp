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

#include "boost/python.hpp"

#include "RenderPassPathBinding.h"

#include "GafferScene/Filter.h"
#include "GafferScene/ScenePlug.h"

#include "GafferSceneUI/Private/RenderPassPath.h"

#include "GafferBindings/PathBinding.h"

#include "Gaffer/Context.h"
#include "Gaffer/PathFilter.h"

#include "boost/mpl/vector.hpp"

using namespace std;
using namespace boost::python;
using namespace IECore;
using namespace IECorePython;
using namespace Gaffer;
using namespace GafferBindings;
using namespace GafferScene;
using namespace GafferSceneUI;

namespace
{

struct PathGroupingFunctionWrapper
{
	PathGroupingFunctionWrapper( object fn )
		:	m_fn( fn )
	{
	}

	std::vector<InternedString> operator()( const std::string &renderPassName )
	{
		IECorePython::ScopedGILLock gilock;
		try
		{
			return extract<std::vector<InternedString>>( m_fn( renderPassName ) );
		}
		catch( const error_already_set & )
		{
			IECorePython::ExceptionAlgo::translatePythonException();
		}
	}

	private:

		object m_fn;
};

void registerPathGroupingFunctionWrapper( object f )
{
	RenderPassPath::registerPathGroupingFunction( PathGroupingFunctionWrapper( f ) );
}

string pathGroupingFunctionToString( const std::string &renderPassName )
{
	std::string result;
	ScenePlug::pathToString( RenderPassPath::pathGroupingFunction()( renderPassName ), result );
	return result;
}

object pathGroupingFunctionWrapper()
{
	return make_function(
		pathGroupingFunctionToString,
		default_call_policies(),
		boost::mpl::vector<string, const string &>()
	);
}

RenderPassPath::Ptr constructor1( ScenePlug &scene, Context &context, PathFilterPtr filter, const bool grouped )
{
	return new RenderPassPath( &scene, &context, filter, grouped );
}

RenderPassPath::Ptr constructor2( ScenePlug &scene, Context &context, const std::vector<IECore::InternedString> &names, const IECore::InternedString &root, PathFilterPtr filter, const bool grouped )
{
	return new RenderPassPath( &scene, &context, names, root, filter, grouped );
}

} // namespace

void GafferSceneUIModule::bindRenderPassPath()
{

	object module( borrowed( PyImport_AddModule( "GafferSceneUI.Private" ) ) );
	scope().attr( "RenderPassPath" ) = module;
	scope moduleScope( module );

	PathClass<RenderPassPath>()
		.def(
			"__init__",
			make_constructor(
				constructor1,
				default_call_policies(),
				(
					boost::python::arg( "scene" ),
					boost::python::arg( "context" ),
					boost::python::arg( "filter" ) = object(),
					boost::python::arg( "grouped" ) = false
				)
			)
		)
		.def(
			"__init__",
			make_constructor(
				constructor2,
				default_call_policies(),
				(
					boost::python::arg( "scene" ),
					boost::python::arg( "context" ),
					boost::python::arg( "names" ),
					boost::python::arg( "root" ) = "/",
					boost::python::arg( "filter" ) = object(),
					boost::python::arg( "grouped" ) = false
				)
			)
		)
		.def( "setScene", &RenderPassPath::setScene )
		.def( "getScene", (ScenePlug *(RenderPassPath::*)())&RenderPassPath::getScene, return_value_policy<CastToIntrusivePtr>() )
		.def( "setContext", &RenderPassPath::setContext )
		.def( "getContext", (Context *(RenderPassPath::*)())&RenderPassPath::getContext, return_value_policy<CastToIntrusivePtr>() )
		.def( "registerPathGroupingFunction", &registerPathGroupingFunctionWrapper )
		.staticmethod( "registerPathGroupingFunction" )
		.def( "pathGroupingFunction", &pathGroupingFunctionWrapper )
		.staticmethod( "pathGroupingFunction" )
	;

}
