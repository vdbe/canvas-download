UI_DIR=./ui
UI_SRC_DIR=./src/lib/ui

UI_FILES=$(shell find $(UI_DIR) -type f -name "*.ui")

.PHONY: structure designer clean ui docker

ui: structure
	./build-ui-files.bash

structure:
	mkdir -p $(UI_DIR) $(UI_SRC_DIR)

designer:
	@exec bash -c 'QT_QPA_PLATFORM=xcb pyqt6-tools designer &'

clean: structure
	find $(UI_SRC_DIR) -type f -name "*.py" -delete

docker:
	docker build -t canvas-download .

