import xlrd
import numpy as np
from datetime import datetime

#Lecture des fichiers en entrée et transformation en table
# Choix du format
# Date & heure (objet date_time), prix de l'électricité, solar normalisé, wind normalisé
file_solar = "Data/solar.xls";
file_wind = "Data/wind.xls";

def read_generated_energy(file_solar, file_wind):
        # ouverture du fichier Excel 
    wb_solar = xlrd.open_workbook(file_solar);
    sh_solar = wb_solar.sheet_by_name(wb_solar.sheet_names()[0]);
    wb_wind = xlrd.open_workbook(file_wind);
    sh_wind = wb_wind.sheet_by_name(wb_wind.sheet_names()[0]);
    table = [];
    # code en dur : par rapport au fichier généré par le site http://www.elia.be/fr/grid-data/production/Solar-power-generation-data/Graph
    d = 0;
    s = 4;   
    w = 4;
    date_form = '%d/%m/%Y %H:%M';
    s_solar = 0;
    s_wind = 0;
    date = datetime.strptime(sh_solar.row_values(4)[d], date_form);

    
    for rownum in range(4,sh_solar.nrows):
       date_solar = datetime.strptime(sh_solar.row_values(rownum)[d], date_form);
       date_wind = datetime.strptime(sh_wind.row_values(rownum)[d], date_form);
       s_solar = s_solar + sh_solar.row_values(rownum)[s];
       s_wind = s_wind + sh_wind.row_values(rownum)[w];
       if (date_solar != date_wind) :
           raise ValueError ("The dates are not the same for the two sets");
           break;
       else :
           if (date_solar.minute == 45) :
               table = table + [[date, s_solar, s_wind] ]; 
               s_solar = 0;
               s_wind = 0;
               if (rownum < sh_solar.nrows - 1) :
                   date = datetime.strptime(sh_solar.row_values(rownum+1)[d], date_form);
    return table;
    
    
tableau = read_generated_energy(file_solar, file_wind);
file_price = "Data/price.xlsx";
country = 'France';
read_electricity_price(file_price, country, tableau);

def read_electricity_price (file_price, country, energy_table):
    wb_price = xlrd.open_workbook(file_price);
    sh_price = wb_price.sheet_by_name(wb_price.sheet_names()[0]);
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
            raise ValueError ('The dates are not the same for the two sets');
            
        else :
            energy_table[rownum-7] = energy_table[rownum-7] + [sh_price.row_values(rownum)[j]];
