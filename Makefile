# Имя исходного файла (без .adoc)
DOC = doc
# Имя выходного файла (без .docx)
OUTNAME = output

# Пути
BUILD_DIR = out/docx
DOCX_FILE = $(BUILD_DIR)/$(OUTNAME).docx

# Эталонные YAML-файлы
GOLDEN_YAML_RP = tests/iconic/RP_structure.yaml
GOLDEN_YAML_PZ = tests/iconic/PZ_structure.yaml
GOLDEN_YAML_RA = tests/iconic/RA_structure.yaml
GOLDEN_YAML_MR = tests/iconic/MR_structure.yaml

# Сборка
build:
	bash scripts/build.sh $(DOC) $(OUTNAME)

# Пример команды для сборки документа: make build DOC=indexPZ OUTNAME=ПЗ

validate-rp: build
	python3 scripts/validate.py $(DOCX_FILE) $(GOLDEN_YAML_RP)

validate-pz: build
	python3 scripts/validate.py $(DOCX_FILE) $(GOLDEN_YAML_PZ)

validate-ra: build
	python3 scripts/validate.py $(DOCX_FILE) $(GOLDEN_YAML_RA)	

validate-mr: build
	python3 scripts/validate.py $(DOCX_FILE) $(GOLDEN_YAML_MR)	

# Пример команды для проверки документа: make validate-rp DOC=indexRP OUTNAME=РП
clean:
	rm -rf out/*
