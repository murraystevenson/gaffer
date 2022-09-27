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
#      * Neither the name of Cinesite VFX Ltd. nor the names of
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

import GafferTest
import GafferScene

class ExpansionTest( GafferTest.TestCase ) :

	def testSetExpandedPaths( self ) :

		e = GafferScene.Expansion()

		p = IECore.PathMatcher( [ "/a", "/b", "/a/b", "/b/c" ] )
		e.setExpandedPaths( p )
		self.assertEqual( e.getExpandedPaths(), p )

	def testClearExpansion( self ) :

		e = GafferScene.Expansion()

		p = IECore.PathMatcher( [ "/a", "/b", "/a/b", "/b/c" ] )
		e.setExpandedPaths( p )
		self.assertEqual( e.getExpandedPaths(), p )

		e.clearExpansion()
		self.assertEqual( e.getExpandedPaths(), IECore.PathMatcher() )

	def testExpand( self ) :

		e = GafferScene.Expansion()

		p = IECore.PathMatcher( [ "/a", "/b", "/a/b", "/b/c" ] )
		e.setExpandedPaths( p )
		self.assertEqual( e.getExpandedPaths(), p )

		p2 = IECore.PathMatcher( [ "/a/b/c", "/c", "/d", "/d/e" ] )
		e.expand( p2, expandAncestors = False )
		r = IECore.PathMatcher( p )
		r.addPaths( p2 )
		self.assertEqual( e.getExpandedPaths(), r )

		p3 = IECore.PathMatcher( [ "/f/g" ] )
		e.expand( p3, expandAncestors = True )
		r.addPaths( IECore.PathMatcher( ["/", "/f", "/f/g" ] ) )
		self.assertEqual( e.getExpandedPaths(), r )

	def testLock( self ) :

		e = GafferScene.Expansion()

		l = IECore.PathMatcher( [ "/b" ] )
		e.lock( l )
		self.assertEqual( e.getLockedPaths(), l )

	def testUnlock( self ) :

		e = GafferScene.Expansion()

		e.lock( IECore.PathMatcher( [ "/a", "/b" ] ) )
		e.unlock( IECore.PathMatcher( [ "/b" ] ) )
		self.assertEqual( e.getLockedPaths(), IECore.PathMatcher( [ "/a" ] ) )

	def testClearLocking( self ) :

		e = GafferScene.Expansion()

		l = IECore.PathMatcher( [ "/a", "/b" ] )
		e.lock( l )
		self.assertEqual( e.getLockedPaths(), l )

		e.clearLocking()
		self.assertEqual( e.getLockedPaths(), IECore.PathMatcher() )

	def testPin( self ) :

		e = GafferScene.Expansion()

		p = IECore.PathMatcher( [ "/a", "/b" ] )
		e.pin( p )
		self.assertEqual( e.getPinnedPaths(), p )

	def testUnpin( self ) :

		e = GafferScene.Expansion()

		e.pin( IECore.PathMatcher( [ "/a", "/b" ] ) )
		e.unpin( IECore.PathMatcher( [ "/b" ] ) )
		self.assertEqual( e.getPinnedPaths(), IECore.PathMatcher( [ "/a" ] ) )

	def testClearPinning( self ) :

		e = GafferScene.Expansion()

		p = IECore.PathMatcher( [ "/a", "/b" ] )
		e.pin( p )
		self.assertEqual( e.getPinnedPaths(), p )

		e.clearPinning()
		self.assertEqual( e.getPinnedPaths(), IECore.PathMatcher() )

	def testLockedPathsAreNotExpanded( self ) :

		e = GafferScene.Expansion()

		p = IECore.PathMatcher( [ "/a", "/b", "/a/b", "/b/c" ] )
		e.setExpandedPaths( p )
		e.lock( IECore.PathMatcher( [ "/b" ] ) )
		self.assertEqual( e.getExpandedPaths(), IECore.PathMatcher( [ "/a", "/a/b" ] ) )

	def testUnlockedPathsAreExpanded( self ) :
		
		e = GafferScene.Expansion()

		p = IECore.PathMatcher( [ "/a", "/b", "/a/b", "/b/c" ] )
		e.setExpandedPaths( p )
		self.assertEqual( e.getExpandedPaths(), p )

		# locking both "/a" and "/b" will result in their descendants also not being expanded
		e.lock( IECore.PathMatcher( [ "/a", "/b" ] ) )
		self.assertEqual( e.getExpandedPaths(), IECore.PathMatcher() )

		# unlocking "/b" will result in it and its descendants being expanded
		e.unlock( IECore.PathMatcher( [ "/b" ] ) )
		self.assertEqual( e.getExpandedPaths(), IECore.PathMatcher( [ "/b", "/b/c" ] ) )

		# clearing all locks will result in the original expansion
		e.clearLocking()
		self.assertEqual( e.getExpandedPaths(), p )

	def testPinnedPathsAreExpanded( self ) :

		e = GafferScene.Expansion()

		e.setExpandedPaths( IECore.PathMatcher( [ "/a", "/a/b" ] ) )
		e.pin( IECore.PathMatcher( [ "/b" ] ) )

		self.assertEqual( e.getExpandedPaths(), IECore.PathMatcher( [ "/a", "/a/b", "/b" ] ) )

	def testUnpinnedPathsAreNoLongerExpanded( self ) :
		
		e = GafferScene.Expansion()

		e.pin( IECore.PathMatcher( [ "/a", "/b/c" ] ) )
		self.assertEqual( e.getExpandedPaths(), IECore.PathMatcher( [ "/a", "/b/c" ] ) )

		e.unpin( IECore.PathMatcher( [ "/b/c" ] ) )
		self.assertEqual( e.getExpandedPaths(), IECore.PathMatcher( [ "/a" ] ) )

		e.clearPinning()
		self.assertEqual( e.getExpandedPaths(), IECore.PathMatcher() )

	def testShouldExpand( self ) :

		e = GafferScene.Expansion()

		e.setExpandedPaths( IECore.PathMatcher( [ "/a", "/b", "/a/b", "/b/c" ] ) )
		self.assertTrue( e.shouldExpand( "/a" ) )
		self.assertTrue( e.shouldExpand( "/b" ) )
		self.assertTrue( e.shouldExpand( "/a/b" ) )
		self.assertTrue( e.shouldExpand( "/b/c" ) )
		self.assertFalse( e.shouldExpand( "/c" ) )

		# Locking "/b" should only affect "/b" and its descendants
		e.lock( IECore.PathMatcher( [ "/b" ] ) )
		self.assertTrue( e.shouldExpand( "/a" ) )
		self.assertTrue( e.shouldExpand( "/a/b" ) )
		self.assertFalse( e.shouldExpand( "/b" ) )
		self.assertFalse( e.shouldExpand( "/b/c" ) )

		# Pinning "/b/c" should not result in it being expanded as "/b" is still locked
		e.pin( IECore.PathMatcher( [ "/b/c" ] ) )
		self.assertTrue( e.shouldExpand( "/a" ) )
		self.assertTrue( e.shouldExpand( "/a/b" ) )
		self.assertFalse( e.shouldExpand( "/b" ) )
		self.assertFalse( e.shouldExpand( "/b/c" ) )

		# Unlocking "/b" should make both "/b" and "/b/c" expandable
		e.unlock( IECore.PathMatcher( [ "/b" ] ) )
		self.assertTrue( e.shouldExpand( "/a" ) )
		self.assertTrue( e.shouldExpand( "/a/b" ) )
		self.assertTrue( e.shouldExpand( "/b" ) )
		self.assertTrue( e.shouldExpand( "/b/c" ) )
		self.assertTrue( e.shouldExpand( "/b/c/d" ) )

		# Unpinning "/b/c" should leave it expanded as it was originally set expanded
		# "/b/c/d" will no longer be expanded as it was inheriting expansion from the pin at "/b/c"
		e.unpin( IECore.PathMatcher( [ "/b/c" ] ) )
		self.assertTrue( e.shouldExpand( "/a" ) )
		self.assertTrue( e.shouldExpand( "/a/b" ) )
		self.assertTrue( e.shouldExpand( "/b" ) )
		self.assertTrue( e.shouldExpand( "/b/c" ) )
		self.assertFalse( e.shouldExpand( "/b/c/d" ) )

		# Expanding only "/a" and "/a/b" should leave "/b" and its descendants collapsed
		e.setExpandedPaths( IECore.PathMatcher( [ "/a", "/a/b" ] ) )
		self.assertTrue( e.shouldExpand( "/a" ) )
		self.assertTrue( e.shouldExpand( "/a/b" ) )
		self.assertFalse( e.shouldExpand( "/b" ) )
		self.assertFalse( e.shouldExpand( "/b/c" ) )
		self.assertFalse( e.shouldExpand( "/b/c/d" ) )

		# Pinning "/b/c" should leave "/b" collapsed while expanding "/b/c" and its descendants
		e.pin( IECore.PathMatcher( [ "/b/c" ] ) )
		self.assertTrue( e.shouldExpand( "/a" ) )
		self.assertTrue( e.shouldExpand( "/a/b" ) )
		self.assertFalse( e.shouldExpand( "/b" ) )
		self.assertTrue( e.shouldExpand( "/b/c" ) )
		self.assertTrue( e.shouldExpand( "/b/c/d" ) )
		
	def testHasExpandedDescendants( self ) :

		e = GafferScene.Expansion()

		e.setExpandedPaths( IECore.PathMatcher( [ "/a", "/b", "/a/b", "/a/b/c", "/b/c", "/b/c/d" ] ) )
		self.assertTrue( e.hasExpandedDescendants( "/" ) )
		self.assertTrue( e.hasExpandedDescendants( "/a" ) )
		self.assertTrue( e.hasExpandedDescendants( "/b" ) )
		self.assertTrue( e.hasExpandedDescendants( "/a/b" ) )
		self.assertTrue( e.hasExpandedDescendants( "/b/c" ) )
		self.assertFalse( e.hasExpandedDescendants( "/a/b/c" ) )
		self.assertFalse( e.hasExpandedDescendants( "/b/c/d" ) )
		self.assertFalse( e.hasExpandedDescendants( "/c" ) )

		# Locking "/b" should only affect it and its descendants
		e.lock( IECore.PathMatcher( [ "/b" ] ) )
		self.assertTrue( e.hasExpandedDescendants( "/" ) )
		self.assertTrue( e.hasExpandedDescendants( "/a" ) )
		self.assertFalse( e.hasExpandedDescendants( "/b" ) )
		self.assertFalse( e.hasExpandedDescendants( "/b/c" ) )

		# Pinning "/b/c" should not result in it being expanded as "/b" is locked
		e.pin( IECore.PathMatcher( [ "/b/c" ] ) )
		self.assertFalse( e.hasExpandedDescendants( "/b" ) )
		self.assertFalse( e.hasExpandedDescendants( "/b/c" ) )

		# Unlocking "/b" should make pinned "/b/c" expanded
		e.unlock( IECore.PathMatcher( [ "/b" ] ) )
		self.assertTrue( e.hasExpandedDescendants( "/b" ) )
		self.assertTrue( e.hasExpandedDescendants( "/b/c" ) )

		# Unpinning "/b/c" should leave it expanded as it was originally set expanded
		e.unpin( IECore.PathMatcher( [ "/b/c" ] ) )
		self.assertTrue( e.hasExpandedDescendants( "/b" ) )
		self.assertTrue( e.hasExpandedDescendants( "/b/c" ) )

if __name__ == "__main__":
	unittest.main()
