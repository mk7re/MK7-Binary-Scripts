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

The following files can be edited using this script. Next to each filename is the datatype you have to specify when executing the script:
<details>
<summary>Common.szs</summary>

```
Effect/Menu/GPUPtclEnvMenu.bin (-f32)
Enemy/EnemyRivalTable.bin (-int)
Kart/Data/KartParts_Param_Accel.bin (-f32)
Kart/Data/KartParts_Param_DriftStart.bin (-f32)
Kart/Data/KartParts_Param_Miniturbo.bin (-f32)
Kart/Data/KartParts_Param_OffRoad.bin (-f32)
Kart/Data/KartParts_Param_Speed_Air.bin (-f32)
Kart/Data/KartParts_Param_Speed_Land.bin (-f32)
Kart/Data/KartParts_Param_Speed_Sea.bin (-f32)
Kart/Data/KartParts_Param_TireFeeling.bin (-f32)
Kart/Data/KartParts_Param_Turn_Air.bin (-f32)
Kart/Data/KartParts_Param_Turn_Land.bin (-f32)
Kart/Data/KartParts_Param_Turn_Seea.bin (-f32)
Kart/Data/KartParts_Param_Weight.bin (-f32)
Kart/Data/KartParts_Point_Body.bin (-int)
Kart/Data/KartParts_Point_Driver.bin (-int)
Kart/Data/KartParts_Point_Tire.bin (-int)
Kart/Data/KartParts_Point_Wing.bin (-int)
```
</details>

<details>
<summary>RaceCommon.szs</summary>

```
Data/GeoHitTableItem.bin (-int)
Data/GeoHitTableItemObj.bin (-int)
Data/GeoHitTableKart.bin (-int)
Data/GeoHitTableKartObj.bin (-int)
Effect/GPUPtclEnv0.bin (-f32)
Effect/GPUPtclEnv1.bin (-f32)
Effect/GPUPtclEnv2.bin (-f32)
Effect/GPUPtclEnv3.bin (-f32)
Effect/GPUPtclStripe_Koura.bin (-f32)
Effect/GPUPtclTail_Bubble.bin (-f32)
Effect/GPUPtclTail_DriftSandSmoke.bin (-f32)
Effect/GPUPtclTail_FireBall.bin (-f32)
Effect/GPUPtclTail_Screw.bin (-f32)
Effect/GPUPtclTail_TrainSmoke.bin (-f32)
Effect/MufflerParam.bin (-vec3)
Effect/TireParam.bin (-vec3)
Effect/TireParamFP.bin (-vec3)
Enemy/EnemyCourseParamTable.bin (-f32)
Enemy/EnemyProbabilityTableEasy.bin (-int)
Enemy/EnemyProbabilityTableHard.bin (-int)
Enemy/EnemyProbabilityTableNormal.bin (-int)
Item/ItemReactTable.bin (-int)
Item/ItemSlotTable_Balloon.bin (-int)
Item/ItemSlotTable_Balloon_AI.bin (-int)
Item/ItemSlotTable_Balloon_Banana.bin (-int)
Item/ItemSlotTable_Balloon_Bomhei.bin (-int)
Item/ItemSlotTable_Balloon_Kinoko.bin (-int)
Item/ItemSlotTable_Balloon_Koura.bin (-int)
Item/ItemSlotTable_Balloon_WiFi.bin (-int)
Item/ItemSlotTable_Balloon_WiFi_AI.bin (-int)
Item/ItemSlotTable_Banana.bin (-int)
Item/ItemSlotTable_Bomb.bin (-int)
Item/ItemSlotTable_Coin.bin (-int)
Item/ItemSlotTable_Coin_AI.bin (-int)
Item/ItemSlotTable_Coin_Banana.bin (-int)
Item/ItemSlotTable_Coin_Bomhei.bin (-int)
Item/ItemSlotTable_Coin_Kinoko.bin (-int)
Item/ItemSlotTable_Coin_Koura.bin (-int)
Item/ItemSlotTable_Coin_WiFi.bin (-int)
Item/ItemSlotTable_Coin_WiFi_AI.bin (-int)
Item/ItemSlotTable_Decided.bin (-int)
Item/ItemSlotTable_GrandPrix.bin (-int)
Item/ItemSlotTable_GrandPrix_AI.bin (-int)
Item/ItemSlotTable_Kinoko.bin (-int)
Item/ItemSlotTable_Koura.bin (-int)
Item/ItemSlotTable_Title.bin (-int)
Item/ItemSlotTable_VS.bin (-int)
Item/ItemSlotTable_VS_AI.bin (-int)
Item/ItemSlotTable_WiFi.bin (-int)
Item/ItemSlotTable_WiFi_AI.bin (-int)
```
</details>
</br>

# MK7 BCTR Advanced EditorGUI
GUI editor for `.bctr` files, based on `MK7_BCTR_analysis`. By [luigifan27](https://github.com/LoigiFan72).

# MK7 BSEQ ViewerGUI
GUI version of `MK7_BSEQ_analyser`. By [luigifan27](https://github.com/LoigiFan72).

# MK7 E3 BSEQ ViewerGUI
GUI version of `MK7_BSEQ_analyser_e3_2010`. By [luigifan27](https://github.com/LoigiFan72).
