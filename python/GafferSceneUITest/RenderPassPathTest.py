##########################################################################
#
#  Copyright (c) 2024, Cinesite VFX Ltd. All rights reserved.
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

import unittest

import IECore

import Gaffer
import GafferScene
import GafferSceneUI
import GafferUITest

class RenderPassPathTest( GafferUITest.TestCase ) :

	def testSimpleChildren( self ) :

		renderPasses = GafferScene.RenderPasses()
		renderPasses["names"].setValue( IECore.StringVectorData( ["A", "B", "C", "D"] ) )

		context = Gaffer.Context()
		path = GafferSceneUI.Private.RenderPassPath( renderPasses["out"], context, "/" )
		self.assertTrue( path.isValid() )
		self.assertFalse( path.isLeaf() )

		children = path.children()
		self.assertEqual( [ str( c ) for c in children ], [ "/A", "/B", "/C", "/D" ] )
		for child in children :
			self.assertIsInstance( child, GafferSceneUI.Private.RenderPassPath )
			self.assertTrue( child.getContext().isSame( context ) )
			self.assertTrue( child.getScene().isSame( renderPasses["out"] ) )
			self.assertTrue( child.isLeaf() )
			self.assertTrue( child.isValid() )
			self.assertEqual( child.children(), [] )

	def testPathIsValid( self ) :

		renderPasses = GafferScene.RenderPasses()
		renderPasses["names"].setValue( IECore.StringVectorData( ["A", "B", "C", "D"] ) )

		path = GafferSceneUI.Private.RenderPassPath( renderPasses["out"], Gaffer.Context(), "/" )
		self.assertTrue( path.isValid() )
		self.assertFalse( path.isLeaf() )

		for parent, valid in [
			( "/", True ),
			( "/A", True ),
			( "/A/B", False ),
			( "/B", True ),
			( "/C", True ),
			( "/D", True ),
			( "/E", False ),
			( "/E/F", False ),
		] :

			path.setFromString( parent )
			self.assertEqual( path.isValid(), valid )

	def testPathIsLeaf( self ) :

		renderPasses = GafferScene.RenderPasses()
		renderPasses["names"].setValue( IECore.StringVectorData( ["A", "B", "C", "D"] ) )

		path = GafferSceneUI.Private.RenderPassPath( renderPasses["out"], Gaffer.Context(), "/" )
		self.assertTrue( path.isValid() )
		self.assertFalse( path.isLeaf() )

		for parent, leaf in [
			( "/", False ),
			( "/A", True ),
			( "/A/B", False ),
			( "/B", True ),
			( "/C", True ),
			( "/D", True ),
			( "/E", False ),
			( "/E/F", False ),
		] :

			path.setFromString( parent )
			self.assertEqual( path.isLeaf(), leaf )

	def testPathCancellation( self ) :

		plane = GafferScene.Plane()
		path = GafferSceneUI.Private.RenderPassPath( plane["out"], Gaffer.Context(), "/" )

		canceller = IECore.Canceller()
		canceller.cancel()

		with self.assertRaises( IECore.Cancelled ) :
			path.children( canceller )

		with self.assertRaises( IECore.Cancelled ) :
			path.isValid( canceller )

		with self.assertRaises( IECore.Cancelled ) :
			path.isLeaf( canceller )

		with self.assertRaises( IECore.Cancelled ) :
			path.property( "renderPassPath:enabled", canceller )

if __name__ == "__main__":
	unittest.main()
