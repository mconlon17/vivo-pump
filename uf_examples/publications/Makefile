# Helper file for invoking the pump code
#
# Note: Before running the tasks please verify that your include
#	path contains the root vivo-pump folder.
#
# @author Andrei Sura
#
# Learning resources:
#	http://www.w3.org/TR/xpath-functions/#regex-syntax
#	http://www.cray.com/blog/equality-inequality-sparql/
#	http://www.cray.com/blog/dont-use-hammer-screw-nail-alternatives-regex-sparql/


CONFIG_DIR := config
FILTERS_DIR := filters
IN_DIR := data_in
OUT_DIR := data_out

# IN_FILE := $(IN_DIR)/tr_07_03_2015_wk_fin.bib
# IN_FILE := $(IN_DIR)/tr_6_mon_1_500.bib_full
# IN_FILE := $(IN_DIR)/tr_6_mon_1_500.bib
IN_FILE := data_2_test/test_pub_data.bib

OUT_FILE_PUBLISHERS := $(OUT_DIR)/publisher_update_data.txt
OUT_FILE_JOURNALS   := $(OUT_DIR)/journal_update_data.txt
OUT_FILE_AUTHOR     := $(OUT_DIR)/author_update_data.txt
OUT_FILE_PUBLICATION:= $(OUT_DIR)/pub_update_data.txt
OUT_FILE_CORRESPONDING:= $(OUT_DIR)/corresponding_update_data.txt

CONFIG_FILE_PUBLISHERS   := $(CONFIG_DIR)/sv_publishers.cfg
CONFIG_FILE_JOURNALS     := $(CONFIG_DIR)/sv_journals.cfg
CONFIG_FILE_AUTHORS      := $(CONFIG_DIR)/sv_authors.cfg
CONFIG_FILE_PUBLICATIONS := $(CONFIG_DIR)/sv_pubs.cfg
CONFIG_FILE_CORRESPONDING := $(CONFIG_DIR)/sv_corresponding.cfg

# === API config ===
API_EMAIL := new_admin@vivo.ufl.edu
API_PASSWORD := Password1

ENDPOINT_READ := 'https://dev.vivo.ufl.edu/vivo/api/sparqlQuery'
ENDPOINT_UPDATE := 'https://dev.vivo.ufl.edu/vivo/api/sparqlUpdate'

UPDATE_FILE_PUBLISHER   := data_2_test/add_publisher.rdf
UPDATE_FILE_JOURNAL     := data_2_test/add_journal.rdf
UPDATE_FILE_AUTHOR      := data_2_test/add_author.rdf
UPDATE_FILE_PUBLICATION := data_2_test/add_publication.rdf

READ_FILE_PUBLISHER     := data_2_test/read_publisher.rq
READ_FILE_JOURNAL       := data_2_test/read_journal.rq
READ_FILE_AUTHOR        := data_2_test/read_author.rq
READ_FILE_PUBLICATION   := data_2_test/read_publication.rq

DO_UPDATE := curl -d 'email=$(API_EMAIL)' -d 'password=$(API_PASSWORD)' $(ENDPOINT_UPDATE)
DO_READ := curl -d 'email=$(API_EMAIL)' -d 'password=$(API_PASSWORD)' $(ENDPOINT_READ)

help:
	@echo ""
	@echo "Available tasks: "
	@echo "  copy_example_files : Copy example files (safe to modify)"
	@echo "  == 1"
	@echo "  prep_publishers    : Prepare the publishers input file"
	@echo "  pump_publishers    : Generate the rdf add/sub files"
	@echo "  == 2"
	@echo "  prep_journals      : Prepare the journals input file"
	@echo "  pump_journals      : Generate the rdf add/sub files"
	@echo "  == 3"
	@echo "  prep_authors       : Prepare the authors input file"
	@echo "  pump_authors       : Generate the rdf add/sub files"
	@echo "  == 4"
	@echo "  prep_pubs          : Prepare the publications input file"
	@echo "  pump_pubs          : Generate the rdf add/sub files"
	@echo "  == 5"
	@echo "  prep_corresponding          : Prepare the corresponding author input file"
	@echo "  pump_corresponding          : Generate the rdf add/sub files"
	@echo ""
	@echo "  == Test insert data:"
	@echo "  test_insert_publisher  : Run sparql query from $(UPDATE_FILE_PUBLISHER)"
	@echo "  test_insert_journal    : Run sparql query from $(UPDATE_FILE_JOURNAL)"
	@echo "  test_insert_author     : Run sparql query from $(UPDATE_FILE_AUTHOR)"
	@echo "  test_insert_publication: Run sparql query from $(UPDATE_FILE_PUBLICATION)"
	@echo "  test_insert_all        : Run all tasks for inserting a new publication"
	@echo ""
	@echo "  == Testing read data:"
	@echo "  test_read_publisher    : Run sparql query from $(READ_FILE_PUBLISHER)"
	@echo "  test_read_journal      : Run sparql query from $(READ_FILE_JOURNAL)"
	@echo "  test_read_author       : Run sparql query from $(READ_FILE_AUTHOR)"
	@echo "  test_read_publication  : Run sparql query from $(READ_FILE_PUBLICATION)"
	@echo ""


copy_example_files:
	mkdir config data_in data_out
	cp config_example/* config
	cp data_in_example/* data_in
	cp data_out_example/* data_out

# === STEP 1
prep_publishers:
	cat $(IN_FILE) \
		| python $(FILTERS_DIR)/bib2csv_filter.py \
		| python $(FILTERS_DIR)/publisher_columns_filter.py \
		| python $(FILTERS_DIR)/publisher_name_filter.py \
		| python $(FILTERS_DIR)/unique_name_filter.py \
		| python $(FILTERS_DIR)/publisher_match_filter.py -c $(CONFIG_FILE_PUBLISHERS) \
		> $(OUT_FILE_PUBLISHERS)
	@echo "\nSee: $(OUT_FILE_PUBLISHERS)"
pump_publishers:
	python ../../sv.py \
		-a update \
		-d publisher_def.json \
		-c $(CONFIG_FILE_PUBLISHERS) \
		-s $(OUT_FILE_PUBLISHERS)


# === STEP 2
prep_journals:
	cat $(IN_FILE) \
		| python filters/bib2csv_filter.py \
		| python filters/journal_columns_filter.py \
		| python filters/unique_issn_filter.py \
		| python filters/journal_match_filter.py -c $(CONFIG_FILE_JOURNALS) \
		> $(OUT_FILE_JOURNALS)
	@echo "\nSee: $(OUT_FILE_JOURNALS)"
pump_journals:
	python ../../sv.py \
		-a update \
		-c $(CONFIG_FILE_JOURNALS) \
		-d journal_def.json \
		-s $(OUT_FILE_JOURNALS)


# === STEP 3
prep_authors:
	cat $(IN_FILE) \
		| python filters/bib2csv_filter.py \
		| python filters/author_prep_filter.py \
		| python filters/author_match_filter.py \
		> $(OUT_FILE_AUTHOR)
	@echo "\nSee: $(OUT_FILE_AUTHOR)"
pump_authors:
	@# TODO: fix the code to allow execution from a different folder
	@# <http://vivo.ufl.edu/individual/n1522>		 "Brenner, Mark" .
	@# <http://vivo.ufl.edu/individual/n45000>		 "Staud, Roland" .
	@# <http://vivo.ufl.edu/individual/n9190102923> "Mackman, Nigel" .
	@# <http://vivo.ufl.edu/individual/n3840747597> "Baylis, Chris" .
	@# <http://vivo.ufl.edu/individual/n5605>		 "Sjoberg, Laura E" .
	@# <http://vivo.ufl.edu/individual/n7282217>	 "Tong, Fan" .
	@# Summary:
	@#	921 rows input
	@#	11368 triples to add 59 triples to sub
	@#	time: real 49m20.295s
	python ../../sv.py \
		-d author_def.json \
		-c config/sv_authors.cfg \
		-s data_out/author_update_data.txt
	@echo "\nSee: author_add.rdf and author_sub.rdf"


# === STEP 4
prep_pubs:
	@# | python filters/pubmed_match_filter.py
	cat $(IN_FILE) \
		| python filters/bib2csv_filter.py \
		| python filters/pub_columns_filter.py \
		| python filters/pub_match_filter.py -c $(CONFIG_FILE_PUBLICATIONS) \
		| python filters/pub_author_match_filter.py -c $(CONFIG_FILE_PUBLICATIONS) \
		> $(OUT_FILE_PUBLICATION)
	@echo "\nSee: $(OUT_FILE_PUBLICATION)"
pump_pubs:
	python ../../sv.py \
		-c config/sv_pubs.cfg \
		-s data_out/pub_update_data.txt

# === STEP 5
prep_corresponding:
	@# | python filters/pubmed_match_filter.py
	cat $(IN_FILE) \
		| python filters/bib2csv_filter.py \
		| python filters/correspondence_columns_filter.py \
		| python filters/correspondence_match_filter.py \
		> $(OUT_FILE_CORRESPONDING)
	@echo "\nSee: $(OUT_FILE_CORRESPONDING)"
pump_corresponding:
	python ../../sv.py \
		-c config/sv_corresponding.cfg \
		-s data_out/corresponding_update_data.txt \
		-d corresponding_def.json

# === Testing tasks
test_find_persons:
	curl -d 'email=new_admin@vivo.ufl.edu' \
		-d 'password=$(API_PASSWORD)' \
		-d 'query=PREFIX foaf:<http://xmlns.com/foaf/0.1/> PREFIX obo:<http://purl.obolibrary.org/obo/> PREFIX vcard:<http://www.w3.org/2006/vcard/ns#> SELECT ?person_uri ?fname ?lname ?mname WHERE { ?person_uri a foaf:Person . ?person_uri obo:ARG_2000028 ?contact_info . ?contact_info vcard:hasName ?name . ?name vcard:familyName ?lname . OPTIONAL { ?name vcard:givenName ?fname . }OPTIONAL { ?name vcard:middleName ?mname . }} LIMIT 10' \
		-H 'Accept: text/csv' 'https://dev.vivo.ufl.edu/vivo/api/sparqlQuery'


test_find_publications:
	curl -d 'email=new_admin@vivo.ufl.edu' \
		-d 'password=$(API_PASSWORD)' \
		-d 'query=PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX core:<http://vivoweb.org/ontology/core#> SELECT ?uri ?label WHERE {  ?uri a core:InformationResource .  ?uri rdfs:label ?label  . FILTER regex(?label, "Safety Profile")} limit 10' \
		-H 'Accept: text/csv' 'https://dev.vivo.ufl.edu/vivo/api/sparqlQuery'


test_add_rdf:
	@# @TODO: fix later - needs a cookie to work
	curl -X POST http://dev.vivo.ufl.edu/uploadRDFForm -d rdfStream=@publisher_add_test.rdf -d mode=directAddABox -d language=N-TRIPLE -d submit=submit


test_insert_publisher:
	$(DO_UPDATE) -d @$(UPDATE_FILE_PUBLISHER)
test_read_publisher:
	$(DO_READ) -d @$(READ_FILE_PUBLISHER)

test_insert_journal:
	$(DO_UPDATE) -d @$(UPDATE_FILE_JOURNAL)
test_read_journal:
	$(DO_READ) -d @$(READ_FILE_JOURNAL)

test_insert_author:
	$(DO_UPDATE) -d @$(UPDATE_FILE_AUTHOR)
test_read_author:
	$(DO_READ) -d @$(READ_FILE_AUTHOR)

test_insert_publication:
	$(DO_UPDATE) -d @$(UPDATE_FILE_PUBLICATION)
test_read_publication:
	$(DO_READ) -d @$(READ_FILE_PUBLICATION)



test_insert_all:
	@# adds 4 pieces of data: publisher, journal, author, publication
	make test_insert_publisher
	make test_insert_journal
	make test_insert_author
	make test_insert_publication

test_delete_all:
	echo "todo"
