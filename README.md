This repository contains scripts used to parse binary files from Mario Kart 7. These scripts are made by AI.

## MK7_BCTR_analysis
Parses and prints `.bctr` information to the screen. These files are used for managing layouts. Works for Nintendogs+cats as well.

`Usage: python MK7_BCTR_analysis.py <file.bctr>`

## MK7_BSEQ_analyser
Parses and prints `.bss` / `.brs` information to the screen. These files contain data related to menus and traversing to and from other menus. Works for Nintendogs+cats as well.

`Usage: python MK7_BSEQ_analyser.py <bseq_filename>`

## MK7_BSEQ_analyser_e3_2010
Parses and prints `.bss` / `.brs` information to the screen (E3 2010 demo format). These files contain data related to menus and traversing to and from other menus. Works for Nintendogs+cats as well.

`Usage: python MK7_BSEQ_analyser_e3_2010.py <bseq_filename>`

## MK7_BSEQ_FlowList_Export
Exports a section of BSEQ that contains information related to traversing to and from menus to an output .xml file. Works for Nintendogs+cats as well.

`Usage: python export_sequence_flow_xml.py input.bss (or input.brs) output.xml`

# mk7_parse_binary_csv
Converts binary-CSV files from .bin to .csv (`bin2csv`) and viceversa (`csv2bin`). An additional argument (`datatype`) exists in order to specify the data type of the values stored by the binary-CSV file (defaults to `int`).

`Usage: mk7_parse_binary_csv.py <mode: bin2csv|csv2bin> <datatype: -int|-f32|-vec3> <input_file> <output_file>`

where:
* `int`  (signed integer)
* `f32`  (float)
* `vec3` (a vector of 3 float components, XYZ)

# MK7 BCTR Advanced EditorGUI
GUI editor for `.bctr` files, based on `MK7_BCTR_analysis`. By [luigifan27](https://github.com/LoigiFan72).

# MK7 BSEQ ViewerGUI
GUI version of `MK7_BSEQ_analyser`. By [luigifan27](https://github.com/LoigiFan72).

# MK7 E3 BSEQ ViewerGUI
GUI version of `MK7_BSEQ_analyser_e3_2010`. By [luigifan27](https://github.com/LoigiFan72).
