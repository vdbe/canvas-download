#!/usr/bin/env bash

PYTHON_DIR="src/lib/ui"
UI_DIR="ui"

DIR="$(dirname $(realpath $0))"

mkdir -p "${DIR}/${PYTHON_DIR}"
mkdir -p "${DIR}/${UI_DIR}"
find "${DIR}/${PYTHON_DIR}" -type f -name '*.py' -delete
find "${DIR}/${PYTHON_DIR}" -empty -type d -delete

echo "Start compiling UI files."

for file in `find "${DIR}/${UI_DIR}" -type f -name "*.ui" -printf '%P\n'`;
    do
        echo "Compiling ${file#/*}"
        [[ "$file" == */* ]] && mkdir -p "${DIR}/${PYTHON_DIR}/${file%/*}"
        pyuic6 "${DIR}/${UI_DIR}/${file#/*}" -o "${DIR}/${PYTHON_DIR}/${file%.*}.py"
done;

echo "Done."
