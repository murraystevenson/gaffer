import Gaffer
import GafferUI
import GafferDispatch
import GafferImage
import GafferScene
import GafferOSL
import GafferAppleseed

GafferUI.Examples.registerExample(
	"Rendering/Wedge Tests",
	"$GAFFER_ROOT/resources/examples/rendering/wedgeTests.gfr",
	description = "Demonstrates how to use the Wedge node to render shader wedge tests.",
	notableNodes = [
		GafferDispatch.Wedge,
		GafferDispatch.SystemCommand,
		GafferImage.Text,
		GafferScene.Outputs,
		Gaffer.ContextVariables,
		Gaffer.Expression
	]
)

GafferUI.Examples.registerExample(
	"Rendering/Macbeth Chart",
	"$GAFFER_ROOT/resources/examples/rendering/macbethChart.gfr",
	description = "Demonstrates how to create and assign a procedural OSL texture.",
	notableNodes = [
		GafferOSL.OSLCode,
		GafferOSL.OSLShader,
		Gaffer.Reference
	]
)

GafferUI.Examples.registerExample(
	"Compositing/Contact Sheet Generation",
	"$GAFFER_ROOT/resources/examples/compositing/contactSheet.gfr",
	description = "Demonstrates how to use the Loop node to build a contact sheet of shader variations.",
	notableNodes = [
		Gaffer.Loop,
		GafferImage.ImageTransform,
		Gaffer.Expression
	]
)

GafferUI.Examples.registerExample(
	"Rendering/Multi-shot Render Spreadsheet",
	"$GAFFER_ROOT/resources/examples/rendering/multiShotRenderSpreadsheet.gfr",
	description = """
	Demonstrates how to use the Spreadsheet node to vary renderer
	settings per shot.
	""",
	notableNodes = [
		Gaffer.Spreadsheet,
		GafferAppleseed.AppleseedOptions
	]
)

GafferUI.Examples.registerExample(
	"Rendering/Per-location Light Tweak Spreadsheet",
	"$GAFFER_ROOT/resources/examples/rendering/perLocationLightTweakSpreadsheet.gfr",
	description = """
	Demonstrates how to use the Spreadsheet node to vary light tweaks
	per location.
	""",
	notableNodes = [
		Gaffer.Spreadsheet,
		GafferScene.ShaderTweaks
	]
)