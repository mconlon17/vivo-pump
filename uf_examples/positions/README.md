# UF Position Update

Given a file of current positions at UF,  add, update and close positions for people at UF.
 
## Method

Use filters to transform the position_data.csv file as provided by UF to position_update_data.txt as input
to the pump.  The pump uses the data to make the appropriate add, update and close outs in VIVO.

## Filters

1. salary_admin_filter.py limits the data to those salary_admin_plans in salary_plan_enum.txt.  Only these
positions will  be put in VIVO
1. position_exception_filter.py remove positions whose JOBCODE_DESCRIPTIONS are in position_exceptions_data.txt
1. manage_columns_filter adds, removes and renames columns
1. merge_filter looks up each position in VIVO.  Found positions will be updated.  New positions will be added
1. null_value_filter replaces all text values of NULL with text values of ''

    cat position_data_small.csv | python salary_plan_filter.py | python position_exception_filter.py | 
    python manage_columns_filter.py | python merge_filter.py | 
    python null_value_filter.py > position_update_data_small.txt 

## Data

Six data fields are needed:

1. ufid
1. deptid
1. start
1. end
1. description
1. hr job title -- un edited description.  This is kept in a uf extension.  It is used as a primary key to
match positions data in the source to positions in vivo

