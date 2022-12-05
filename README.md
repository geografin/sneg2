# sneg2
Snowpack from global long-term forecast athmospheric models calculation
=======================================================================
Program description

Variables at grid nodes:
-----------
| As defined in algorythm | Variable name | Sense | Units |
|:-----------------------:|:--------------:|:-----:|:-----------------:|
| S  | Snowpack           |  Снегозапас |    |
| Sh | SolSnowpack        | Твердая фаза воды в снеге (льдистость?)|    |
| g  | LiqSnowpack        | Жидкая фаза воды в снеге |   1 |
| d  | LiqSnowpackNext    |  |    |
| G  | SnowCapacity       |  |  1  |
| T  | TEMP               |  |    |
| p  | PREC               |  3|    |
| h  | SnowFrost          |  |    |
| y  | Flow               |  |    |
| Tsum | TempSum          | Накапливаемая сумма температур |   |

Параметры:
----------
| Обозначение в алгоритме | Имя переменной | Смысл | Единицы измерения |
|:-----------------------:|:--------------:|:-----:|:-----------------:|
| a  | meltrate | коэффициент стаивания снега | мм/сут*градус |


