%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%% ME370C - Project: Improvement of Adiabatic CAES %%%%%%%%%%%%
%%%%%%%%% Calvin McSweeny                                 %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%% Study of adiabatic Pressur Vessel-Cyclic behavior %%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%% I. Adiabatic pressur vessel

% Assumptions:
% 1/ Air behaves as ideal gas
% 2/ Adiabatic pressure vessel (no heat loss)

% Ambient conditions
Tamb = 25+273.15; %[K]
Pamb = oneatm; %[Pa]

R = 8.314; %[m^3.Pa/(mol.K)]
M_air = 28.976; %[g/mol]
R_air = 1e3*R/M_air; %[m^3.Pa/(kg.K)]
gamma_air = 1.4; %[]

% Characteristics
P_storage = 60e5; % [Pa] Storage pressure in the pressure vessell
P_prime = 20e5; % [Pa] Operational pressure (optimal turbine efficiency)
V_storage = 1e5; % [m^3] Volume of the pressure vessel
mdotc_air = 100; % [kg/s] Mass airflow during charge/discharge
mdotd_air = 20; % [kg/s] Mass airflow during charge/discharge
time=24*3600; %[sec] Maximum duration of charge/discharge
Tinit = 20+273.15; %[K] Initial temperature of the vessel
Tin = 300; %[K] Temperature of the air coming in the vessel

m_0 = P_prime*V_storage/(R_air*Tinit);


function [


%%% Simulation
steps=300;
delta_t=time/steps; %[sec] time step
Time=[0:delta_t:time];
T_charge=zeros(1,steps);
T_discharge=zeros(1,steps);
m_charge=zeros(1,steps);
m_discharge=zeros(1,steps);
P_charge=zeros(1,steps);
P_discharge=zeros(1,steps);



% Phase1: Charge
m_charge(1,1)=m_0;
T_charge(1,1)=m_0/m_charge(1,1)*Tinit;
P_charge(1,1)=P_prime;
i=1;
while (P_charge(1,i)<=P_storage)
    i=i+1;
    m_charge(1,i)=m_0+mdotc_air*Time(i);
    T_charge(1,i)=m_0/m_charge(1,i)*Tinit+mdotc_air*gamma_air*Tin/m_charge(1,i)*Time(i);
    P_charge(1,i)=P_prime + mdotc_air*gamma_air*R_air*Tin/V_storage*Time(i);
end
steps_charge=i;

m_max=max(m_charge);
T_max=max(T_charge);

% Phase2: Discharge
m_discharge(1,1)=m_max;
T_discharge(1,1)=T_max;
P_discharge(1,1)=m_discharge(1,1)*R_air*T_discharge(1,1)/V_storage;
i=1;
while P_discharge(1,i)>P_prime
    i=i+1;
    m_discharge(1,i)=m_max-mdotd_air*Time(i);
    T_discharge(1,i)=T_max*(1-mdotd_air/m_max*Time(i))^(gamma_air+1);
    P_discharge(1,i)=m_discharge(1,i)*R_air*T_discharge(1,i)/V_storage;
end
steps_discharge=i;
    






    
    
