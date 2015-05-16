# UF Position Update

Given a file of current positions at UF,  add, update and close positions for people at UF.
 
## Method

Use filters to transform the position_data.csv file as provided by UF to position_update_data.txt as input
to the pump.  The pump uses the data to make the appropriate add, update and close outs in VIVO.

## Filters

1. salary_admin_filter.py limits the data to those salary_admin_plans in salary_plan_enum.txt.  Only these
positions will  be put in VIVO.
1. manage_columns_filter adds, removes and renames columns
1. merge_filter looks up each position in VIVO.  Found positions will be updated.  New positions will be added.

cat position_data.csv | python salary_plan_filter.txt | python manage_columns_filter.py | 
python merge_filter.py > position_update_data.txt 

## Data

Six data fields are needed:

1. ufid
1. deptid
1. start
1. end
1. description
1. hr job title -- un edited description.  This is kept in a uf extension.  It is used as a primary key to
match positions data in the source to positions in vivo

