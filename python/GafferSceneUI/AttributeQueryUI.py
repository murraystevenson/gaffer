#########################################################################
#
#  Copyright (c) 2021, Cinesite VFX Ltd. All rights reserved.
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

import functools

import imath

import Gaffer
import GafferUI
import GafferScene

from GafferUI.PlugValueWidget import sole

##########################################################################
# Internal utilities
##########################################################################

def __getLabel( plug ) :

	n = plug.node()
	queryPlug = n.queryPlug( plug )
	prefix = queryPlug["name"].getValue() or "none"

	return prefix + "." + plug.relativeName( n.outPlugFromQuery( queryPlug ) )

##########################################################################
# Query widget
##########################################################################

class _QueryWidget( GafferUI.PlugValueWidget ) :

	def __init__( self, queryPlugs, **kw ) :

		self.__column = GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Vertical, spacing = 4 )

		if isinstance( queryPlugs, Gaffer.Plug ) :
			queryPlugs = { queryPlugs }

		GafferUI.PlugValueWidget.__init__( self, self.__column, queryPlugs )

		self.__plugValueWidgets = {}
		self.__plugWidgets = {}
		with self.__column :

			with GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Horizontal, spacing = 4 ) :

				GafferUI.Spacer( size = imath.V2i( 7, 1 ), maximumSize = imath.V2i( 7, 1 ) )

				self.__collapseButton = GafferUI.Button( image = "collapsibleArrowRight.png", hasFrame = False )
				self.__collapseButton.clickedSignal().connect( Gaffer.WeakMethod( self.__collapseButtonClicked ) )

				self.__plugValueWidgets["name"] = GafferUI.StringPlugValueWidget( { plug["name"] for plug in self.getPlugs() } )
				self.__plugValueWidgets["name"].textWidget()._qtWidget().setFixedWidth( GafferUI.PlugWidget.labelWidth() - 23 ) # Adjust for spacer and `collapseButton`
				self.__plugValueWidgets["defaultValue"] = GafferUI.PlugValueWidget.create( { plug["value"] for plug in self.getPlugs() } )

			with GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Vertical, spacing = 4 ) as self.__outputsColumn :

				outPlugs = [ plug.node().outPlugFromQuery( plug ) for plug in self.getPlugs() ]
				for childName in outPlugs[0].keys() :
					widget = GafferUI.PlugWidget( GafferUI.PlugValueWidget.create( { plug[childName] for plug in outPlugs } ) )
					self.__plugWidgets[childName] = widget
					self.__plugValueWidgets[childName] = widget.plugValueWidget()

			self.__setOutputsVisible( sole( Gaffer.Metadata.value( p, "ui:queryWidget:outputsVisible" ) for p in queryPlugs ) )

	def setPlugs( self, plugs ) :

		GafferUI.PlugValueWidget.setPlugs( self, plugs )

		self.__plugValueWidgets["name"].setPlugs( { plug["name"] for plug in self.getPlugs() } )
		self.__plugValueWidgets["defaultValue"].setPlugs( { plug["value"] for plug in self.getPlugs() } )

		outPlugs = [ plug.node().outPlugFromQuery( plug ) for plug in self.getPlugs() ]
		for childName in outPlugs[0].keys() :
			childPlugs = { plug[childName] for plug in outPlugs }
			self.__plugValueWidgets[childName].setPlugs( childPlugs )
			self.__plugWidgets[childName].labelPlugValueWidget().setPlugs( childPlugs )

	def hasLabel( self ) :

		return True

	def childPlugValueWidget( self, childPlug ) :

		for w in self.__plugValueWidgets.values() :
			if childPlug in w.getPlugs() :
				return w

		return None

	def __collapseButtonClicked( self, button ) :

		self.__setOutputsVisible( not self.__getOutputsVisible() )

	def __getOutputsVisible( self ) :

		return self.__outputsColumn.getVisible()

	def __setOutputsVisible( self, visible ) :

		self.__outputsColumn.setVisible( visible )
		self.__collapseButton.setImage( "collapsibleArrowDown.png" if visible else "collapsibleArrowRight.png" )

		for plug in self.getPlugs() :
			Gaffer.Metadata.registerValue( plug, "ui:queryWidget:outputsVisible", visible, persistent = False )

class _SourcePlugValueWidget( GafferUI.PlugValueWidget ) :

	def __init__( self, childPlug, **kw ) :

		self.__textWidget = GafferUI.TextWidget( editable = False )
		self.__textWidget._qtWidget().setFixedWidth( 60 )

		GafferUI.PlugValueWidget.__init__( self, self.__textWidget, childPlug )

	def hasLabel( self ) :

		return True

	def _updateFromValues( self, values, exception ) :

		value = sole( values )
		if value is None :
			self.__textWidget.setText( "---" )
		else :
			self.__textWidget.setText(
				GafferScene.AttributeQuery.Source.values[ value ].name if value > 0 else "None"
			)

		self.__textWidget.setErrored( exception is not None )

##########################################################################
# Metadata
##########################################################################

Gaffer.Metadata.registerNode(

	GafferScene.AttributeQuery,

	"description",
	"""
	Queries attributes from a scene location, creating outputs for each attribute.
	""",

	"layout:section:Settings.Queries:collapsed", False,

	plugs = {

		"scene" : {

			"description" :
			"""
			The scene to query the attributes from.
			"""

		},

		"location" : {

			"description" :
			"""
			The location within the scene to query the attributes at.
			> Note : If the location does not exist then the query will not be
			> performed and all outputs will be set to their default values with
			> each output `source` plug set to "None" (`0`).
			""",

			"plugValueWidget:type" : "GafferSceneUI.ScenePathPlugValueWidget",
			"scenePathPlugValueWidget:scene" : "scene",
			"nodule:type" : ""

		},

		"inherit" : {

			"description" :
			"""
			When on, each query includes attributes inherited from ancestor locations
			and the scene globals if a local attribute is not found.
			""",

			"nodule:type" : ""

		},

		"useMetadata" : {

			"description" :
			"""
			When on, returns "defaultValue" metadata registrations for missing attributes.
			""",

			"nodule:type" : "",

			"userDefault" : True,

		},

		"attributes" : {

			"description" :
			"""
			All attributes at the queried location output as a single `IECore.CompoundObject`.
			""",

			"nodule:type" : "",

		},

		"queries" : {

			"description" :
			"""
			The attributes to be queried - arbitrary numbers of attributes may be added
			as children of this plug via the user interface, or via python. Each
			child is a `NameValuePlug` whose `name` plug is the attribute to query,
			and whose `value` plug is the default value to use if the attribute can
			not be retrieved.
			""",

			"plugValueWidget:type" : "GafferUI.LayoutPlugValueWidget",

			"layout:section" : "Settings.Queries",
			"layout:customWidget:footer:widgetType" : "GafferSceneUI.AttributeQueryUI._AttributeQueryFooter",
			"layout:customWidget:footer:index" : -1,
			"layout:customWidget:addButton:index" : -1,
			"plugCreationWidget:action" : "addQuery",
			"ui:scene:acceptsAttributes" : True,
			"ui:scene:attributesLocationPlug" : "location",

			"nodule:type" : "",

		},

		"queries.*" : {

			"description" :
			"""
			A pair of attribute name to query and default value.
			""",

			"plugValueWidget:type" : "GafferSceneUI.AttributeQueryUI._QueryWidget",

		},

		"queries.*.name" : {

			"description" :
			"""
			The name of the attribute to query.
			""",

		},

		"queries.*.value" : {

			"description" :
			"""
			The value to output if the attribute does not exist.
			""",

		},

		"out" : {

			"description" :
			"""
			The parent plug of the query outputs. The order of outputs corresponds
			to the order of children of `queries`.
			""",

			"plugValueWidget:type" : "",

			"nodule:type" : "GafferUI::CompoundNodule",
			"noduleLayout:spacing" : 0.4,
			"noduleLayout:customGadget:addButton:gadgetType" : "",

		},

		"out.*" : {

			"description" :
			"""
			The result of the query.
			""",

			"nodule:type" : "GafferUI::CompoundNodule",

		},

		"out.*.source" : {

			"description" :
			"""
			Outputs the source of the value returned by the query.

			- None (`0`) : No source was found.
			- Local (`1`) : The location itself.
			- Inherited (`2`) : An ancestor of the location.
			- Globals (`3`) : An attribute in the scene globals.
			- Fallback (`4`) : The query did not find a result and fell back to returning the default value of the attribute.

			> Note : `Inherited` and `Globals` are only possible when `inherit` is on,
			> and `Fallback` only when `useMetadata` is on.
			""",

			"plugValueWidget:type" : "GafferSceneUI.AttributeQueryUI._SourcePlugValueWidget",

			"nodule:type" : "",

		},

		"out.*.exists" : {

			"description" :
			"""
			Outputs true if the attribute exists, otherwise false.
			""",

			"noduleLayout:label" : __getLabel,

		},

		"out.*.value" : {

			"description" :
			"""
			Outputs the value returned by the query.
			""",

		},

		"out.*.value..." : {

			"noduleLayout:label" : __getLabel,

		},

	}
)

##########################################################################
# _AttributeQueryFooter
##########################################################################

## \todo Maybe we can move the metadata signalling elsewhere and
# remove this widget?
class _AttributeQueryFooter( GafferUI.PlugCreationWidget ) :

	def __init__( self, queriesPlug, **kw ) :

		GafferUI.PlugCreationWidget.__init__( self, queriesPlug, **kw )

		queriesPlug.node().plugSetSignal().connect(
			Gaffer.WeakMethod( self.__updateQueryMetadata )
		)

	def __updateQueryMetadata( self, plug ) :

		node = plug.node()

		if node["queries"].isAncestorOf( plug ) :

			qPlug = plug.ancestor( Gaffer.NameValuePlug )

			if qPlug is not None and qPlug["name"] == plug :

				Gaffer.Metadata.plugValueChangedSignal( node )(
					node.outPlugFromQuery( qPlug ),
					"label",
					Gaffer.Metadata.ValueChangedReason.StaticRegistration
				)

##########################################################################
# Delete Plug
##########################################################################

def __plugPopupMenu( menuDefinition, plugValueWidget ) :

	plug = plugValueWidget.getPlug().ancestor( Gaffer.NameValuePlug )
	if plug is not None and isinstance( plug.node(), GafferScene.AttributeQuery ) and plug.node()["queries"].isAncestorOf( plug ) :

		if len( menuDefinition.items() ) :
			menuDefinition.append( "/DeleteDivider", { "divider" : True } )

		menuDefinition.append( "/Delete", { "command" : functools.partial( __deletePlug, plug ), "active" : not Gaffer.MetadataAlgo.readOnly( plug.node()["queries"] ) } )

def __deletePlug( plug ) :

	with Gaffer.UndoScope( plug.ancestor( Gaffer.ScriptNode ) ) :
		plug.node().removeQuery( plug )

GafferUI.PlugValueWidget.popupMenuSignal().connect( __plugPopupMenu )