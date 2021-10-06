\* The_Tie_Production_Problem *\
Maximize
Total_Profit_of_Ties_Produced: 8.22 Type_AllPoly + 16.24 Type_AllSilk
 + 8.77 Type_PolyCotton + 8.66 Type_SilkCotton
Subject To
Total_Amount_of_Cotton_Available: 0.05 Type_PolyCotton + 0.044 Type_SilkCotton
 <= 1600
Total_Amount_of_Polyester_Available: 0.08 Type_AllPoly + 0.05 Type_PolyCotton
 <= 3000
Total_Amount_of_Silk_Available: 0.125 Type_AllSilk + 0.066 Type_SilkCotton
 <= 1200
_C1: Type_AllSilk >= 5000
_C2: Type_AllSilk <= 7000
_C3: Type_AllPoly >= 10000
_C4: Type_AllPoly <= 14000
_C5: Type_PolyCotton >= 13000
_C6: Type_PolyCotton <= 16000
_C7: Type_SilkCotton >= 5000
_C8: Type_SilkCotton <= 8500
End
