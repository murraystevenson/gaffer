##########################################################################
#
#  Copyright (c) 2022, Cinesite VFX Ltd. All rights reserved.
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

import imath
import six
import functools
import collections

import IECore

import Gaffer
import GafferUI
import GafferScene
import GafferSceneUI

Gaffer.Metadata.registerNode(

	GafferScene.AttributeTweaks,

	"description",
	"""
	Makes modifications to attributes.
	""",

	plugs = {

		"localise" : [

			"description",
			"""
			Turn on to allow location-specific tweaks to be made to inherited
			attributes. Attributes will be localised to locations matching the
			node's filter prior to tweaking. The original inherited attributes
			will remain untouched.
			"""

		],

		"ignoreMissing" : [

			"description",
			"""
			Ignores tweaks targeting missing attributes. When off, missing attributes
			cause the node to error.
			"""

		],

		"tweaks" : [

			"description",
			"""
			The tweaks to be made to the attributes. Arbitrary numbers of user defined
			tweaks may be added as children of this plug via the user interface, or
			using the AttributeTweaks API via python.
			""",

			"plugValueWidget:type", "GafferUI.LayoutPlugValueWidget",
			"layout:customWidget:footer:widgetType", "GafferSceneUI.AttributeTweaksUI._TweaksFooter",
			"layout:customWidget:footer:index", -1,

			"nodule:type", "",

		],

		"tweaks.*" : [

			"tweakPlugValueWidget:allowCreate", True,

		],

	}
)

##########################################################################
# Internal utilities
##########################################################################

def _attributeTweaksNode( plugValueWidget ) :

	# The plug may not belong to an AttributeTweaks node
	# directly. Instead it may have been promoted
	# elsewhere and be driving a target plug on an
	# AttributeTweaks node.

	def walkOutputs( plug ) :

		if isinstance( plug.node(), GafferScene.AttributeTweaks ) :
			return plug.node()

		for output in plug.outputs() :
			node = walkOutputs( output )
			if node is not None :
				return node

	return walkOutputs( plugValueWidget.getPlug() )

def _pathsFromAffected( plugValueWidget ) :

	node = _attributeTweaksNode( plugValueWidget )
	if node is None :
		return []

	pathMatcher = IECore.PathMatcher()
	with plugValueWidget.getContext() :
		GafferScene.SceneAlgo.matchingPaths( node["filter"], node["in"], pathMatcher )

	return pathMatcher.paths()

def _pathsFromSelection( plugValueWidget ) :

	node = _attributeTweaksNode( plugValueWidget )
	if node is None :
		return []

	paths = GafferSceneUI.ContextAlgo.getSelectedPaths( plugValueWidget.getContext() )
	paths = paths.paths() if paths else []

	with plugValueWidget.getContext() :
		paths = [ p for p in paths if node["in"].exists( p ) ]

	return paths


##########################################################################
# _TweaksFooter
##########################################################################

class _TweaksFooter( GafferUI.PlugValueWidget ) :

	def __init__( self, plug ) :

		row = GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Horizontal )

		GafferUI.PlugValueWidget.__init__( self, row, plug )

		with row :

				GafferUI.Spacer( imath.V2i( GafferUI.PlugWidget.labelWidth(), 1 ) )

				GafferUI.MenuButton(
					image = "plus.png",
					hasFrame = False,
					menu = GafferUI.Menu( Gaffer.WeakMethod( self.__menuDefinition ) )
				)

				GafferUI.Spacer( imath.V2i( 1 ), imath.V2i( 999999, 1 ), parenting = { "expand" : True } )

	def _updateFromPlug( self ) :

		self.setEnabled( self._editable() )

	def __menuDefinition( self ) :

		result = IECore.MenuDefinition()

		result.append(
			"/From Affected",
			{
				"subMenu" : Gaffer.WeakMethod( self.__addFromAffectedMenuDefinition )
			}
		)

		result.append(
			"/From Selection",
			{
				"subMenu" : Gaffer.WeakMethod( self.__addFromSelectedMenuDefinition )
			}
		)

		result.append( "/FromPathsDivider", { "divider" : True } )

		# TODO - would be nice to share these default options with other users of TweakPlug
		for item in [
			Gaffer.BoolPlug,
			Gaffer.FloatPlug,
			Gaffer.IntPlug,
			"NumericDivider",
			Gaffer.StringPlug,
			"StringDivider",
			Gaffer.V2iPlug,
			Gaffer.V3iPlug,
			Gaffer.V2fPlug,
			Gaffer.V3fPlug,
			"VectorDivider",
			Gaffer.Color3fPlug,
			Gaffer.Color4fPlug
		] :

			if isinstance( item, six.string_types ) :
				result.append( "/" + item, { "divider" : True } )
			else :
				result.append(
					"/" + item.__name__.replace( "Plug", "" ),
					{
						"command" : functools.partial( Gaffer.WeakMethod( self.__addTweak ), "", item ),
					}
				)

		return result

	def __addFromAffectedMenuDefinition( self ) :

		return self.__addFromPathsMenuDefinition( _pathsFromAffected( self ) )

	def __addFromSelectedMenuDefinition( self ) :

		return self.__addFromPathsMenuDefinition( _pathsFromSelection( self ) )

	def __addFromPathsMenuDefinition( self, paths ) :

		result = IECore.MenuDefinition()

		node = _attributeTweaksNode( self )
		attributes = {}

		if node is not None :
			with self.getContext() :
				useFullAttr = node["localise"].getValue()
				for path in paths :
					attr = node["in"].fullAttributes( path ) if useFullAttr else node["in"].attributes( path )
					attributes.update( attr )

		attributes = collections.OrderedDict( sorted( attributes.items() ) )

		for key, value in [ ( k, v ) for k, v in attributes.items() if k.replace( ':', '_' ) not in node["tweaks"] ] :
			result.append(
				"/" + key,
				{
					"command" : functools.partial(
						Gaffer.WeakMethod( self.__addTweak ),
						key,
						value
					)
				}
			)

		if not len( result.items() ) :
			result.append(
				"/No Attributes Found", { "active" : False }
			)
			return result

		return result

	def __addTweak( self, name, plugTypeOrValue ) :

		if isinstance( plugTypeOrValue, IECore.Data ) :
			plug = Gaffer.TweakPlug( name, plugTypeOrValue )
		else :
			plug = Gaffer.TweakPlug( name, plugTypeOrValue() )

		if name :
			plug.setName( name.replace( ':', '_' ) )

		with Gaffer.UndoScope( self.getPlug().ancestor( Gaffer.ScriptNode ) ) :
			self.getPlug().addChild( plug )