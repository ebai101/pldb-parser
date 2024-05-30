# pldb-parser

Parsing the proprietary IFF files that Reason uses to store plugin data. The format is used for other things, like a few different types of patches, but this parser is specifically for the PluginDatabase.dat file.

This is very proof-of-concept, I might make it more useful/stable in the future.

## usage

- Find your PluginDatabase.dat at `~/Library/Application Support/Propellerhead Software/Reason/Caches` (grab the newest one)
- Copy to the work dir, rename to `pldb.dat`
- Run `python pldb.py`
- Read the output. Pipe it to a file if you wish. The world is your oyster.

## uad_plugin_sync

This script leverages some of the research I did into the UAD Console's internal TCP message protocol, [more on that here.](https://github.com/ebai101/UADCtrl.spoon) It finds any UAD plugins that aren't authorized and disables them in the PluginDatabase.dat file.

Usage is very similar, just run `python uad_plugin_sync.py` after copying your PluginDatabase.dat to the work dir. You need to rename the file back to its original name and copy it back to the original folder after the script has run. Obviously, you'll need to be connected to a UAD device for this to work.

## some notes on the file format

I got some good info from the NN-XT Patch Format, which is similar to the plugin database format. [Download that here.](https://cdn.reasonstudios.com/developers/NNXT/NN-XT_Patch_File_Format.zip) It seems to be an extension of the generic IFF container format with a few quirks.

The version tag in particular is specific to this format, which has a specific 5 byte sequence to represent the version of the stored data. For example:

| byte | value    |
| ---- | -------- |
| 0xbc | reserved |
| 0x01 | major    |
| 0x00 | minor    |
| 0x02 | revision |
| 0x00 | reserved |

would be parsed as `1.0.2`.

The `enabled` and `crashed` fields were of particular interest to me. `enabled` is set to 3 if the plugin is enabled, and 5 if it is disabled. `crashed` is set to 1 if the plugin loads successfully, and 2 if not. Notably the plugin properties chunk (`PLPR`) does not generate if the plugin crashes on load.

There are a few data fields I'm not sure about, and they didn't seem necessary for what I was trying to do, so I just labeled them "unknown" of some sort. I'm not sure if the major and minor version tags are correct, either.

There's also `pldb_format.tcl`, which is a Hex Fiend template I built for reading these files in Hex Fiend. You can use that for more granular editing of the database.