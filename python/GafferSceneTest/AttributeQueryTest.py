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

import pathlib
import random
import imath

import IECore
import Gaffer
import GafferTest
import GafferScene
import GafferSceneTest

def randomName( gen, mnc, mxc ) :

	from string import ascii_lowercase

	return ''.join( gen.choice( ascii_lowercase )
		for _ in range( gen.randrange( mnc, mxc ) ) )

def addAttr( parent, name, data ) :

	parent.addChild( Gaffer.NameValuePlug( name, data, True, name, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

def addAttrs( parent ) :

	addAttr( parent, "b", IECore.BoolData() )
	addAttr( parent, "f", IECore.FloatData() )
	addAttr( parent, "i", IECore.IntData() )
	addAttr( parent, "bv", IECore.BoolVectorData() )
	addAttr( parent, "fv", IECore.FloatVectorData() )
	addAttr( parent, "iv", IECore.IntVectorData() )
	addAttr( parent, "s", IECore.StringData() )
	addAttr( parent, "sv", IECore.StringVectorData() )
	addAttr( parent, "isv", IECore.InternedStringVectorData() )
	addAttr( parent, "c4f", IECore.Color4fData() )
	addAttr( parent, "c3f", IECore.Color3fData() )
	addAttr( parent, "v3f", IECore.V3fData() )
	addAttr( parent, "v2f", IECore.V2fData() )
	addAttr( parent, "v3i", IECore.V3iData() )
	addAttr( parent, "v2i", IECore.V2iData() )
	addAttr( parent, "b3f", IECore.Box3fData() )
	addAttr( parent, "b2f", IECore.Box2fData() )
	addAttr( parent, "b3i", IECore.Box3iData() )
	addAttr( parent, "b2i", IECore.Box2iData() )
	addAttr( parent, "o", IECore.M44fData() )

def addUserPlugs( parent, direction = Gaffer.Plug.Direction.In ) :

	parent["user"].addChild( Gaffer.BoolPlug( "b", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.FloatPlug( "f", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.IntPlug( "i", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.BoolVectorDataPlug( "bv", direction = direction, defaultValue = IECore.BoolVectorData(), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.FloatVectorDataPlug( "fv", direction = direction, defaultValue = IECore.FloatVectorData(), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.IntVectorDataPlug( "iv", direction = direction, defaultValue = IECore.IntVectorData(), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.StringPlug( "s", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.StringVectorDataPlug( "sv", direction = direction, defaultValue = IECore.StringVectorData(), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.InternedStringVectorDataPlug( "isv", direction = direction, defaultValue = IECore.InternedStringVectorData(), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.Color3fPlug( "c3f", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.Color4fPlug( "c4f", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.V3fPlug( "v3f", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.V3iPlug( "v3i", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.V2fPlug( "v2f", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.V2iPlug( "v2i", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.Box3fPlug( "b3f", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.Box3iPlug( "b3i", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.Box2fPlug( "b2f", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.Box2iPlug( "b2i", direction = direction, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
	parent["user"].addChild( Gaffer.ObjectPlug( "o", direction = direction, defaultValue = IECore.NullObject(), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

class AttributeQueryTest( GafferSceneTest.SceneTestCase ) :

	def testDefault( self ) :

		q = GafferScene.AttributeQuery()

		self.assertEqual( q["location"].getValue(), "" )
		self.assertFalse( q["inherit"].getValue() )
		self.assertFalse( q["useMetadata"].getValue() )
		self.assertEqual( len( q["queries"] ), 0 )
		self.assertEqual( len( q["out"] ), 0 )
		self.assertEqual( q["attributes"].getValue(), IECore.CompoundObject() )

	def testOutput( self ) :

		q = GafferScene.AttributeQuery()

		n1 = q.addQuery( Gaffer.IntPlug() )
		n2 = q.addQuery( Gaffer.Color3fPlug() )
		n3 = q.addQuery( Gaffer.Box2iPlug() )
		badPlug = Gaffer.NameValuePlug( "missing", Gaffer.Color3fPlug(), "badPlug" )

		self.assertEqual( q.outPlugFromQuery( n1 ), q["out"][0] )
		self.assertEqual( q.outPlugFromQuery( n2 ), q["out"][1] )
		self.assertEqual( q.outPlugFromQuery( n3 ), q["out"][2] )

		self.assertEqual( q.existsPlugFromQuery( n1 ), q["out"][0]["exists"] )
		self.assertEqual( q.existsPlugFromQuery( n2 ), q["out"][1]["exists"] )
		self.assertEqual( q.existsPlugFromQuery( n3 ), q["out"][2]["exists"] )

		self.assertEqual( q.valuePlugFromQuery( n1 ), q["out"][0]["value"] )
		self.assertEqual( q.valuePlugFromQuery( n2 ), q["out"][1]["value"] )
		self.assertEqual( q.valuePlugFromQuery( n3 ), q["out"][2]["value"] )

		self.assertEqual( q.queryPlug( q["out"][0]["value"] ), n1 )
		self.assertEqual( q.queryPlug( q["out"][1]["value"] ), n2 )
		self.assertEqual( q.queryPlug( q["out"][1]["value"]["r"] ), n2 )
		self.assertEqual( q.queryPlug( q["out"][2]["value"] ), n3 )
		self.assertEqual( q.queryPlug( q["out"][2]["value"]["min"] ), n3 )
		self.assertEqual( q.queryPlug( q["out"][2]["value"]["min"]["x"] ), n3 )
		self.assertRaises( IECore.Exception, q.queryPlug, badPlug )

	def testAddRemoveQuery( self ) :

		def assertChildren( query, children ) :

			self.assertEqual( len( query["queries"].children() ), len( children ) )
			self.assertEqual( len( query["out"].children() ), len( children ) )

			for i, ( name, plugType ) in enumerate( children ) :
				self.assertEqual( query["queries"][i]["name"].getValue(), name )
				self.assertIsInstance( query["queries"][i]["value"], plugType )
				self.assertIsInstance( query["out"][i]["exists"], Gaffer.BoolPlug )
				self.assertIsInstance( query["out"][i]["source"], Gaffer.IntPlug )
				self.assertIsInstance( query["out"][i]["value"], plugType )

		query = GafferScene.AttributeQuery()
		assertChildren( query, [] )

		a = query.addQuery( Gaffer.IntPlug(), "a" )
		assertChildren( query, [ ( "a", Gaffer.IntPlug ) ] )

		b = query.addQuery( Gaffer.Color3fPlug( "c3f" ), "b" )
		assertChildren( query, [ ( "a", Gaffer.IntPlug ), ( "b", Gaffer.Color3fPlug ) ] )

		c = query.addQuery( Gaffer.Box2iPlug( "b2i", Gaffer.Plug.Direction.Out, imath.Box2i( imath.V2i( 1 ), imath.V2i( 2 ) ) ), "c" )
		assertChildren( query, [ ( "a", Gaffer.IntPlug ), ( "b", Gaffer.Color3fPlug ), ( "c", Gaffer.Box2iPlug ) ] )

		query.removeQuery( b )
		assertChildren( query, [ ( "a", Gaffer.IntPlug ), ( "c", Gaffer.Box2iPlug ) ] )

		query.removeQuery( c )
		assertChildren( query, [ ( "a", Gaffer.IntPlug ) ] )

		query.removeQuery( a )
		assertChildren( query, [] )

	def testNoScene( self ) :

		r = random.Random()

		loc = randomName( r, 5, 10 )
		name = randomName( r, 5, 10 )

		q = GafferScene.AttributeQuery()

		q["location"].setValue( "" )
		q.addQuery( Gaffer.StringPlug() )
		q["inherit"].setValue( True )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["queries"][0]["name"].setValue( name )
		q["inherit"].setValue( False )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["inherit"].setValue( True )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["location"].setValue( loc )
		q["queries"][0]["name"].setValue( "" )
		q["inherit"].setValue( False )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["inherit"].setValue( True )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["queries"][0]["name"].setValue( name )
		q["inherit"].setValue( False )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["inherit"].setValue( True )
		self.assertFalse( q["out"][0]["exists"].getValue() )

	def testSceneNoAttr( self ) :

		r = random.Random()

		loc = randomName( r, 5, 10 )
		name = randomName( r, 5, 10 )

		s = GafferScene.Sphere()
		s["name"].setValue( loc )
		a = GafferScene.CustomAttributes()
		a["in"].setInput( s["out"] )
		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )

		q["location"].setValue( "" )
		q.addQuery( Gaffer.StringPlug() )
		q["inherit"].setValue( True )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["queries"][0]["name"].setValue( name )
		q["inherit"].setValue( False )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["inherit"].setValue( True )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["location"].setValue( loc )
		q["queries"][0]["name"].setValue( "" )
		q["inherit"].setValue( False )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["inherit"].setValue( True )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["queries"][0]["name"].setValue( name )
		q["inherit"].setValue( False )
		self.assertFalse( q["out"][0]["exists"].getValue() )

		q["inherit"].setValue( True )
		self.assertFalse( q["out"][0]["exists"].getValue() )

	def testExists( self ) :

		r = random.Random()
		loc = randomName( r, 5, 10 )

		s = GafferScene.Sphere()
		s["name"].setValue( loc )
		a = GafferScene.CustomAttributes()
		a["in"].setInput( s["out"] )
		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )

		addAttrs( a["attributes"] )

		q["location"].setValue( "" )
		q["inherit"].setValue( False )

		names = [
			"", "b", "f", "i", "bv", "fv", "iv", "s", "is", "sv", "isv",
			"c4f", "c3f", "v3f", "v2f", "v3i", "v2i", "b3f", "b2f", "b3i", "b2i"
		]

		for i, name in enumerate( names ) :
			with self.subTest( name = name ) :
				q.addQuery( Gaffer.StringPlug(), name )
				self.assertFalse( q["out"][i]["exists"].getValue() )

		q["location"].setValue( loc )

		for i, name in enumerate( names ) :
			with self.subTest( name = name ) :
				self.assertEqual( name not in ( "", "is" ), q["out"][i]["exists"].getValue() )

	def testValues( self ) :

		r = random.Random()
		loc = randomName( r, 5, 10 )

		s = GafferScene.Sphere()
		s["name"].setValue( loc )
		a = GafferScene.CustomAttributes()
		a["in"].setInput( s["out"] )
		addAttrs( a["attributes"] )

		a["attributes"]["b"]["value"].setValue( bool( r.randint( 0, 1 ) ) )
		a["attributes"]["f"]["value"].setValue( r.uniform( -100.0, 100.0 ) )
		a["attributes"]["i"]["value"].setValue( r.randint( -100, 100 ) )
		a["attributes"]["bv"]["value"].setValue( IECore.BoolVectorData( [ bool( r.randint( 0, 1 ) ) for _ in range( 10 ) ] ) )
		a["attributes"]["fv"]["value"].setValue( IECore.FloatVectorData( [ r.uniform( -100.0, 100.0 ) for _ in range( 10 ) ] ) )
		a["attributes"]["iv"]["value"].setValue( IECore.IntVectorData( [ r.randint( -100, 100 ) for _ in range( 10 ) ] ) )
		a["attributes"]["s"]["value"].setValue( randomName( r, 4, 5 ) )
		a["attributes"]["sv"]["value"].setValue( IECore.StringVectorData( [ randomName( r, 4, 5 ) for _ in range( 10 ) ] ) )
		a["attributes"]["isv"]["value"].setValue( IECore.InternedStringVectorData( [ IECore.InternedString( randomName( r, 4, 5 ) ) for _ in range( 10 ) ] ) )
		a["attributes"]["c4f"]["value"].setValue( imath.Color4f( r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ) ) )
		a["attributes"]["c3f"]["value"].setValue( imath.Color3f( r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ) ) )
		a["attributes"]["v3f"]["value"].setValue( imath.V3f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ) )
		a["attributes"]["v2f"]["value"].setValue( imath.V2f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ) )
		a["attributes"]["v3i"]["value"].setValue( imath.V3i( r.randint( -100, 100 ), r.randint( -100, 100 ), r.randint( -100, 100 ) ) )
		a["attributes"]["v2i"]["value"].setValue( imath.V2i( r.randint( -100, 100 ), r.randint( -100, 100 ) ) )
		a["attributes"]["b3f"]["value"].setValue( imath.Box3f(
			imath.V3f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ),
			imath.V3f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ) ) )
		a["attributes"]["b2f"]["value"].setValue( imath.Box2f(
			imath.V2f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ),
			imath.V2f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ) ) )
		a["attributes"]["b3i"]["value"].setValue( imath.Box3i(
			imath.V3i( r.randint( -100, 100 ), r.randint( -100, 100 ), r.randint( -100, 100 ) ),
			imath.V3i( r.randint( -100, 100 ), r.randint( -100, 100 ), r.randint( -100, 100 ) ) ) )
		a["attributes"]["b2i"]["value"].setValue( imath.Box2i(
			imath.V2i( r.randint( -100, 100 ), r.randint( -100, 100 ) ),
			imath.V2i( r.randint( -100, 100 ), r.randint( -100, 100 ) ) ) )

		n = Gaffer.Node()
		addUserPlugs( n )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["b"] )
		q["queries"][0]["value"].setValue( bool( r.randint( 0, 1 ) ) )
		self.assertEqual( q["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue( "b" )
		self.assertEqual( q["value"].getValue(), a["attributes"]["b"]["value"].getValue() )
		q["queries"][0]["name"].setValue( "f" )
		self.assertEqual( q["value"].getValue(), bool( a["attributes"]["f"]["value"].getValue() ) )
		q["queries"][0]["name"].setValue( "i" )
		self.assertEqual( q["value"].getValue(), bool( a["attributes"]["i"]["value"].getValue() ) )
		q["queries"][0]["name"].setValue( "o" )
		self.assertEqual( q["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["f"] )
		q["queries"][0]["value"].setValue( r.uniform( -100.0, 100.0 ) )
		self.assertEqual( q["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue( "b" )
		self.assertEqual( q["value"].getValue(), float( a["attributes"]["b"]["value"].getValue() ) )
		q["queries"][0]["name"].setValue( "f" )
		self.assertEqual( q["value"].getValue(), a["attributes"]["f"]["value"].getValue() )
		q["queries"][0]["name"].setValue( "i" )
		self.assertEqual( q["value"].getValue(), int( a["attributes"]["i"]["value"].getValue() ) )
		q["queries"][0]["name"].setValue( "o" )
		self.assertEqual( q["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["i"] )
		q["queries"][0]["value"].setValue( r.randint( -100, 100 ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("b")
		self.assertEqual( q["out"][0]["value"].getValue(), int( a["attributes"]["b"]["value"].getValue() ) )
		q["queries"][0]["name"].setValue("f")
		self.assertEqual( q["out"][0]["value"].getValue(), int( a["attributes"]["f"]["value"].getValue() ) )
		q["queries"][0]["name"].setValue("i")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["i"]["value"].getValue() )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["bv"] )
		q["queries"][0]["value"].setValue( IECore.BoolVectorData( [ bool( r.randint( 0, 1 ) ) for _ in range( 10 ) ] ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("bv")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["bv"]["value"].getValue() )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["fv"] )
		q["queries"][0]["value"].setValue( IECore.FloatVectorData( [ r.uniform( -100.0, 100.0 ) for _ in range( 10 ) ] ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("fv")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["fv"]["value"].getValue() )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["iv"] )
		q["queries"][0]["value"].setValue( IECore.IntVectorData( [ r.randint( -100, 100 ) for _ in range( 10 ) ] ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("iv")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["iv"]["value"].getValue() )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["s"] )
		q["queries"][0]["value"].setValue( randomName( r, 4, 5 ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("s")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["s"]["value"].getValue() )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["sv"] )
		q["queries"][0]["value"].setValue( IECore.StringVectorData( [ randomName( r, 4, 5 ) for _ in range( 10 ) ] ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("sv")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["sv"]["value"].getValue() )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["isv"] )
		q["queries"][0]["value"].setValue( IECore.InternedStringVectorData( [ IECore.InternedString( randomName( r, 4, 5 ) ) for _ in range( 10 ) ] ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("isv")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["isv"]["value"].getValue() )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["c4f"] )
		q["queries"][0]["value"].setValue( imath.Color4f( r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ) ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("c4f")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["c4f"]["value"].getValue() )
		q["queries"][0]["name"].setValue("c3f")
		v = a["attributes"]["c3f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Color4f( v.x, v.y, v.z, 1.0 ) )
		q["queries"][0]["name"].setValue("v3f")
		v = a["attributes"]["v3f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Color4f( v.x, v.y, v.z, 1.0 ) )
		q["queries"][0]["name"].setValue("v2f")
		v = a["attributes"]["v2f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Color4f( v.x, v.y, 0.0, 1.0 ) )
		q["queries"][0]["name"].setValue("f")
		v = a["attributes"]["f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Color4f( v, v, v, 1.0 ) )
		q["queries"][0]["name"].setValue("i")
		v = float( a["attributes"]["i"]["value"].getValue() )
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Color4f( v, v, v, 1.0 ) )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["c3f"] )
		q["queries"][0]["value"].setValue( imath.Color3f( r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ) ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("c4f")
		v = a["attributes"]["c4f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Color3f( v.r, v.g, v.b ) )
		q["queries"][0]["name"].setValue("c3f")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["c3f"]["value"].getValue() )
		q["queries"][0]["name"].setValue("v3f")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["v3f"]["value"].getValue() )
		q["queries"][0]["name"].setValue("v2f")
		v = a["attributes"]["v2f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Color3f( v.x, v.y, 0.0 ) )
		q["queries"][0]["name"].setValue("f")
		v = a["attributes"]["f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Color3f( v, v, v ) )
		q["queries"][0]["name"].setValue("i")
		v = float( a["attributes"]["i"]["value"].getValue() )
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Color3f( v, v, v ) )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["v3f"] )
		q["queries"][0]["value"].setValue( imath.V3f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("c3f")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["c3f"]["value"].getValue() )
		q["queries"][0]["name"].setValue("v3f")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["v3f"]["value"].getValue() )
		q["queries"][0]["name"].setValue("v3i")
		v = a["attributes"]["v3i"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V3f( float( v.x ), float( v.y ), float( v.z ) ) )
		q["queries"][0]["name"].setValue("v2f")
		v = a["attributes"]["v2f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V3f( v.x, v.y, 0.0 ) )
		q["queries"][0]["name"].setValue("v2i")
		v = a["attributes"]["v2i"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V3f( float( v.x ), float( v.y ), 0.0 ) )
		q["queries"][0]["name"].setValue("f")
		v = a["attributes"]["f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V3f( v, v, v ) )
		q["queries"][0]["name"].setValue("i")
		v = float( a["attributes"]["i"]["value"].getValue() )
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V3f( v, v, v ) )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["v2f"] )
		q["queries"][0]["value"].setValue( imath.V2f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("v2f")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["v2f"]["value"].getValue() )
		q["queries"][0]["name"].setValue("v2i")
		v = a["attributes"]["v2i"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V2f( float( v.x ), float( v.y ) ) )
		q["queries"][0]["name"].setValue("f")
		v = a["attributes"]["f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V2f( v, v ) )
		q["queries"][0]["name"].setValue("i")
		v = float( a["attributes"]["i"]["value"].getValue() )
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V2f( v, v ) )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["v3i"] )
		q["queries"][0]["value"].setValue( imath.V3i( r.randint( -100, 100 ), r.randint( -100, 100 ), r.randint( -100, 100 ) ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("v3f")
		v = a["attributes"]["v3f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V3i( int( v.x ), int( v.y ), int( v.z ) ) )
		q["queries"][0]["name"].setValue("v2f")
		v = a["attributes"]["v2f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V3i( int( v.x ), int( v.y ), 0 ) )
		q["queries"][0]["name"].setValue("v3i")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["v3i"]["value"].getValue() )
		q["queries"][0]["name"].setValue("v2i")
		v = a["attributes"]["v2i"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V3i( v.x, v.y, 0 ) )
		q["queries"][0]["name"].setValue("f")
		v = int( a["attributes"]["f"]["value"].getValue() )
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V3i( v, v, v ) )
		q["queries"][0]["name"].setValue("i")
		v = a["attributes"]["i"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V3i( v, v, v ) )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["v2i"] )
		q["queries"][0]["value"].setValue( imath.V2i( r.randint( -100, 100 ), r.randint( -100, 100 ) ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("v2f")
		v = a["attributes"]["v2f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V2i( int( v.x ), int( v.y ) ) )
		q["queries"][0]["name"].setValue("v2i")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["v2i"]["value"].getValue() )
		q["queries"][0]["name"].setValue("f")
		v = int( a["attributes"]["f"]["value"].getValue() )
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V2i( v, v ) )
		q["queries"][0]["name"].setValue("i")
		v = a["attributes"]["i"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.V2i( v, v ) )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["b3f"] )
		q["queries"][0]["value"].setValue( imath.Box3f(
			imath.V3f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ),
			imath.V3f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ) ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("b3f")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["b3f"]["value"].getValue() )
		q["queries"][0]["name"].setValue("b3i")
		v = a["attributes"]["b3i"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Box3f(
			imath.V3f( float( v.min().x ), float( v.min().y ), float( v.min().z ) ),
			imath.V3f( float( v.max().x ), float( v.max().y ), float( v.max().z ) ) ) )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["b2f"] )
		q["queries"][0]["value"].setValue( imath.Box2f(
			imath.V2f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ),
			imath.V2f( r.uniform( -100.0, 100.0 ), r.uniform( -100.0, 100.0 ) ) ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("b2f")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["b2f"]["value"].getValue() )
		q["queries"][0]["name"].setValue("b2i")
		v = a["attributes"]["b2i"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Box2f(
			imath.V2f( float( v.min().x ), float( v.min().y ) ),
			imath.V2f( float( v.max().x ), float( v.max().y ) ) ) )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["b3i"] )
		q["queries"][0]["value"].setValue( imath.Box3i(
			imath.V3i( r.randint( -100, 100 ), r.randint( -100, 100 ), r.randint( -100, 100 ) ),
			imath.V3i( r.randint( -100, 100 ), r.randint( -100, 100 ), r.randint( -100, 100 ) ) ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("b3f")
		v = a["attributes"]["b3f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Box3i(
			imath.V3i( int( v.min().x ), int( v.min().y ), int( v.min().z ) ),
			imath.V3i( int( v.max().x ), int( v.max().y ), int( v.max().z ) ) ) )
		q["queries"][0]["name"].setValue("b3i")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["b3i"]["value"].getValue() )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["b2i"] )
		q["queries"][0]["value"].setValue( imath.Box2i(
			imath.V2i( r.randint( -100, 100 ), r.randint( -100, 100 ) ),
			imath.V2i( r.randint( -100, 100 ), r.randint( -100, 100 ) ) ) )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("b2f")
		v = a["attributes"]["b2f"]["value"].getValue()
		self.assertEqual( q["out"][0]["value"].getValue(), imath.Box2i(
			imath.V2i( int( v.min().x ), int( v.min().y ) ),
			imath.V2i( int( v.max().x ), int( v.max().y ) ) ) )
		q["queries"][0]["name"].setValue("b2i")
		self.assertEqual( q["out"][0]["value"].getValue(), a["attributes"]["b2i"]["value"].getValue() )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["o"] )
		q["queries"][0]["value"].setValue( { randomName( r, 4, 5 ) : IECore.NullObject() } )
		self.assertEqual( q["out"][0]["value"].getValue(), q["queries"][0]["value"].getValue() )
		q["queries"][0]["name"].setValue("o")
		self.assertEqual( q["out"][0]["value"].getValue().value, a["attributes"]["o"]["value"].getValue() )

	def testMultipleQueries( self ) :

		sphere = GafferScene.Sphere()

		attributes = GafferScene.CustomAttributes()
		attributes["in"].setInput( sphere["out"] )
		attributes["extraAttributes"].setValue(
			IECore.CompoundObject( {
				"i" : IECore.IntData( 2 ),
				"s" : IECore.StringData( "two" ),
			} )
		)

		sphereFilter = GafferScene.PathFilter()
		sphereFilter["paths"].setValue( IECore.StringVectorData( [ "/sphere" ] ) )
		attributes["filter"].setInput( sphereFilter["out"] )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( attributes["out"] )
		q["location"].setValue( "/sphere" )

		q.addQuery( Gaffer.IntPlug( defaultValue = 1 ), "i" )
		q.addQuery( Gaffer.StringPlug( defaultValue = "one" ), "s" )
		q.addQuery( Gaffer.IntPlug( defaultValue = 3 ), "missing" )

		self.assertTrue( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["value"].getValue(), 2 )
		self.assertTrue( q["out"][1]["exists"].getValue() )
		self.assertEqual( q["out"][1]["value"].getValue(), "two" )
		self.assertFalse( q["out"][2]["exists"].getValue() )
		self.assertEqual( q["out"][2]["value"].getValue(), 3 )

		q["queries"][0]["name"].setValue( "missing" )
		self.assertFalse( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["value"].getValue(), 1 )
		self.assertTrue( q["out"][1]["exists"].getValue() )
		self.assertEqual( q["out"][1]["value"].getValue(), "two" )
		self.assertFalse( q["out"][2]["exists"].getValue() )
		self.assertEqual( q["out"][2]["value"].getValue(), 3 )

		q["queries"][2]["name"].setValue( "i" )
		self.assertFalse( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["value"].getValue(), 1 )
		self.assertTrue( q["out"][1]["exists"].getValue() )
		self.assertEqual( q["out"][1]["value"].getValue(), "two" )
		self.assertTrue( q["out"][2]["exists"].getValue() )
		self.assertEqual( q["out"][2]["value"].getValue(), 2 )

	def testSource( self ) :

		Source = GafferScene.AttributeQuery.Source

		group = GafferScene.Group()

		sphere = GafferScene.Sphere()
		group["in"][0].setInput( sphere["out"] )

		sphereFilter = GafferScene.PathFilter()
		sphereFilter["paths"].setValue( IECore.StringVectorData( [ "/group/sphere" ] ) )

		groupFilter = GafferScene.PathFilter()
		groupFilter["paths"].setValue( IECore.StringVectorData( [ "/group" ] ) )

		globalAttributes = GafferScene.CustomAttributes()
		globalAttributes["in"].setInput( group["out"] )
		globalAttributes["global"].setValue( True )
		globalAttributes["extraAttributes"].setValue( IECore.CompoundObject( { "test" : IECore.StringData( "global" ) } ) )

		groupAttributes = GafferScene.CustomAttributes()
		groupAttributes["in"].setInput( globalAttributes["out"] )
		groupAttributes["filter"].setInput( groupFilter["out"] )
		groupAttributes["extraAttributes"].setValue( IECore.CompoundObject( { "test" : IECore.StringData( "inherited" ) } ) )
		groupAttributes["enabled"].setValue( False )

		sphereAttributes = GafferScene.CustomAttributes()
		sphereAttributes["in"].setInput( groupAttributes["out"] )
		sphereAttributes["filter"].setInput( sphereFilter["out"] )
		sphereAttributes["extraAttributes"].setValue( IECore.CompoundObject( { "test" : IECore.StringData( "local" ) } ) )
		sphereAttributes["enabled"].setValue( False )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( sphereAttributes["out"] )
		q["location"].setValue( "/group/sphere" )
		q.addQuery( Gaffer.StringPlug( defaultValue = "none" ), "test" )

		self.assertFalse( q["inherit"].getValue() )
		self.assertFalse( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.None_ )
		self.assertEqual( q["out"][0]["value"].getValue(), "none" )

		q["inherit"].setValue( True )
		self.assertTrue( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.Globals )
		self.assertEqual( q["out"][0]["value"].getValue(), "global" )

		groupAttributes["enabled"].setValue( True )
		self.assertTrue( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.Inherited )
		self.assertEqual( q["out"][0]["value"].getValue(), "inherited" )

		sphereAttributes["enabled"].setValue( True )
		self.assertTrue( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.Local )
		self.assertEqual( q["out"][0]["value"].getValue(), "local" )

		q["inherit"].setValue( False )
		self.assertTrue( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.Local )
		self.assertEqual( q["out"][0]["value"].getValue(), "local" )

		q["location"].setValue( "/group/missing" )
		self.assertFalse( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.None_ )
		self.assertEqual( q["out"][0]["value"].getValue(), "none" )

	def testSerialisation( self ) :

		r = random.Random()
		loc = randomName( r, 5, 10 )

		c = GafferScene.Sphere()
		c["name"].setValue( loc )
		a = GafferScene.CustomAttributes()
		a["in"].setInput( c["out"] )
		addAttrs( a["attributes"] )

		a["attributes"]["b"]["value"].setValue( bool( r.randint( 0, 1 ) ) )
		a["attributes"]["f"]["value"].setValue( r.uniform( -100.0, 100.0 ) )
		a["attributes"]["i"]["value"].setValue( r.randint( -100, 100 ) )
		a["attributes"]["bv"]["value"].setValue( IECore.BoolVectorData( [ bool( r.randint( 0, 1 ) ) for _ in range( 10 ) ] ) )
		a["attributes"]["fv"]["value"].setValue( IECore.FloatVectorData( [ r.uniform( -10.0, 10.0 ) for _ in range( 10 ) ] ) )
		a["attributes"]["iv"]["value"].setValue( IECore.IntVectorData( [ r.randint( -100, 100 ) for _ in range( 10 ) ] ) )
		a["attributes"]["s"]["value"].setValue( randomName( r, 4, 5 ) )
		a["attributes"]["sv"]["value"].setValue( IECore.StringVectorData( [ randomName( r, 4, 5 ) for _ in range( 10 ) ] ) )
		a["attributes"]["isv"]["value"].setValue( IECore.InternedStringVectorData( [ IECore.InternedString( randomName( r, 4, 5 ) ) for _ in range( 10 ) ] ) )
		a["attributes"]["c4f"]["value"].setValue( imath.Color4f( r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ) ) )
		a["attributes"]["c3f"]["value"].setValue( imath.Color3f( r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ), r.uniform( 0.0, 1.0 ) ) )
		a["attributes"]["v3f"]["value"].setValue( imath.V3f( r.uniform( -10.0, 10.0 ), r.uniform( -10.0, 10.0 ), r.uniform( -10.0, 10.0 ) ) )
		a["attributes"]["v2f"]["value"].setValue( imath.V2f( r.uniform( -10.0, 10.0 ), r.uniform( -10.0, 10.0 ) ) )
		a["attributes"]["v3i"]["value"].setValue( imath.V3i( r.randint( -100, 100 ), r.randint( -100, 100 ), r.randint( -100, 100 ) ) )
		a["attributes"]["v2i"]["value"].setValue( imath.V2i( r.randint( -100, 100 ), r.randint( -100, 100 ) ) )
		a["attributes"]["b3f"]["value"].setValue( imath.Box3f(
			imath.V3f( r.uniform( -10.0, 0.0 ), r.uniform( -10.0, 0.0 ), r.uniform( -10.0, 0.0 ) ),
			imath.V3f( r.uniform( 0.0, 10.0 ), r.uniform( 0.0, 10.0 ), r.uniform( 0.0, 10.0 ) ) ) )
		a["attributes"]["b2f"]["value"].setValue( imath.Box2f(
			imath.V2f( r.uniform( -10.0, 0.0 ), r.uniform( -10.0, 0.0 ) ),
			imath.V2f( r.uniform( 0.0, 10.0 ), r.uniform( 0.0, 10.0 ) ) ) )
		a["attributes"]["b3i"]["value"].setValue( imath.Box3i(
			imath.V3i( r.randint( -10, 0 ), r.randint( -10, 0 ), r.randint( -10, 0 ) ),
			imath.V3i( r.randint( 0, 10 ), r.randint( 0, 10 ), r.randint( 0, 10 ) ) ) )
		a["attributes"]["b2i"]["value"].setValue( imath.Box2i(
			imath.V2i( r.randint( -10, 0 ), r.randint( -10, 0 ) ),
			imath.V2i( r.randint( 0, 10 ), r.randint( 0, 10 ) ) ) )

		n = Gaffer.Node()
		addUserPlugs( n )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["b"] )
		q["queries"][0]["name"].setValue("b")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["b"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["f"] )
		q["queries"][0]["name"].setValue("f")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertAlmostEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["f"]["value"].getValue(), places=4 )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["i"] )
		q["queries"][0]["name"].setValue("i")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["i"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["bv"] )
		q["queries"][0]["name"].setValue("bv")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["bv"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["fv"] )
		q["queries"][0]["name"].setValue("fv")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		for i in range( 10 ) :
			self.assertAlmostEqual( s["n"]["out"][0]["value"].getValue()[ i ], a["attributes"]["fv"]["value"].getValue()[ i ], places=4 )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["iv"] )
		q["queries"][0]["name"].setValue("iv")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["iv"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["s"] )
		q["queries"][0]["name"].setValue("s")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["s"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["sv"] )
		q["queries"][0]["name"].setValue("sv")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["sv"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["isv"] )
		q["queries"][0]["name"].setValue("isv")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["isv"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["c4f"] )
		q["queries"][0]["name"].setValue("c4f")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		for i in range( 4 ) :
			self.assertAlmostEqual( s["n"]["out"][0]["value"].getValue()[ i ], a["attributes"]["c4f"]["value"].getValue()[ i ], places=4 )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["c3f"] )
		q["queries"][0]["name"].setValue("c3f")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		for i in range( 3 ) :
			self.assertAlmostEqual( s["n"]["out"][0]["value"].getValue()[ i ], a["attributes"]["c3f"]["value"].getValue()[ i ], places=4 )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["v3f"] )
		q["queries"][0]["name"].setValue("v3f")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		for i in range( 3 ) :
			self.assertAlmostEqual( s["n"]["out"][0]["value"].getValue()[ i ], a["attributes"]["v3f"]["value"].getValue()[ i ], places=4 )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["v2f"] )
		q["queries"][0]["name"].setValue("v2f")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		for i in range( 2 ) :
			self.assertAlmostEqual( s["n"]["out"][0]["value"].getValue()[ i ], a["attributes"]["v2f"]["value"].getValue()[ i ], places=4 )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["v3i"] )
		q["queries"][0]["name"].setValue("v3i")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["v3i"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["v2i"] )
		q["queries"][0]["name"].setValue("v2i")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["v2i"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["b3f"] )
		q["queries"][0]["name"].setValue("b3f")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		for j in range( 3 ) :
			self.assertAlmostEqual( s["n"]["out"][0]["value"].getValue().min()[ j ], a["attributes"]["b3f"]["value"].getValue().min()[ j ], places=4 )
			self.assertAlmostEqual( s["n"]["out"][0]["value"].getValue().max()[ j ], a["attributes"]["b3f"]["value"].getValue().max()[ j ], places=4 )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["b2f"] )
		q["queries"][0]["name"].setValue("b2f")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		for j in range( 2 ) :
			self.assertAlmostEqual( s["n"]["out"][0]["value"].getValue().min()[ j ], a["attributes"]["b2f"]["value"].getValue().min()[ j ], places=4 )
			self.assertAlmostEqual( s["n"]["out"][0]["value"].getValue().max()[ j ], a["attributes"]["b2f"]["value"].getValue().max()[ j ], places=4 )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["b3i"] )
		q["queries"][0]["name"].setValue("b3i")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["b3i"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["b2i"] )
		q["queries"][0]["name"].setValue("b2i")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue(), a["attributes"]["b2i"]["value"].getValue() )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( a["out"] )
		q["location"].setValue( loc )
		q.addQuery( n["user"]["o"] )
		q["queries"][0]["name"].setValue("o")
		s = Gaffer.ScriptNode()
		s["n"] = q
		s["a"] = a
		s["c"] = c
		ss = s.serialise()
		s = Gaffer.ScriptNode()
		s.execute( ss )
		self.assertTrue( s["n"]["out"][0]["exists"].getValue() )
		self.assertEqual( s["n"]["out"][0]["value"].getValue().value, a["attributes"]["o"]["value"].getValue() )

	def testShaderOutput( self ) :

		loc = "shaderSphere"

		v = GafferSceneTest.TestShader( "assignedShader" )
		v.loadShader( "simpleShader" )
		v["type"].setValue( "test:shader" )

		d = Gaffer.ObjectPlug(
			"o",
			direction = Gaffer.Plug.Direction.Out,
			defaultValue = IECore.NullObject()
		)

		s = GafferScene.Sphere()
		s["name"].setValue( loc )

		sa = GafferScene.ShaderAssignment()
		sa["in"].setInput( s["out"] )
		sa["shader"].setInput( v["out"] )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( sa["out"] )
		q.addQuery( d )
		q["queries"][0]["name"].setValue( "test:shader" )

		self.assertEqual( q["out"][0]["value"].getValue(), d.getValue() )

		q["location"].setValue( loc )

		self.assertEqual( q["out"][0]["value"].getValue(), v.attributes()["test:shader"] )

	def testQueryDoubleData( self ) :

		sphere = GafferScene.Sphere()

		attributes = GafferScene.CustomAttributes()
		attributes["in"].setInput( sphere["out"] )
		attributes["extraAttributes"].setValue( IECore.CompoundObject( { "test" : IECore.DoubleData( 2.5 ) } ) )

		query = GafferScene.AttributeQuery()
		query.addQuery( Gaffer.FloatPlug() )
		query["scene"].setInput( attributes["out"] )
		query["location"].setValue( "/sphere" )
		query["queries"][0]["name"].setValue( "test" )

		self.assertTrue( query["out"][0]["exists"].getValue() )
		self.assertEqual( query["out"][0]["value"].getValue(), 2.5 )

	def testInheritedGlobalAttribute( self ) :

		sphere = GafferScene.Sphere()

		globalAttributes = GafferScene.CustomAttributes()
		globalAttributes["in"].setInput( sphere["out"] )
		globalAttributes["global"].setValue( True )
		globalAttributes["extraAttributes"].setValue( IECore.CompoundObject( { "test" : IECore.DoubleData( 5.0 ) } ) )

		attributes = GafferScene.CustomAttributes()
		attributes["in"].setInput( globalAttributes["out"] )
		attributes["extraAttributes"].setValue( IECore.CompoundObject( { "test" : IECore.DoubleData( 2.5 ) } ) )
		attributes["enabled"].setValue( False )

		query = GafferScene.AttributeQuery()
		query.addQuery( Gaffer.FloatPlug() )
		query["scene"].setInput( attributes["out"] )
		query["location"].setValue( "/sphere" )
		query["queries"][0]["name"].setValue( "test" )

		self.assertFalse( query["out"][0]["exists"].getValue() )
		self.assertEqual( query["out"][0]["value"].getValue(), 0.0 )

		query["inherit"].setValue( True )

		self.assertTrue( query["out"][0]["exists"].getValue() )
		self.assertEqual( query["out"][0]["value"].getValue(), 5.0 )

		globalAttributes["extraAttributes"].setValue( IECore.CompoundObject( { "test" : IECore.DoubleData( 10.0 ) } ) )

		self.assertTrue( query["out"][0]["exists"].getValue() )
		self.assertEqual( query["out"][0]["value"].getValue(), 10.0 )

		attributes["enabled"].setValue( True )

		self.assertTrue( query["out"][0]["exists"].getValue() )
		self.assertEqual( query["out"][0]["value"].getValue(), 2.5 )

		query["inherit"].setValue( False )

		self.assertTrue( query["out"][0]["exists"].getValue() )
		self.assertEqual( query["out"][0]["value"].getValue(), 2.5 )

	def testAttributesOutput( self ) :

		group = GafferScene.Group()

		sphere = GafferScene.Sphere()
		group["in"][0].setInput( sphere["out"] )

		sphereFilter = GafferScene.PathFilter()
		sphereFilter["paths"].setValue( IECore.StringVectorData( [ "/group/sphere" ] ) )

		groupFilter = GafferScene.PathFilter()
		groupFilter["paths"].setValue( IECore.StringVectorData( [ "/group" ] ) )

		globalAttributes = GafferScene.CustomAttributes()
		globalAttributes["in"].setInput( group["out"] )
		globalAttributes["global"].setValue( True )
		globalAttributes["extraAttributes"].setValue(
			IECore.CompoundObject( { "g" : IECore.IntData( 1 ) } )
		)

		groupAttributes = GafferScene.CustomAttributes()
		groupAttributes["in"].setInput( globalAttributes["out"] )
		groupAttributes["filter"].setInput( groupFilter["out"] )
		groupAttributes["extraAttributes"].setValue(
			IECore.CompoundObject( { "a" : IECore.IntData( 2 ), "shared" : IECore.IntData( 20 ) } )
		)

		sphereAttributes = GafferScene.CustomAttributes()
		sphereAttributes["in"].setInput( groupAttributes["out"] )
		sphereAttributes["filter"].setInput( sphereFilter["out"] )
		sphereAttributes["extraAttributes"].setValue(
			IECore.CompoundObject( { "l" : IECore.IntData( 3 ), "shared" : IECore.IntData( 30 ) } )
		)

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( sphereAttributes["out"] )

		self.assertEqual( q["attributes"].getValue(), IECore.CompoundObject() )

		q["location"].setValue( "/group/sphere" )

		self.assertFalse( q["inherit"].getValue() )
		self.assertEqual(
			q["attributes"].getValue(),
			q["scene"].attributes( "/group/sphere" )
		)

		q["inherit"].setValue( True )
		self.assertEqual(
			q["attributes"].getValue(),
			q["scene"].fullAttributes( "/group/sphere", withGlobalAttributes = True )
		)

		q["location"].setValue( "/group/missing" )
		self.assertEqual( q["attributes"].getValue(), IECore.CompoundObject() )

	def testAttributesOutputAgreesWithQueries( self ) :

		sphere = GafferScene.Sphere()

		attributes = GafferScene.CustomAttributes()
		attributes["in"].setInput( sphere["out"] )
		attributes["extraAttributes"].setValue(
			IECore.CompoundObject( { "i" : IECore.IntData( 2 ), "s" : IECore.StringData( "two" ) } )
		)

		sphereFilter = GafferScene.PathFilter()
		sphereFilter["paths"].setValue( IECore.StringVectorData( [ "/sphere" ] ) )
		attributes["filter"].setInput( sphereFilter["out"] )

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( attributes["out"] )
		q["location"].setValue( "/sphere" )
		q.addQuery( Gaffer.IntPlug(), "i" )
		q.addQuery( Gaffer.StringPlug(), "s" )

		allAttributes = q["attributes"].getValue()
		self.assertEqual( set( allAttributes.keys() ), { "i", "s" } )

		for i, name in enumerate( [ "i", "s" ] ) :
			with self.subTest( name = name ) :
				self.assertTrue( q["out"][i]["exists"].getValue() )
				self.assertEqual( q["out"][i]["value"].getValue(), allAttributes[name].value )

		# `useMetadata` doesn't add anything to `attributes`, it only affects the
		# fallback used by the individual queries.

		Gaffer.Metadata.registerValue( "attribute:test:registered", "defaultValue", 12 )
		self.addCleanup( Gaffer.Metadata.deregisterValue, "attribute:test:registered", "defaultValue" )

		q["useMetadata"].setValue( True )
		self.assertEqual( q["attributes"].getValue(), allAttributes )
		self.assertNotIn( "test:registered", q["attributes"].getValue() )

	def testAttributesOutputDirtyPropagation( self ) :

		sphere = GafferScene.Sphere()

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( sphere["out"] )
		q.addQuery( Gaffer.IntPlug(), "test" )

		cs = GafferTest.CapturingSlot( q.plugDirtiedSignal() )
		q["location"].setValue( "/sphere" )
		self.assertIn( q["attributes"], { x[0] for x in cs } )

		del cs[:]
		q["inherit"].setValue( True )
		self.assertIn( q["attributes"], { x[0] for x in cs } )

		# `useMetadata` and the queries themselves shouldn't affect `attributes`

		del cs[:]
		q["useMetadata"].setValue( True )
		self.assertNotIn( q["attributes"], { x[0] for x in cs } )

		del cs[:]
		q["queries"][0]["name"].setValue( "other" )
		self.assertNotIn( q["attributes"], { x[0] for x in cs } )

		del cs[:]
		q.addQuery( Gaffer.StringPlug(), "another" )
		self.assertNotIn( q["attributes"], { x[0] for x in cs } )

	def testUseMetadata( self ) :

		Source = GafferScene.AttributeQuery.Source

		Gaffer.Metadata.registerValue( "attribute:test:registered", "defaultValue", 12 )
		self.addCleanup( Gaffer.Metadata.deregisterValue, "attribute:test:registered", "defaultValue" )

		sphere = GafferScene.Sphere()

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( sphere["out"] )
		q["location"].setValue( "/sphere" )
		q.addQuery( Gaffer.IntPlug( defaultValue = -1 ), "test:registered" )
		q.addQuery( Gaffer.IntPlug( defaultValue = -2 ), "test:neverRegistered" )

		# Without `useMetadata`, missing attributes output the default value
		# provided by the query.

		self.assertFalse( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.None_ )
		self.assertEqual( q["out"][0]["value"].getValue(), -1 )

		self.assertFalse( q["out"][1]["exists"].getValue() )
		self.assertEqual( q["out"][1]["source"].getValue(), Source.None_ )
		self.assertEqual( q["out"][1]["value"].getValue(), -2 )

		# With it on, the registered `defaultValue` is returned instead. The attribute
		# still doesn't exist in the scene, so `exists` remains false.

		q["useMetadata"].setValue( True )
		self.assertFalse( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.Fallback )
		self.assertEqual( q["out"][0]["value"].getValue(), 12 )

		# Missing attributes with no registered `defaultValue` still return the default
		# value provided by the query.

		self.assertFalse( q["out"][1]["exists"].getValue() )
		self.assertEqual( q["out"][1]["source"].getValue(), Source.None_ )
		self.assertEqual( q["out"][1]["value"].getValue(), -2 )

		# Attributes found in the scene take precedence over the registered value.

		attributes = GafferScene.CustomAttributes()
		attributes["in"].setInput( sphere["out"] )
		attributes["extraAttributes"].setValue(
			IECore.CompoundObject( { "test:registered" : IECore.IntData( 3 ) } )
		)

		sphereFilter = GafferScene.PathFilter()
		sphereFilter["paths"].setValue( IECore.StringVectorData( [ "/sphere" ] ) )
		attributes["filter"].setInput( sphereFilter["out"] )

		q["scene"].setInput( attributes["out"] )
		self.assertTrue( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.Local )
		self.assertEqual( q["out"][0]["value"].getValue(), 3 )

		# Removing the attribute should fall back to the metadata.

		attributes["enabled"].setValue( False )
		self.assertFalse( q["out"][0]["exists"].getValue() )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.Fallback )
		self.assertEqual( q["out"][0]["value"].getValue(), 12 )

		# Querying a missing location shouldn't return the metadata
		# as the location itself doesn't exist.

		q["location"].setValue( "/missing" )
		self.assertEqual( q["out"][0]["source"].getValue(), Source.None_ )
		self.assertEqual( q["out"][0]["value"].getValue(), -1 )

	def testUseMetadataConvertsValue( self ) :

		Gaffer.Metadata.registerValue( "attribute:test:float", "defaultValue", 2.5 )
		self.addCleanup( Gaffer.Metadata.deregisterValue, "attribute:test:float", "defaultValue" )

		sphere = GafferScene.Sphere()

		q = GafferScene.AttributeQuery()
		q["scene"].setInput( sphere["out"] )
		q["location"].setValue( "/sphere" )
		q["useMetadata"].setValue( True )

		Gaffer.Metadata.registerValue( "attribute:test:matrix", "defaultValue", imath.M44f() )
		self.addCleanup( Gaffer.Metadata.deregisterValue, "attribute:test:matrix", "defaultValue" )

		q.addQuery( Gaffer.FloatPlug( defaultValue = -1.0 ), "test:float" )
		q.addQuery( Gaffer.IntPlug( defaultValue = -1 ), "test:float" )
		q.addQuery( Gaffer.FloatPlug( defaultValue = -1.0 ), "test:matrix" )

		self.assertEqual( q["out"][0]["value"].getValue(), 2.5 )
		self.assertEqual( q["out"][1]["value"].getValue(), 2 )

		self.assertEqual( q["out"][2]["value"].getValue(), -1.0 )
		self.assertEqual(
			q["out"][2]["source"].getValue(), GafferScene.AttributeQuery.Source.Fallback
		)

	def testDirtyPropagation( self ) :

		sphere = GafferScene.Sphere()

		globalAttributes = GafferScene.StandardAttributes()
		globalAttributes["in"].setInput( sphere["out"] )
		globalAttributes["global"].setValue( True )

		standardAttributes = GafferScene.StandardAttributes()
		standardAttributes["in"].setInput( globalAttributes["out"] )

		query = GafferScene.AttributeQuery()
		query.addQuery( Gaffer.BoolPlug() )
		query["scene"].setInput( standardAttributes["out"] )
		query["location"].setValue( "/sphere" )

		cs = GafferTest.CapturingSlot( query.plugDirtiedSignal() )

		standardAttributes["attributes"]["scene:visible"]["enabled"].setValue( True )
		self.assertIn( query["out"][0]["value"], { x[0] for x in cs } )

		standardAttributes["attributes"]["scene:visible"]["enabled"].setValue( False )
		del cs[:]
		query["queries"][0]["value"].setValue( True )
		self.assertIn( query["out"][0]["value"], { x[0] for x in cs } )

		# modifying the globals with the `inherit` plug disabled
		# should not dirty query["out"][0]["value"]
		del cs[:]
		globalAttributes["attributes"]["scene:visible"]["enabled"].setValue( True )
		self.assertNotIn( query["out"][0]["value"], { x[0] for x in cs } )

		query["inherit"].setValue( True )
		self.assertIn( query["out"][0]["value"], { x[0] for x in cs } )

		globalAttributes["attributes"]["scene:visible"]["enabled"].setValue( False )
		del cs[:]
		globalAttributes["attributes"]["scene:visible"]["enabled"].setValue( True )
		self.assertIn( query["out"][0]["value"], { x[0] for x in cs } )

		del cs[:]
		standardAttributes["attributes"]["scene:visible"]["enabled"].setValue( True )
		self.assertIn( query["out"][0]["value"], { x[0] for x in cs } )

		# Enabling the defaultValue metadata fallback should not dirty "exists".
		del cs[:]
		query["useMetadata"].setValue( True )
		dirtied = { x[0] for x in cs }
		self.assertIn( query["out"][0]["source"], dirtied )
		self.assertIn( query["out"][0]["value"], dirtied )
		self.assertNotIn( query["out"][0]["exists"], dirtied )

	def testLoadFrom1_7( self ) :

		script = Gaffer.ScriptNode()
		script["fileName"].setValue( pathlib.Path( __file__ ).parent / "scripts" / "attributeQuery-1.7.0.0.gfr" )
		script.load()

		query = script["AttributeQuery"]

		self.assertEqual( len( query["queries"] ), 1 )
		self.assertEqual( len( query["out"] ), 1 )
		self.assertEqual( query["location"].getValue(), "/sphere" )
		self.assertTrue( query["inherit"].getValue() )
		self.assertEqual( query["queries"][0]["name"].getValue(), "test" )
		self.assertIsInstance( query["queries"][0]["value"], Gaffer.FloatPlug )
		self.assertEqual( query["queries"][0]["value"].getValue(), 2.5 )

		self.assertTrue( query["out"][0]["exists"].getValue() )
		self.assertEqual( query["out"][0]["source"].getValue(), GafferScene.AttributeQuery.Source.Local )
		self.assertEqual( query["out"][0]["value"].getValue(), 3.5 )

		# Connections to the old node's `value` and `exists` plugs are remapped to the
		# corresponding children of `out`.

		self.assertEqual( script["Sphere1"]["radius"].getInput(), query["out"][0]["value"] )
		self.assertEqual( script["CustomAttributes1"]["enabled"].getInput(), query["out"][0]["exists"] )

		self.assertEqual( query["attribute"], query["queries"][0]["name"] )
		self.assertEqual( query["default"], query["queries"][0]["value"] )
		self.assertEqual( query["exists"], query["out"][0]["exists"] )
		self.assertEqual( query["value"], query["out"][0]["value"] )

		# Connections to the old node's `attribute` and `default` plugs are remapped
		# to the corresponding children of a query.

		queryWithInputs = script["AttributeQueryWithInputs"]

		self.assertEqual( len( queryWithInputs["queries"] ), 1 )
		self.assertEqual( len( queryWithInputs["out"] ), 1 )
		self.assertIsInstance( queryWithInputs["queries"][0]["value"], Gaffer.StringPlug )
		self.assertEqual( queryWithInputs["queries"][0]["name"].getValue(), "testString" )
		self.assertEqual( queryWithInputs["queries"][0]["name"].getInput(), script["CustomAttributes"]["attributes"]["member0"]["name"] )
		self.assertEqual( queryWithInputs["queries"][0]["value"].getValue(), "hello" )
		self.assertEqual( queryWithInputs["queries"][0]["value"].getInput(), script["CustomAttributes"]["attributes"]["member0"]["value"] )

		# Nodes that were never `setup()` could still have their `attribute` plug set or
		# connected and their `exists` output used.

		unsetupQuery = script["UnsetupAttributeQuery"]

		self.assertEqual( len( unsetupQuery["queries"] ), 1 )
		self.assertEqual( len( unsetupQuery["out"] ), 1 )
		self.assertIsInstance( unsetupQuery["queries"][0]["value"], Gaffer.StringPlug )
		self.assertEqual( unsetupQuery["queries"][0]["name"].getValue(), "missing" )
		self.assertFalse( unsetupQuery["out"][0]["exists"].getValue() )
		self.assertEqual( script["CustomAttributes2"]["enabled"].getInput(), unsetupQuery["out"][0]["exists"] )

		unsetupQueryWithInput = script["UnsetupAttributeQueryWithInput"]

		self.assertEqual( len( unsetupQueryWithInput["queries"] ), 1 )
		self.assertEqual( len( unsetupQueryWithInput["out"] ), 1 )
		self.assertIsInstance( unsetupQueryWithInput["queries"][0]["value"], Gaffer.StringPlug )
		self.assertEqual( unsetupQueryWithInput["queries"][0]["name"].getValue(), "test" )
		self.assertEqual( unsetupQueryWithInput["queries"][0]["name"].getInput(), script["CustomAttributes"]["attributes"]["member1"]["name"] )
