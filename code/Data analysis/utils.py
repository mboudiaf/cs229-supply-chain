import xlrd
import numpy as np
from datetime import datetime


# read_generated_energy reads the file for solar energy and for wind energy
# it creates and return a table with [datetime, solar energy generated, wind energy generated]
# it compares the dates and time from file_solar and file_wind and throws an error if it is not the same

def read_generated_energy(file_solar, file_wind):
    
    #read excel files
    wb_solar = xlrd.open_workbook(file_solar);
    sh_solar = wb_solar.sheet_by_name(wb_solar.sheet_names()[0]);
    wb_wind = xlrd.open_workbook(file_wind);
    sh_wind = wb_wind.sheet_by_name(wb_wind.sheet_names()[0]);
                                    
   
    # "hard" code that depends on the chosen file(fate is in column d, solar info is in column s and wind info in column w)
    d = 0;
    s = 4;   
    w = 4;
    date_form = '%d/%m/%Y %H:%M';
    
    # initialization
    table = [];
    s_solar = 0;
    s_wind = 0;
    date = datetime.strptime(sh_solar.row_values(4)[d], date_form);

    
    for rownum in range(4,sh_solar.nrows):
       date_solar = datetime.strptime(sh_solar.row_values(rownum)[d], date_form);
       date_wind = datetime.strptime(sh_wind.row_values(rownum)[d], date_form);
       s_solar = s_solar + sh_solar.row_values(rownum)[s];
       s_wind = s_wind + sh_wind.row_values(rownum)[w];

        # both dates are compared
       if (date_solar != date_wind) :
           print("wind");
           print(date_solar);
           print(date_wind);
           raise ValueError ("The dates are not the same for the two sets");
           break;
       else :
           #in those files, the time step is 15 minutes : I turn it into a one hour time step
           if (date_solar.minute == 45) :
               table = table + [[date, s_solar, s_wind] ]; 
               s_solar = 0;
               s_wind = 0;
               if (rownum < sh_solar.nrows - 1) :
                   date = datetime.strptime(sh_solar.row_values(rownum+1)[d], date_form);
    return table;
    
# read_electrictity_price changes the output of the precedenting function
# It modifies the table energy_table and does not return anything
def read_electricity_price (file_price, country, energy_table):
    
    #read excel files
    wb_price = xlrd.open_workbook(file_price);
    sh_price = wb_price.sheet_by_name(wb_price.sheet_names()[0]);
                                      
    #look for the column corresponding to "country"
    names =  sh_price.row_values(6);
    for j in range(2,sh_price.ncols) :
        nom = names[j];
        long = len(nom);
        if (nom[0:long-10] == country) :
            break;
            
    date_form = '%b %d, %Y %I:%M %p';
    for rownum in range(7, sh_price.nrows) :
        date_price = datetime.strptime(sh_price.row_values(rownum)[0] + ' ' + sh_price.row_values(rownum)[1], date_form);
        if (date_price != energy_table[rownum-7][0]) :
            print("energy");
            print(date_price);
            print(energy_table[rownum-7][0]);
            raise ValueError ('The dates are not the same for the two sets');
            
        else :
            energy_table[rownum-7] = energy_table[rownum-7] + [sh_price.row_values(rownum)[j]];

#The generate_table will generate a table organized like this :
    # Each row represents an hour
    # The column 0 is an object which type is timedate and represents the date + hour
    # The column 1 represents the solar energy generation (in MW)
    # The column 2 represents the wind energy generation (in MW)
    # The column 3 represents the price of electricity (in Euro/MWh)
def generate_table(file_solar, file_wind, file_price, country) :
    tableau = read_generated_energy(file_solar, file_wind);
    read_electricity_price(file_price, country, tableau);
    return tableau;
    
def sort_by_hour(tableau):
    nrows, ncol = np.shape(tableau);
    sol = [[]]*24;
    win = [[]]*24;
    price = [[]]*24;    
    for i in range (nrows):
        h = int(tableau[i][0].hour);
        sol[h] = sol[h] + [tableau[i][1]];
        win[h] = win[h] + [tableau[i][2]];
        price[h] = price[h] + [tableau[i][3]];
    return sol, win, price