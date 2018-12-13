import utils
import numpy as np
import matplotlib.pyplot as plt


country = 'France';

sol1 = "Data/sol_jan (2).xls";
sol2 = "Data/sol_feb (2).xls";
sol3 = "Data/sol_march (2).xls";

win1 = "Data/win_jan (2).xls";
win2 = "Data/win_feb (2).xls";
win3 = "Data/win_march (2).xls";

price1 = "Data/price_jan.xlsx";
price2 = "Data/price_feb.xlsx";
price3 = "Data/price_march.xlsx";

#t = read_generated_energy(sol1,win1);

tab1 = utils.generate_table(sol1, win1, price1, country);
tab2 = utils.generate_table(sol2, win2, price2, country);
tab3 = utils.generate_table(sol3, win3, price3, country);
tab = tab1 + tab2 + tab3;

sol, win, price = utils.sort_by_hour(tab);
plt.hist(sol[10]) #histogramme de la production solaire à 10h