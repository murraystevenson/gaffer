#!/usr/bin/env python
##########################################################################
#
#  Copyright (c) 2023, Cinesite VFX Ltd. All rights reserved.
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

import argparse
import github
import glob
import hashlib
import os
import pathlib
import sys
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from urllib.request import urlretrieve

# Validates the images generated a Gaffer build by comparing them against an existing set of reference images.
# Graphics and documentation images are tested by default, but either test can be skipped with `--skip-graphics` or `--skip-images`.

parser = argparse.ArgumentParser()

parser.add_argument(
	"--check",
	dest = "check",
	required = True,
	help = "The path to a gaffer folder or archive file to check the images within."
)

parser.add_argument(
	"--reference",
	dest = "reference",
	default = "",
	required = False,
	help = "The path to a gaffer folder containing reference images to compare against."
)

parser.add_argument(
	"--failpercent",
	dest = "failpercent",
	default = "3",
	required = False,
	help = "The percentage of pixels that must differ before a failure is reported."
)

parser.add_argument(
	"--failvalue",
	dest = "failvalue",
	default = "0.05",
	required = False,
	help = "The threshold before a pixel is considered different."
)

parser.add_argument(
	"--perceptual",
	dest = "perceptual",
	required = False,
	help = "Perform a perceptual diff of the images."
)

parser.add_argument(
	"--skip-graphics",
	dest = "skipGraphics",
	action = "store_true",
	required = False,
	help = "Skip validation of graphics."
)

parser.add_argument(
	"--skip-images",
	dest = "skipImages",
	action = "store_true",
	required = False,
	help = "Skip validation of documentation images."
)

parser.add_argument(
	"--report",
	dest = "report",
	required = False,
	help = "The path to output an HTML report of the changes."
)

parser.add_argument(
	"--ci",
	dest = "ci",
	action = "store_true",
	required = False,
	help = "CI mode. Reference images will be downloaded from an existing release determined by the GITHUB_REF_NAME environment variable."
)

parser.add_argument(
	"--github-access-token",
	dest = "githubAccessToken",
	default = os.environ.get( "GITHUB_ACCESS_TOKEN", None ),
	help = "A suitable access token to authenticate the GitHub API."
)

args = parser.parse_args()

def __generateReport( missing, differences, info ) :

	html = """\
<!DOCTYPE html>
<html><head><title>Image Comparison</title>
<style>
	body { background-color: grey; }
	table { border-collapse: collapse; width: 100%; }
	th { text-align: left; }
	th, td { max-width: 512px; border-top: 1px solid; }
	img { max-width: 100%; height: auto; image-rendering: pixelated; }
	.textbox { width: 50px; }
	.slider { width: 200px; }
	.toolbar { position: fixed; bottom: 50px; right: 50px; }
</style>
</head>
<body>
	<table>
		<tr>
			<th>File</th>
			<th>Reference</th>
			<th>Incoming</th>
			<th>Diff</th>
			<th>Log</th>
		</tr>
"""

	for m in sorted( missing ) :
		html += f"""\
		<tr>
			<td>{ m }</td>
			<td><a href="reference/{ m }" target="_blank"><img src="reference/{ m }"></a></td>
			<td><p style="color: darkred"><b>FILE MISSING</b></p></td>
			<td></td>
			<td></td>
		</tr>
"""

	for d in sorted( differences ) :
		log = info[ d ].replace( "\n", "<br />" )
		html += f"""\
		<tr>
			<td>{ d }</td>
			<td><a href="reference/{ d }" target="_blank"><img src="reference/{ d }"></a></td>
			<td><a href="incoming/{ d }" target="_blank"><img src="incoming/{ d }"></a></td>
			<td><a href="diff/{ d }" target="_blank"><img class="diff" src="diff/{ d }"></a></td>
			<td>{ log }</td>
		</tr>
"""

	html += """\
	</table>
	<div class="toolbar">
		<button title="White Background" class="white-button" onclick="document.body.style.backgroundColor = 'white'; document.body.style.color = 'black';">White</button>
		<button title="Grey Background" class="grey-button" onclick="document.body.style.backgroundColor = 'grey'; document.body.style.color = 'black';">Grey</button>
		<button title="Black Background" class="black-button" onclick="document.body.style.backgroundColor = 'black'; document.body.style.color = 'white';">Black</button>
		<label for="brightness">B:</label>
		<input title="Brightness" type="number" id="brightness" class="textbox" value="1" min="0" max="10" step="0.01" oninput="updateImageFilter( 0 )">
		<input title="Brightness" type="range" id="brightness-slider" class="slider" value="1" min="0" max="5" step="0.01" oninput="updateImageFilter( 1 )">
		<label for="contrast">C:</label>
		<input title="Contrast" type="number" id="contrast" class="textbox" value="1" min="0" max="5" step="0.01" oninput="updateImageFilter( 0 )">
		<input title="Contrast" type="range" id="contrast-slider" class="slider" value="1" min="0" max="2" step="0.01" oninput="updateImageFilter( 1 )">
		<label for="saturate">S:</label>
		<input title="Saturation" type="number" id="saturate" class="textbox" value="1" min="0" max="5" step="0.01" oninput="updateImageFilter( 0 )">
		<input title="Saturation" type="range" id="saturate-slider" class="slider" value="1" min="0" max="2" step="0.01" oninput="updateImageFilter( 1 )">
		<button title="No Minimum Image Width" onclick="setMinWidth(0)">0</button>
		<button title="Minimum Image Width: 64px" onclick="setMinWidth(64)">64</button>
		<button title="Minimum Image Width: 256px" onclick="setMinWidth(256)">256</button>
		<button title="Minimum Image Width: 512px" onclick="setMinWidth(512)">512</button>
	</div>
	<script>
		function updateImageFilter( slider )
		{
			var brightness = document.getElementById( slider ? "brightness-slider" : "brightness" ).value;
			var contrast = document.getElementById( slider ? "contrast-slider" : "contrast" ).value;
			var saturate = document.getElementById( slider ? "saturate-slider" : "saturate" ).value;

			document.getElementById( slider ? "brightness" : "brightness-slider" ).value = brightness;
			document.getElementById( slider ? "contrast" : "contrast-slider" ).value = contrast;
			document.getElementById( slider ? "saturate" : "saturate-slider" ).value = saturate;

			var images = document.getElementsByClassName( "diff" );
			for( var i = 0; i < images.length; i++ )
			{
				images[i].style.filter = "brightness(" + brightness + ") contrast(" + contrast + ") saturate( " + saturate + " )";
			}
		}
		function setMinWidth( width )
		{
			var images = document.getElementsByTagName( "img" );
			for( var i = 0; i < images.length; i++ )
			{
				images[i].style.minWidth = `${width}px`;
			}
		}
	</script>
"""

	html += "</body></html>"

	return html

def __downloadReleasePackage( downloadPath ) :

	target = os.environ.get( "GITHUB_REF_NAME" )
	if not target :
		parser.exit( 1, "GITHUB_REF_NAME not defined, unable to determine release version to compare against." )

	client = github.Github( args.githubAccessToken )
	repo = client.get_repo( "GafferHQ/gaffer" )
	targetVersion = None
	if target.endswith( "_maintenance" ) :
		targetVersion = target.split( "_" )[0]
	elif "/tags" in os.environ.get( "GITHUB_REF" ) :
		targetVersion = ".".join( target.split( "." )[:2] )

	release = None
	if targetVersion :
		for r in repo.get_releases() :
			if r.tag_name.startswith( targetVersion ) :
				release = r
				break
	else :
		# use the latest release for lack of a specific target...
		release = repo.get_latest_release()

	if not release :
		parser.exit( 1, "No release found for target: '{}'.".format( target ) )

	platform = { "darwin" : "macos", "win32" : "windows" }.get( sys.platform, "linux" )
	extension = "zip" if platform == "windows" else "tar.gz"
	packageName = "gaffer-{}-{}.{}".format( release.tag_name, platform, extension )

	package = None
	for asset in release.get_assets() :
		if asset.name == packageName :
			package = asset
			break

	if not package :
		parser.exit( 1, "No package found for release: '{}'.".format( release.title ) )

	fileName, headers = urlretrieve( package.browser_download_url, pathlib.Path( downloadPath ) / packageName )

	return fileName

def __extractArchive( archiveFile, extractionPath, subdirectoryToExtract = "" ) :

	if str( archiveFile ).endswith( ".tar.gz" ) :
		package = archiveFile.name[:-len(".tar.gz")]
		archiveRoot = pathlib.Path( package ) / subdirectoryToExtract

		with tarfile.open( archiveFile, "r:gz" ) as a :

			members = [
				tarinfo for tarinfo in a.getmembers()
				if tarinfo.name.startswith( str( archiveRoot ) )
			]

			a.extractall( members = members, path = extractionPath )

	elif str( archiveFile ).endswith( ".zip" ) :
		package = archiveFile.name[:-len(".zip")]
		archiveRoot = pathlib.Path( package ) / subdirectoryToExtract

		with zipfile.ZipFile( archiveFile, "r" ) as a:
			for member in a.infolist() :
				# filenames returned by zipfile.infolist have POSIX-style paths
				if member.filename.startswith( str( archiveRoot.as_posix() ) ) :
					a.extract( member, path = extractionPath )
	else :
		parser.exit( 1, "Unknown archive: {}".format( archiveFile ) )

	return extractionPath / archiveRoot

if not args.reference and not args.ci :
	parser.exit( 1, "Provide a gaffer directory to compare against with --reference, or run in --ci mode where one will be downloaded." )

if args.skipImages and args.skipGraphics :
	parser.exit( 1, "All checks skipped, nothing to do." )

# Perform a glob match of the check and reference paths as Windows does not automatically expand glob patterns
if args.reference :
	referencePaths = glob.glob( args.reference )
	if len( referencePaths ) != 1 or not pathlib.Path( referencePaths[0] ).exists() :
		parser.exit( 1, "Invalid path provided to --reference, it should be a single gaffer directory or archive file." )

	referenceDirectory = pathlib.Path( referencePaths[0] )

checkPaths = glob.glob( args.check )
if len( checkPaths ) != 1 or not pathlib.Path( checkPaths[0] ).exists() :
	parser.exit( 1, "Invalid path provided to --check, it should be a single gaffer directory or archive file." )

if checkPaths[0].endswith( ( ".tar.gz", ".zip" ) ) :
	tempArchiveDirectory = tempfile.TemporaryDirectory()
	gafferDirectory = __extractArchive( pathlib.Path( checkPaths[0] ), tempArchiveDirectory.name )
else :
	gafferDirectory = pathlib.Path( checkPaths[0] )

directoriesToCheck = []
if not args.skipImages :
	directoriesToCheck.append( pathlib.Path( "doc", "gaffer", "html", "_images" ) )
if not args.skipGraphics :
	directoriesToCheck.append( pathlib.Path( "graphics" ) )

if not any( [ ( gafferDirectory / d ).exists() for d in directoriesToCheck ] ):
	parser.exit( 1, "No image directories found to check within '{}'.".format( gafferDirectory ) )

gafferCommand = gafferDirectory / "bin" / ( "gaffer.cmd" if sys.platform == "win32" else "gaffer" )
diff = "--pdiff" if args.perceptual else "--diff"
differences = []
missing = []
info = {}

if args.report :
	reportDirectory = pathlib.Path( args.report )

if args.ci :
	archiveTempDirectory = tempfile.TemporaryDirectory()
	archiveFile = __downloadReleasePackage( archiveTempDirectory.name )

for directoryToCheck in directoriesToCheck :

	incomingImageDirectory = gafferDirectory / directoryToCheck
	if not incomingImageDirectory.exists() :
		print( "Image directory '{}' does not exist, skipping check.".format( incomingImageDirectory ) )
		continue

	if args.ci :
		referenceImageDirectory = __extractArchive( archiveFile, archiveTempDirectory.name, directoryToCheck )
	else :
		referenceImageDirectory = referenceDirectory / directoryToCheck

	if not referenceImageDirectory.exists() :
		print( "Reference image directory '{}' does not exist, skipping check.".format( referenceImageDirectory ) )
		continue

	for referenceImage in sorted( referenceImageDirectory.glob( "*.png" ) ) :

		imageToCheck = incomingImageDirectory / referenceImage.name
		relativeFileName = directoryToCheck / referenceImage.name
		if not imageToCheck.is_file() :
			missing.append( relativeFileName )
			if args.report :
				( reportDirectory / "reference" / directoryToCheck ).mkdir( parents = True, exist_ok = True )
				shutil.copyfile( referenceImage, reportDirectory / "reference" / relativeFileName )
			continue

		# compare image hashes as an early out to avoid doing a more expensive image comparison
		with open( imageToCheck, mode = "rb" ) as f1, open( referenceImage, mode = "rb" ) as f2 :
			h1 = hashlib.md5()
			h2 = hashlib.md5()
			h1.update( f1.read() )
			h2.update( f2.read() )
			if h1.hexdigest() == h2.hexdigest() :
				continue

		if subprocess.call( [ str( gafferCommand ), "env", "oiiotool", str( referenceImage ), str( imageToCheck ), "--failpercent", args.failpercent, "--fail", args.failvalue, diff ] ) != 0 :
			differences.append( relativeFileName )
			if args.report :
				for d in [ "reference", "incoming", "diff" ] :
					( reportDirectory / d / directoryToCheck ).mkdir( parents = True, exist_ok = True )
				# generate an image showing the diff of the RGB channels
				result = subprocess.run(
					[ str( gafferCommand ), "env", "oiiotool", str( referenceImage ), "--ch", "R,G,B", str( imageToCheck ), "--ch", "R,G,B", "--failpercent", args.failpercent, "--fail", args.failvalue, diff, "--absdiff", "--ch", "R,G,B", "-o", str( reportDirectory / "diff" / relativeFileName ) ],
					capture_output = True, text = True
				)
				info[ relativeFileName ] = result.stdout
				shutil.copyfile( imageToCheck, reportDirectory / "incoming" / relativeFileName )
				shutil.copyfile( referenceImage, reportDirectory / "reference" / relativeFileName )

# flush to prevent our final logging from being mixed
# up in any of the previous reporting
sys.stderr.flush()
sys.stdout.flush()

if missing or differences :

	sys.stderr.write( "\nValidation failed:" )
	sys.stderr.write(
		"\n" + "\n".join( [ f"WARNING: '{ m }' is missing" for m in sorted( missing ) ] )
	)
	sys.stderr.write(
		"\n" + "\n".join( [ f"WARNING: '{ d }' has differences" for d in sorted( differences ) ] )
	)

	sys.stderr.write( "\n\nSummary:\n" )
	if missing :
		sys.stderr.write( "Images missing: {}\n".format( len( missing ) ) )
	if differences :
		sys.stderr.write( "Images with differences: {}\n".format( len( differences ) ) )

	if args.report :
		with open( reportDirectory / "index.html", "w" ) as f :
			f.write( __generateReport( missing, differences, info ) )
			print( "\nReport written to: {}".format( f.name ) )

		if args.ci and os.environ.get( "GITHUB_OUTPUT", None ) :
			with open( os.environ["GITHUB_OUTPUT"], "a" ) as f :
				f.write( "report={}\n".format( args.report ) )

	sys.exit( 1 )

else :

	print( "No differences found." )
