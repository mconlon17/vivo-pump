# Helper file for invoking the pump code
#
# Note: Before running the tasks please verify that your include
#	path contains the root vivo-pump folder
#
# @author Andrei Sura
#
# @TODO: add tasks for the remaining steps
#
CONFIG_DIR := config
FILTERS_DIR := filters
IN_DIR := data_in
OUT_DIR := data_out

IN_FILE_PUBLISHERS := $(IN_DIR)/tr_07_03_2015_wk_fin.bib
OUT_FILE_PUBLISHERS := $(OUT_DIR)/publisher_update_data.txt

CONFIG_FILE_PUBLISHERS		:= $(CONFIG_DIR)/sv_publishers.cfg
CONFIG_FILE_JOURNALS		:= $(CONFIG_DIR)/sv_journals.cfg
CONFIG_FILE_AUTHORS			:= $(CONFIG_DIR)/sv_authors.cfg
CONFIG_FILE_PUBLICATIONS	:= $(CONFIG_DIR)/sv_pubs.cfg


help:
	@echo ""
	@echo "Available tasks: "
	@echo "  prep_publishers    : Prepare the input file"
	@echo "  pump_publishers    : Pump the input file"
	@echo ""

prep_publishers:
	cat $(IN_FILE_PUBLISHERS) \
		| python $(FILTERS_DIR)/bib2csv_filter.py \
		| python $(FILTERS_DIR)/publisher_columns_filter.py \
		| python $(FILTERS_DIR)/unique_name_filter.py \
		| python $(FILTERS_DIR)/publisher_match_filter.py -c $(CONFIG_FILE_PUBLISHERS) \
		> $(OUT_FILE_PUBLISHERS)

pump_publishers:
	sv -a update \
		-d publisher_def.json \
		-c $(CONFIG_FILE_PUBLISHERS) \
		-s $(OUT_FILE_PUBLISHERS)

prep_journals:
	echo 'todo'
pump_journals:
	echo 'todo'

prep_authors:
	cat data_in/tr_07_03_2015_wk_fin.bib \
		| python filters/bib2csv_filter.py \
		| python filters/author_prep_filter.py \
		| python filters/author_match_filter.py \
		> data_out/author_update_data.txt

pump_authors:
	@# TODO: fix the code to allow execution from a different folder
	@# sv -a update
	python ../../sv.py \
		-d author_def.json \
		-c config/sv_authors.cfg \
		-s data_out/author_update_data.txt

prep_pubs:
	echo 'todo'
pump_pubs:
	echo 'todo'
