##########################################################################
#
#  Copyright (c) 2025, Cinesite VFX Ltd. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import os
import sys
import functools

import IECore
import Gaffer
import GafferScene

# Register function to load renderer on demand. This allows us to find the renderer
# even if the relevant Python module hasn't been imported (in `gaffer execute` for instance).

def __creator( renderType, fileName, messageHandler, renderer, module ) :

	# Import module to replace ourselves with the true renderer creation function.
	__import__( module )
	# And then call `create()` again to use it.
	return GafferScene.Private.IECoreScenePreview.Renderer.create( renderer, renderType, fileName, messageHandler )

if "RMANTREE" in os.environ and IECore.SearchPath( sys.path ).find( "IECoreRenderMan" ) :

	if "RenderMan" not in GafferScene.Private.IECoreScenePreview.Renderer.types() :
		# Register creator that will load the IECoreRenderMan module to provide RenderMan on demand.
		GafferScene.Private.IECoreScenePreview.Renderer.registerType(
			"RenderMan", functools.partial( __creator, renderer = "RenderMan", module = "IECoreRenderMan" )
		)

	Gaffer.Metadata.registerValue( "renderer:RenderMan", "enabled", os.environ.get( "GAFFERRENDERMAN_HIDE_UI", "" ) != "1" )

Gaffer.Metadata.registerValues( {

	"renderer:RenderMan" : {

		"optionPrefix" : "ri",
		"attributePrefix" : "ri",

	},

} )
