# sneg2
Snowpack from global long-term forecast athmospheric models calculation
=======================================================================
Program description

Variables at grid nodes:
-----------
| As defined in algorythm | Variable name | Explanation | Units |
|:-----------------------:|:--------------:|:-----:|:-----------------:|
| S  | Snowpack           |  Snowpack |    |
| Sh | SolSnowpack        | Solid phase in snow (ice fraction)|    |
| g  | LiqSnowpack        | Liquid phase in snow |   1 |
| d  | LiqSnowpackNext    |  |    |
| G  | SnowCapacity       |  |  1  |
| T  | TEMP               |  |    |
| p  | PREC               |  3|    |
| h  | SnowFrost          |  |    |
| y  | Flow               |  |    |
| Tsum | TempSum          | Накапливаемая сумма температур |   |

Параметры:
----------
| As defined in algorythm | Variable name | Explanation| Units |
|:-----------------------:|:--------------:|:-----:|:-----------------:|
| a  | meltrate | melt coefficient for snow | mm/day*grad |


