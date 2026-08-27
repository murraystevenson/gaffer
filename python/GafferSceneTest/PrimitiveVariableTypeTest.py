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
#      * Neither the name of Image Engine Design Inc nor the names of
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
import math

import IECore
import IECoreScene

import Gaffer
import GafferTest
import GafferScene
import GafferSceneTest

class PrimitiveVariableTypeTest( GafferSceneTest.SceneTestCase ) :

	def __convert( self, primitive ) :

		self.__objectToScene = GafferScene.ObjectToScene()
		self.__objectToScene["object"].setValue( primitive )

		self.__filter = GafferScene.PathFilter()
		self.__filter["paths"].setValue( IECore.StringVectorData( [ "/object" ] ) )

		self.__convertNode = GafferScene.PrimitiveVariableType()
		self.__convertNode["in"].setInput( self.__objectToScene["out"] )
		self.__convertNode["filter"].setInput( self.__filter["out"] )
		self.__convertNode["primitiveVariables"].setValue( "*" )
		self.__convertNode["type"]["enabled"].setValue( True )

		return self.__convertNode

	def testConversionProducesExpectedTypes( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["float"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 0.1 )
		)
		points["half"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.HalfData( 2.5 )
		)
		points["double"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.DoubleData( -4.25 )
		)
		points["char"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.CharData( "a" )
		)
		points["uchar"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.UCharData( 65 )
		)
		points["short"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.ShortData( 3200 )
		)
		points["ushort"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.UShortData( 65 )
		)
		points["int"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.IntData( 5 )
		)
		points["uint"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.UIntData( 15 )
		)
		points["int64"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.Int64Data( 5 )
		)
		points["uint64"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.UInt64Data( 15 )
		)
		points["v2i"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.V2iData( imath.V2i( 20, 35 ) )
		)
		points["v3i"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.V3iData( imath.V3i( -10, 101, 5 ) )
		)
		points["v2f"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.V2fData( imath.V2f( 20.2, 350.1 ) )
		)
		points["v3f"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.V3fData( imath.V3f( -10.5, 101.2, 50 ) )
		)
		points["color3f"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.Color3fData( imath.Color3f( 99, 1, 505 ) )
		)
		points["color4f"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.Color4fData( imath.Color4f( 0.25, 0.5, 0.75, 1 ) )
		)
		points["floatArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatVectorData( [ 0.1, 0.4, 5.1 ] )
		)
		points["halfArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.HalfVectorData( [ 1.5, -2.5 ] )
		)
		points["doubleArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.DoubleVectorData( [ 0.1, 2.5 ] )
		)
		points["charArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.CharVectorData( [ "a", "b", "c" ] )
		)
		points["ucharArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.UCharVectorData( [ 65, 67, 68 ] )
		)
		points["shortArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.ShortVectorData( [ 3200, -101, 1 ] )
		)
		points["ushortArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.UShortVectorData( [ 65, 11, 22 ] )
		)
		points["intArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.IntVectorData( [ 3, 4, 5 ] )
		)
		points["v2iArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.V2iVectorData( [ imath.V2i( 1, 2 ), imath.V2i( 4, 5 ) ] )
		)
		points["v3iArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.V3iVectorData( [ imath.V3i( 1, 2, 3 ), imath.V3i( 4, 5, 6 ) ] )
		)
		points["v2fArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.V2fVectorData( [ imath.V2f( 111, 112 ), imath.V2f( 114, 115 ) ] )
		)
		points["v3fArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.V3fVectorData( [ imath.V3f( 1, 2, 3 ), imath.V3f( 4, 5, 6 ) ] )
		)
		points["color3fArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.Color3fVectorData( [ imath.Color3f( -1, -2, -3 ), imath.Color3f( -4, -5, -6 ) ] )
		)
		points["color4fArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.Color4fVectorData( [ imath.Color4f( 1, 2, 3, 4 ), imath.Color4f( 5, 6, 7, 8 ) ] )
		)

		convert = self.__convert( points )

		__elementTypes = {

			GafferScene.PrimitiveVariableType.ElementType.UChar : ( IECore.UCharData, IECore.UCharVectorData ),
			GafferScene.PrimitiveVariableType.ElementType.Int : ( IECore.IntData, IECore.IntVectorData ),
			GafferScene.PrimitiveVariableType.ElementType.UInt : ( IECore.UIntData, IECore.UIntVectorData ),
			GafferScene.PrimitiveVariableType.ElementType.Int64 : ( IECore.Int64Data, IECore.Int64VectorData ),
			GafferScene.PrimitiveVariableType.ElementType.UInt64 : ( IECore.UInt64Data, IECore.UInt64VectorData ),

			GafferScene.PrimitiveVariableType.ElementType.Half : ( IECore.HalfData, IECore.HalfVectorData ),
			GafferScene.PrimitiveVariableType.ElementType.Float : ( IECore.FloatData, IECore.FloatVectorData ),
			GafferScene.PrimitiveVariableType.ElementType.Double : ( IECore.DoubleData, IECore.DoubleVectorData ),

			GafferScene.PrimitiveVariableType.ElementType.V2i : ( IECore.V2iData, IECore.V2iVectorData ),
			GafferScene.PrimitiveVariableType.ElementType.V2f : ( IECore.V2fData, IECore.V2fVectorData ),
			GafferScene.PrimitiveVariableType.ElementType.V2d : ( IECore.V2dData, IECore.V2dVectorData ),

			GafferScene.PrimitiveVariableType.ElementType.V3i : ( IECore.V3iData, IECore.V3iVectorData ),
			GafferScene.PrimitiveVariableType.ElementType.V3f : ( IECore.V3fData, IECore.V3fVectorData ),
			GafferScene.PrimitiveVariableType.ElementType.V3d : ( IECore.V3dData, IECore.V3dVectorData ),

			GafferScene.PrimitiveVariableType.ElementType.Color3f : ( IECore.Color3fData, IECore.Color3fVectorData ),
			GafferScene.PrimitiveVariableType.ElementType.Color4f : ( IECore.Color4fData, IECore.Color4fVectorData ),

		}

		for elementType in GafferScene.PrimitiveVariableType.ElementType.values.values() :

			convert["type"]["value"].setValue( int( elementType ) )
			result = convert["out"].object( "/object" )

			targetDataType, targetVectorDataType = __elementTypes[ elementType ]

			for name in points.keys() :

				with self.subTest( elementType = elementType, primitiveVariable = name ) :

					self.assertIsInstance(
						result[name].data,
						targetVectorDataType if IECore.DataTraits.isSequenceDataType( points[name].data ) else targetDataType
					)
					self.assertEqual( result[name].interpolation, points[name].interpolation )
					self.assertEqual( result[name].indices, points[name].indices )

			self.assertTrue( result.arePrimitiveVariablesValid() )

	def testUnsupportedTypesRaise( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["string"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.StringData( "Invalid" )
		)
		points["stringArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.StringVectorData( [ "Invalid" ] )
		)
		points["bool"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.BoolData( True )
		)
		points["matrix"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.M44fData( imath.M44f() )
		)
		points["quaternion"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.QuatfData( imath.Quatf( 1, 2, 3, 4 ) )
		)
		points["box"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.Box3fData( imath.Box3f( imath.V3f( 0 ), imath.V3f( 1 ) ) )
		)
		points["internedString"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.InternedStringData( "Invalid" )
		)
		points["internedStringArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.InternedStringVectorData( [ "Invalid" ] )
		)
		points["boolArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.BoolVectorData( [ True ] )
		)
		points["matrix33"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.M33fData( imath.M33f() )
		)
		points["matrixArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.M44fVectorData( [ imath.M44f() ] )
		)
		points["quaternionArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.QuatfVectorData( [ imath.Quatf( 1, 2, 3, 4 ) ] )
		)
		points["box2i"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.Box2iData( imath.Box2i( imath.V2i( 0 ), imath.V2i( 1 ) ) )
		)
		points["boxArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.Box3fVectorData( [ imath.Box3f( imath.V3f( 0 ), imath.V3f( 1 ) ) ] )
		)

		convert = self.__convert( points )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Float ) )

		for name in points.keys() :
			typeName = points[name].data.typeName()
			with self.subTest( name = name, typeName = typeName ) :
				convert["primitiveVariables"].setValue( name )

				with self.assertRaisesRegex( Gaffer.ProcessException, f"PrimitiveVariableType : Primitive variable \"{name}\" has unsupported type \"{typeName}\"" ) :
					convert["out"].object( "/object" )

	def testChangingDimensions( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["float"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 5 )
		)
		points["v2f"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.V2fData( imath.V2f( 2, 3 ), IECore.GeometricData.Interpretation.UV )
		)
		points["v3f"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.V3fData( imath.V3f( 3, 4, 5 ), IECore.GeometricData.Interpretation.Normal )
		)
		points["color4f"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.Color4fData( imath.Color4f( 4, 5, 6, 1 ) )
		)

		convert = self.__convert( points )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Float ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["float"].data, IECore.FloatData( 5 ) )
		self.assertEqual( result["v2f"].data, IECore.FloatData( 2 ) )
		self.assertEqual( result["v3f"].data, IECore.FloatData( 3 ) )
		self.assertEqual( result["color4f"].data, IECore.FloatData( 4 ) )
		self.assertTrue( result.arePrimitiveVariablesValid() )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.V2f ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["float"].data, IECore.V2fData( imath.V2f( 5, 5 ) ) )
		self.assertEqual( result["v2f"].data, IECore.V2fData( imath.V2f( 2, 3 ), IECore.GeometricData.Interpretation.UV ) )
		self.assertEqual( result["v3f"].data, IECore.V2fData( imath.V2f( 3, 4 ), IECore.GeometricData.Interpretation.Normal ) )
		self.assertEqual( result["color4f"].data, IECore.V2fData( imath.V2f( 4, 5 ) ) )
		self.assertTrue( result.arePrimitiveVariablesValid() )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.V3f ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["float"].data, IECore.V3fData( imath.V3f( 5, 5, 5 ) ) )
		self.assertEqual( result["v2f"].data, IECore.V3fData( imath.V3f( 2, 3, 0 ), IECore.GeometricData.Interpretation.UV ) )
		self.assertEqual( result["v3f"].data, IECore.V3fData( imath.V3f( 3, 4, 5 ), IECore.GeometricData.Interpretation.Normal ) )
		self.assertEqual( result["color4f"].data, IECore.V3fData( imath.V3f( 4, 5, 6 ) ) )
		self.assertTrue( result.arePrimitiveVariablesValid() )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Color3f ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["float"].data, IECore.Color3fData( imath.Color3f( 5, 5, 5 ) ) )
		self.assertEqual( result["v2f"].data, IECore.Color3fData( imath.Color3f( 2, 3, 0 ) ) )
		self.assertEqual( result["v3f"].data, IECore.Color3fData( imath.Color3f( 3, 4, 5 ) ) )
		self.assertEqual( result["color4f"].data, IECore.Color3fData( imath.Color3f( 4, 5, 6 ) ) )
		self.assertTrue( result.arePrimitiveVariablesValid() )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Color4f ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["float"].data, IECore.Color4fData( imath.Color4f( 5, 5, 5, 5 ) ) )
		self.assertEqual( result["v2f"].data, IECore.Color4fData( imath.Color4f( 2, 3, 0, 0 ) ) )
		self.assertEqual( result["v3f"].data, IECore.Color4fData( imath.Color4f( 3, 4, 5, 0 ) ) )
		self.assertEqual( result["color4f"].data, IECore.Color4fData( imath.Color4f( 4, 5, 6, 1 ) ) )
		self.assertTrue( result.arePrimitiveVariablesValid() )

	def testSingleValueToVector( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["float"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 2.75 )
		)
		points["negativeFloat"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( -2.75 )
		)
		points["int"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.IntData( 3 )
		)
		points["negativeInt"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.IntData( -3 )
		)

		convert = self.__convert( points )

		for target, values in (
			( GafferScene.PrimitiveVariableType.ElementType.V3f, [ imath.V3f( 2.75 ), imath.V3f( -2.75 ), imath.V3f( 3 ), imath.V3f( -3 ) ] ),
			( GafferScene.PrimitiveVariableType.ElementType.V2f, [ imath.V2f( 2.75 ), imath.V2f( -2.75 ), imath.V2f( 3 ), imath.V2f( -3 ) ] ),
			( GafferScene.PrimitiveVariableType.ElementType.V3i, [ imath.V3i( 2 ), imath.V3i( -2 ), imath.V3i( 3 ), imath.V3i( -3 ) ] ),
			( GafferScene.PrimitiveVariableType.ElementType.V2i, [ imath.V2i( 2 ), imath.V2i( -2 ), imath.V2i( 3 ), imath.V2i( -3 ) ] ),
		 ) :
			with self.subTest( target = target ) :
				convert["type"]["value"].setValue( int( target ) )
				result = convert["out"].object( "/object" )
				self.assertEqual( result["float"].data.value, values[0] )
				self.assertEqual( result["negativeFloat"].data.value, values[1] )
				self.assertEqual( result["int"].data.value, values[2] )
				self.assertEqual( result["negativeInt"].data.value, values[3] )

				self.assertTrue( result.arePrimitiveVariablesValid() )

	def testFloatPrecision( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["f"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 0.1 )
		)
		points["d"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.DoubleData( 0.1 )
		)
		points["h"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.HalfData( 0.1 )
		)

		convert = self.__convert( points )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Float ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["f"].data, IECore.FloatData( 0.1 ) )
		self.assertEqual( result["d"].data, IECore.FloatData( 0.1 ) )
		self.assertEqual( result["h"].data, IECore.FloatData( 0.0999755859375 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Double ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["f"].data, IECore.DoubleData( 0.10000000149011612 ) )
		self.assertEqual( result["d"].data, IECore.DoubleData( 0.1 ) )
		self.assertEqual( result["h"].data, IECore.DoubleData( 0.0999755859375 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Half ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["f"].data, IECore.HalfData( 0.0999755859375 ) )
		self.assertEqual( result["d"].data, IECore.HalfData( 0.0999755859375 ) )
		self.assertEqual( result["h"].data, IECore.HalfData( 0.0999755859375 ) )

	def testNarrowingFloatingPointOverflowsToInfinity( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["big"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.DoubleData( 1e300 )
		)
		points["negativeBig"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.DoubleData( -1e300 )
		)
		points["mediumBig"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.DoubleData( 1e30 )
		)

		convert = self.__convert( points )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Float ) )
		result = convert["out"].object( "/object" )
		# Values too large for float overflow to infinity.
		self.assertEqual( result["big"].data, IECore.FloatData( float( "inf" ) ) )
		self.assertEqual( result["negativeBig"].data, IECore.FloatData( float( "-inf" ) ) )
		# This one fits, so it converts as usual.
		self.assertEqual( result["mediumBig"].data, IECore.FloatData( 1e30 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Half ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["big"].data, IECore.HalfData( float( "inf" ) ) )
		self.assertEqual( result["negativeBig"].data, IECore.HalfData( float( "-inf" ) ) )
		# Half's max is 65504, so `mediumBig` overflows as well.
		self.assertEqual( result["mediumBig"].data, IECore.HalfData( float( "inf" ) ) )

	def testFloatToIntClamping( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		# The largest float that converts to an int exactly.
		points["atIntLimit"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 2147483520 )
		)
		points["overIntLimit"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 2**31 )
		)
		points["atInt64Limit"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 2**62 )
		)
		points["overInt64Limit"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 2**63 )
		)

		convert = self.__convert( points )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Int ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["atIntLimit"].data, IECore.IntData( 2147483520 ) )
		self.assertEqual( result["overIntLimit"].data, IECore.IntData( 2**31 - 1 ) )
		self.assertEqual( result["atInt64Limit"].data, IECore.IntData( 2**31 - 1 ) )
		self.assertEqual( result["overInt64Limit"].data, IECore.IntData( 2**31 - 1 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Int64 ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["atIntLimit"].data, IECore.Int64Data( 2147483520 ) )
		self.assertEqual( result["overIntLimit"].data, IECore.Int64Data( 2**31 ) )
		self.assertEqual( result["atInt64Limit"].data, IECore.Int64Data( 2**62 ) )
		self.assertEqual( result["overInt64Limit"].data, IECore.Int64Data( 2**63 - 1 ) )

	def testOutOfRangeValuesAreClamped( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["big"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.IntData( 2147483647 )
		)
		points["negativeBig"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.IntData( -2147483648 )
		)
		points["bigFloat"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 1e30 )
		)
		points["negativeBigFloat"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( -1e30 )
		)

		convert = self.__convert( points )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.UChar ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["big"].data, IECore.UCharData( 255 ) )
		self.assertEqual( result["negativeBig"].data, IECore.UCharData( 0 ) )
		self.assertEqual( result["bigFloat"].data, IECore.UCharData( 255 ) )
		self.assertEqual( result["negativeBigFloat"].data, IECore.UCharData( 0 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Int ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["big"].data, IECore.IntData( 2147483647 ) )
		self.assertEqual( result["negativeBig"].data, IECore.IntData( -2147483648 ) )
		self.assertEqual( result["bigFloat"].data, IECore.IntData( 2147483647 ) )
		self.assertEqual( result["negativeBigFloat"].data, IECore.IntData( -2147483648 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.UInt ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["big"].data, IECore.UIntData( 2147483647 ) )
		self.assertEqual( result["negativeBig"].data, IECore.UIntData( 0 ) )
		self.assertEqual( result["bigFloat"].data, IECore.UIntData( 4294967295 ) )
		self.assertEqual( result["negativeBigFloat"].data, IECore.UIntData( 0 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Int64 ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["big"].data, IECore.Int64Data( 2147483647 ) )
		self.assertEqual( result["negativeBig"].data, IECore.Int64Data( -2147483648 ) )
		self.assertEqual( result["bigFloat"].data, IECore.Int64Data( 9223372036854775807 ) )
		self.assertEqual( result["negativeBigFloat"].data, IECore.Int64Data( -9223372036854775808 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.UInt64 ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["big"].data, IECore.UInt64Data( 2147483647 ) )
		self.assertEqual( result["negativeBig"].data, IECore.UInt64Data( 0 ) )
		self.assertEqual( result["bigFloat"].data, IECore.UInt64Data( 18446744073709551615 ) )
		self.assertEqual( result["negativeBigFloat"].data, IECore.UInt64Data( 0 ) )

	def testInf( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["inf"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( float( "inf" ) )
		)
		points["negativeInf"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( float( "-inf" ) )
		)

		convert = self.__convert( points )

		# Clamped to the destination's limits.
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.UChar ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["inf"].data, IECore.UCharData( 255 ) )
		self.assertEqual( result["negativeInf"].data, IECore.UCharData( 0 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Int ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["inf"].data, IECore.IntData( 2147483647 ) )
		self.assertEqual( result["negativeInf"].data, IECore.IntData( -2147483648 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.UInt ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["inf"].data, IECore.UIntData( 4294967295 ) )
		self.assertEqual( result["negativeInf"].data, IECore.UIntData( 0 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Int64 ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["inf"].data, IECore.Int64Data( 9223372036854775807 ) )
		self.assertEqual( result["negativeInf"].data, IECore.Int64Data( -9223372036854775808 ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.UInt64 ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["inf"].data, IECore.UInt64Data( 18446744073709551615 ) )
		self.assertEqual( result["negativeInf"].data, IECore.UInt64Data( 0 ) )

		# Preserved when converted to other floating point types.
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Double ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["inf"].data, IECore.DoubleData( float( "inf" ) ) )
		self.assertEqual( result["negativeInf"].data, IECore.DoubleData( float( "-inf" ) ) )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Half ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["inf"].data, IECore.HalfData( float( "inf" ) ) )
		self.assertEqual( result["negativeInf"].data, IECore.HalfData( float( "-inf" ) ) )

	def testNaN( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["nan"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( float( "nan" ) )
		)
		points["halfNan"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.HalfData( float( "nan" ) )
		)
		points["doubleNan"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.DoubleData( float( "nan" ) )
		)
		points["nanArray"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatVectorData( [ float( "nan" ) ] * 20000 )
		)

		convert = self.__convert( points )

		for name in points.keys() :
			with self.subTest( name = name ) :
				convert["primitiveVariables"].setValue( name )
				# Throws when converted to types without NaN.
				for elementType in [
					GafferScene.PrimitiveVariableType.ElementType.UChar,
					GafferScene.PrimitiveVariableType.ElementType.Int,
					GafferScene.PrimitiveVariableType.ElementType.UInt,
					GafferScene.PrimitiveVariableType.ElementType.Int64,
					GafferScene.PrimitiveVariableType.ElementType.UInt64,
					GafferScene.PrimitiveVariableType.ElementType.V2i,
					GafferScene.PrimitiveVariableType.ElementType.V3i,
				] :
					with self.subTest( elementType = elementType ) :
						convert["type"]["value"].setValue( int( elementType ) )
						self.assertRaises( Gaffer.ProcessException, convert["out"].object, "/object" )

				# Preserved when converted to other floating point types.
				for elementType in [
					GafferScene.PrimitiveVariableType.ElementType.Half,
					GafferScene.PrimitiveVariableType.ElementType.Double,
					GafferScene.PrimitiveVariableType.ElementType.V2f,
					GafferScene.PrimitiveVariableType.ElementType.V3f,
					GafferScene.PrimitiveVariableType.ElementType.Color3f,
					GafferScene.PrimitiveVariableType.ElementType.Color4f,
				] :
					with self.subTest( elementType = elementType ) :
						convert["type"]["value"].setValue( int( elementType ) )
						result = convert["out"].object( "/object" )
						data = result[name].data
						values = data if IECore.DataTraits.isSequenceDataType( data ) else [ data.value ]
						dimensions = values[0].dimensions() if hasattr( values[0], "dimensions" ) else 0
						for value in values :
							if dimensions > 0 :
								for x in range( dimensions ) :
									self.assertTrue( math.isnan( value[x] ) )
							else :
								self.assertTrue( math.isnan( value ) )

	def testVertexInterpolatedData( self ) :

		points = IECoreScene.PointsPrimitive( IECore.V3fVectorData( [ imath.V3f( x ) for x in range( 0, 3 ) ] ) )
		points["v"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Vertex,
			IECore.V3fVectorData( [ imath.V3f( x, x + 1, x + 2 ) for x in range( 0, 3 ) ] )
		)
		points["i"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Vertex,
			IECore.IntVectorData( [ x for x in range( 0, 3 ) ] )
		)
		points["f"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Vertex,
			IECore.FloatVectorData( [ x for x in range( 0, 3 ) ] )
		)

		convert = self.__convert( points )
		convert["primitiveVariables"].setValue( "v i f" )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Color3f ) )

		result = convert["out"].object( "/object" )
		self.assertEqual(
			result["v"].data,
			IECore.Color3fVectorData( [ imath.Color3f( x, x + 1, x + 2 ) for x in range( 0, 3 ) ] )
		)
		self.assertEqual( result["v"].interpolation, IECoreScene.PrimitiveVariable.Interpolation.Vertex )
		self.assertEqual(
			result["i"].data,
			IECore.Color3fVectorData( [ imath.Color3f( x ) for x in range( 0, 3 ) ] )
		)
		self.assertEqual( result["i"].interpolation, IECoreScene.PrimitiveVariable.Interpolation.Vertex )
		self.assertEqual(
			result["f"].data,
			IECore.Color3fVectorData( [ imath.Color3f( x ) for x in range( 0, 3 ) ] )
		)
		self.assertEqual( result["f"].interpolation, IECoreScene.PrimitiveVariable.Interpolation.Vertex )
		self.assertTrue( result.arePrimitiveVariablesValid() )

	def testEmptyVectorData( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["empty"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Vertex, IECore.IntVectorData()
		)

		convert = self.__convert( points )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.V3f ) )
		convert["interpretation"]["enabled"].setValue( True )
		convert["interpretation"]["value"].setValue( int( IECore.GeometricData.Interpretation.Normal ) )

		result = convert["out"].object( "/object" )
		self.assertIsInstance( result["empty"].data, IECore.V3fVectorData )
		self.assertEqual( len( result["empty"].data ), 0 )
		self.assertEqual( result["empty"].data.getInterpretation(), IECore.GeometricData.Interpretation.Normal )
		self.assertTrue( result.arePrimitiveVariablesValid() )

	def testColorVectorData( self ) :

		# large enough to test conversion via the parallel_for
		size = 100000

		points = IECoreScene.PointsPrimitive( size )
		points["color3"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Vertex,
			IECore.Color3fVectorData( [ imath.Color3f( x, x + 1, x + 2 ) for x in range( 0, size ) ] )
		)
		points["index"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Vertex, IECore.IntVectorData( list( range( 0, size ) ) )
		)

		convert = self.__convert( points )
		convert["primitiveVariables"].setValue( "color3 index" )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Color4f ) )

		result = convert["out"].object( "/object" )
		self.assertEqual(
			result["color3"].data,
			IECore.Color4fVectorData( [ imath.Color4f( x, x + 1, x + 2, 0 ) for x in range( 0, size ) ] )
		)
		self.assertEqual(
			result["index"].data,
			IECore.Color4fVectorData( [ imath.Color4f( x, x, x, x ) for x in range( 0, size ) ] )
		)
		self.assertTrue( result.arePrimitiveVariablesValid() )

	def testInterpolationsAndIndicesArePreserved( self ) :

		mesh = IECoreScene.MeshPrimitive.createPlane( imath.Box2f( imath.V2f( -1 ), imath.V2f( 1 ) ) )
		mesh["uniform"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Uniform, IECore.IntVectorData( [ 1 ] )
		)
		mesh["faceVarying"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.FaceVarying, IECore.IntVectorData( [ 1, 2, 3, 4 ] )
		)
		mesh["indexed"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Vertex,
			IECore.IntVectorData( [ 10, 20 ] ),
			IECore.IntVectorData( [ 0, 1, 1, 0 ] )
		)
		mesh["constant"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.IntData( 5 )
		)

		convert = self.__convert( mesh )
		convert["primitiveVariables"].setValue( "uniform faceVarying indexed constant" )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Double ) )

		result = convert["out"].object( "/object" )

		for name in [ "uniform", "faceVarying", "indexed", "constant" ] :
			with self.subTest( primitiveVariable = name ) :
				self.assertEqual( result[name].interpolation, mesh[name].interpolation )
				self.assertEqual( result[name].indices, mesh[name].indices )

		self.assertEqual( result["uniform"].data, IECore.DoubleVectorData( [ 1 ] ) )
		self.assertEqual( result["faceVarying"].data, IECore.DoubleVectorData( [ 1, 2, 3, 4 ] ) )
		# Indexed variables convert the data, not the expanded values.
		self.assertEqual( result["indexed"].data, IECore.DoubleVectorData( [ 10, 20 ] ) )
		# `Constant` variables convert to the single value type rather than the
		# array type.
		self.assertEqual( result["constant"].data, IECore.DoubleData( 5 ) )

		# Unmatched variables are untouched, so the mesh remains renderable.
		self.assertEqual( result["P"], mesh["P"] )
		self.assertEqual( result["uv"], mesh["uv"] )

		self.assertTrue( result.arePrimitiveVariablesValid() )
		self.assertSceneValid( convert["out"] )

	def testInterpretation( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["normal"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.V3fData( imath.V3f( 1, 2, 3 ), IECore.GeometricData.Interpretation.Normal )
		)
		points["color"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.Color3fData( imath.Color3f( 4, 5, 6 ) )
		)

		convert = self.__convert( points )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.V3d ) )

		# With `interpretation` disabled, the source interpretation is preserved
		# and non-geometric sources like `Color3f` get `None`.
		self.assertFalse( convert["interpretation"]["enabled"].getValue() )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["normal"].data.getInterpretation(), IECore.GeometricData.Interpretation.Normal )
		self.assertEqual( result["color"].data.getInterpretation(), IECore.GeometricData.Interpretation.None_ )

		convert["interpretation"]["enabled"].setValue( True )
		convert["interpretation"]["value"].setValue( int( IECore.GeometricData.Interpretation.Point ) )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["normal"].data.getInterpretation(), IECore.GeometricData.Interpretation.Point )
		self.assertEqual( result["color"].data.getInterpretation(), IECore.GeometricData.Interpretation.Point )

	def testInterpretationWithoutType( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["normal"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.V3fData( imath.V3f( 1, 2, 3 ), IECore.GeometricData.Interpretation.Normal )
		)
		points["uv"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.V2fData( imath.V2f( 4, 5 ), IECore.GeometricData.Interpretation.UV )
		)
		points["float"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 6 )
		)

		convert = self.__convert( points )
		convert["type"]["enabled"].setValue( False )
		convert["interpretation"]["enabled"].setValue( True )
		convert["interpretation"]["value"].setValue( int( IECore.GeometricData.Interpretation.Vector ) )

		result = convert["out"].object( "/object" )

		# Interpretations changed, while types and values unchanged
		self.assertEqual( result["normal"].data, IECore.V3fData( points["normal"].data.value, IECore.GeometricData.Interpretation.Vector ) )
		self.assertEqual( result["uv"].data, IECore.V2fData( points["uv"].data.value, IECore.GeometricData.Interpretation.Vector ) )
		# FloatData is left unchanged
		self.assertEqual( result["float"].data, points["float"].data )

	def testInterpretationAndType( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["normal"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.V3fData( imath.V3f( 1, 2, 3 ), IECore.GeometricData.Interpretation.Normal )
		)
		points["uv"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.V2fData( imath.V2f( 4, 5 ), IECore.GeometricData.Interpretation.UV )
		)
		points["float"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.FloatData( 6 )
		)

		convert = self.__convert( points )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.V3f ) )
		convert["interpretation"]["enabled"].setValue( True )
		convert["interpretation"]["value"].setValue( int( IECore.GeometricData.Interpretation.Vector ) )

		result = convert["out"].object( "/object" )
		self.assertEqual( result["normal"].data.value, imath.V3f( 1, 2, 3 ) )
		self.assertEqual( result["normal"].data.getInterpretation(), IECore.GeometricData.Interpretation.Vector )
		self.assertEqual( result["uv"].data.value, imath.V3f( 4, 5, 0 ) )
		self.assertEqual( result["uv"].data.getInterpretation(), IECore.GeometricData.Interpretation.Vector )
		self.assertEqual( result["float"].data.value, imath.V3f( 6, 6, 6 ) )
		self.assertEqual( result["float"].data.getInterpretation(), IECore.GeometricData.Interpretation.Vector )

	def testInterpretationLostOnNonGeometricTypes( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["normal"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.V3fData( imath.V3f( 1, 2, 3 ), IECore.GeometricData.Interpretation.Normal )
		)

		convert = self.__convert( points )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Color3f ) )

		result = convert["out"].object( "/object" )
		self.assertEqual( result["normal"].data, IECore.Color3fData( imath.Color3f( 1, 2, 3 ) ) )

		convert["interpretation"]["enabled"].setValue( True )
		convert["interpretation"]["value"].setValue( int( IECore.GeometricData.Interpretation.Point ) )
		self.assertEqual( convert["out"].object( "/object" ), result )

		convert2 = GafferScene.PrimitiveVariableType()
		convert2["in"].setInput( convert["out"] )
		convert2["filter"].setInput( self.__filter["out"] )
		convert2["primitiveVariables"].setValue( "*" )
		convert2["type"]["enabled"].setValue( True )
		convert2["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.V3f ) )

		result = convert2["out"].object( "/object" )
		self.assertEqual( result["normal"].data.value, imath.V3f( 1, 2, 3 ) )
		self.assertEqual( result["normal"].data.getInterpretation(), IECore.GeometricData.Interpretation.None_ )

	def testNameMatching( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["a"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.IntData( 1 )
		)
		points["aa"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.IntData( 2 )
		)

		convert = self.__convert( points )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Float ) )
		convert["primitiveVariables"].setValue( "a" )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["a"].data, IECore.FloatData( 1 ) )
		self.assertEqual( result["aa"].data, points["aa"].data )

		convert["primitiveVariables"].setValue( "aa" )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["a"].data, points["a"].data )
		self.assertEqual( result["aa"].data, IECore.FloatData( 2 ) )

		convert["primitiveVariables"].setValue( "a*" )
		result = convert["out"].object( "/object" )
		self.assertEqual( result["a"].data, IECore.FloatData( 1 ) )
		self.assertEqual( result["aa"].data, IECore.FloatData( 2 ) )

	def testPassThroughs( self ) :

		points = IECoreScene.PointsPrimitive( 0 )
		points["int"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant, IECore.IntData( 1 )
		)
		points["point"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Constant,
			IECore.V3fData( imath.V3f( 1, 2, 3 ), IECore.GeometricData.Interpretation.Point )
		)

		convert = self.__convert( points )

		convert["type"]["enabled"].setValue( False )
		self.assertFalse( convert["interpretation"]["enabled"].getValue() )
		self.assertScenesEqual( convert["out"], convert["in"] )
		self.assertSceneHashesEqual( convert["out"], convert["in"] )

		convert["type"]["enabled"].setValue( True )

		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Float ) )
		convert["primitiveVariables"].setValue( "" )
		self.assertScenesEqual( convert["out"], convert["in"] )
		self.assertSceneHashesEqual( convert["out"], convert["in"] )

		# Variables already of the requested type shouldn't change the object.
		convert["primitiveVariables"].setValue( "int" )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Int ) )
		self.assertScenesEqual( convert["out"], convert["in"] )

		# `interpretation` doesn't change the object, because `int` has no interpretation.
		convert["interpretation"]["enabled"].setValue( True )
		convert["interpretation"]["value"].setValue( int( IECore.GeometricData.Interpretation.Point ) )
		self.assertScenesEqual( convert["out"], convert["in"] )

		# Attempting to set "point" to its current interpretation shouldn't change the object.
		convert["primitiveVariables"].setValue( "point" )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.V3f ) )
		self.assertScenesEqual( convert["out"], convert["in"] )

	def testNonPrimitiveObjectsAreUnchanged( self ) :

		camera = GafferScene.Camera()

		pathFilter = GafferScene.PathFilter()
		pathFilter["paths"].setValue( IECore.StringVectorData( [ "/camera" ] ) )

		convert = GafferScene.PrimitiveVariableType()
		convert["in"].setInput( camera["out"] )
		convert["filter"].setInput( pathFilter["out"] )
		convert["primitiveVariables"].setValue( "*" )
		convert["type"]["enabled"].setValue( True )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.Double ) )
		convert["interpretation"]["enabled"].setValue( True )
		convert["interpretation"]["value"].setValue( int( IECore.GeometricData.Interpretation.Point ) )

		self.assertScenesEqual( convert["out"], camera["out"] )
		self.assertSceneValid( convert["out"] )

	def testDirtyPropagation( self ) :

		convert = GafferScene.PrimitiveVariableType()

		for plug, value in [
			( convert["primitiveVariables"], "*" ),
			( convert["type"]["enabled"], True ),
			( convert["type"]["value"], int( GafferScene.PrimitiveVariableType.ElementType.Int ) ),
			( convert["interpretation"]["enabled"], True ),
			( convert["interpretation"]["value"], int( IECore.GeometricData.Interpretation.Normal ) ),
		] :
			with self.subTest( plug = plug.relativeName( convert ) ) :
				cs = GafferTest.CapturingSlot( convert.plugDirtiedSignal() )
				plug.setValue( value )
				self.assertIn( convert["out"]["object"], [ x[0] for x in cs ] )

	@GafferTest.TestRunner.PerformanceTestMethod()
	def testPerformance( self ) :

		plane = GafferScene.Plane()
		plane["divisions"].setValue( imath.V2i( 3000, 3000 ) )

		pathFilter = GafferScene.PathFilter()
		pathFilter["paths"].setValue( IECore.StringVectorData( [ "/plane" ] ) )

		convert = GafferScene.PrimitiveVariableType()
		convert["in"].setInput( plane["out"] )
		convert["filter"].setInput( pathFilter["out"] )
		convert["primitiveVariables"].setValue( "P uv" )
		convert["type"]["enabled"].setValue( True )
		convert["type"]["value"].setValue( int( GafferScene.PrimitiveVariableType.ElementType.V3d ) )

		convert["in"].object( "/plane" )

		with GafferTest.TestRunner.PerformanceScope() :
			convert["out"].object( "/plane" )
