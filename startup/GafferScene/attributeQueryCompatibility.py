##########################################################################
#
#  Copyright (c) 2026, Cinesite VFX Ltd. All rights reserved.
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

import IECore

import Gaffer
import GafferScene

# The AttributeQuery node used to only offer a single query that was typed via
# `setup()`, but we now support multiple queries added via `addQuery()`.
# Here we monkey patch the API so we can silently load scripts which were
# serialised in the old version, converting `setup()` to `addQuery()` and
# handling renamed and relocated plugs.

__legacyPlugPaths = {
	"attribute" : ( "queries", "name" ),
	"default" : ( "queries", "value" ),
	"exists" : ( "out", "exists" ),
	"value" : ( "out", "value" )
}

def __setup( self, plug ) :

	if len( self["queries"] ) :
		raise IECore.Exception( "AttributeQuery already has a query" )

	if not Gaffer.PlugAlgo.canSetValueFromData( plug ) and not isinstance( plug, Gaffer.ObjectPlug ) :
		raise IECore.Exception( "AttributeQuery cannot be setup from specified plug" )

	self.addQuery( plug )

def __getItem( originalGetItem ) :

	def getItem( self, key ) :

		legacyPath = __legacyPlugPaths.get( key ) if isinstance( key, str ) else None
		if legacyPath is None or key in self :
			return originalGetItem( self, key )

		if not len( self["queries"] ) :
			if key in ( "default", "value" ) :
				# In the old node these plugs wouldn't exist until `setup()`
				# was called. Delegate to getItem to raise the same errors
				# as the original node.
				return originalGetItem( self, key )

			if key in ( "exists", "attribute" ) :
				# These plugs were available on the old node even when
				# it hadn't been `setup()`. The new node creates equivalent
				# plugs as children of each query, so in order to access
				# them we must first add a query. The type of query created
				# isn't important, if the script is reliant on the `value`
				# plug, `setup()` would have been called before either of
				# these plugs are accessed and we would already have a query
				# of the correct type.
				self.addQuery( Gaffer.StringPlug() )

		parent, child = legacyPath
		return self[parent][0][child]

	return getItem

GafferScene.AttributeQuery.setup = __setup
GafferScene.AttributeQuery.__getitem__ = __getItem( GafferScene.AttributeQuery.__getitem__ )
