#!/usr/bin/env bash
# Test script for HexUploader.py
# Written by Julian

# Commands to test
tests=(
	"python3 HexUploader.py" \
	"python3 HexUploader.py -h" \
	"python3 HexUploader.py invalid-subcommand" \
	"python3 HexUploader.py listports" \
	"python3 HexUploader.py read" \
	"python3 HexUploader.py upload" \
	"python3 HexUploader.py verify" \
	# TODO: add more tests
)

run_tests(){
	for test_command in "${tests[@]}"; do
		# Run test
		echo "Output: $test_command"
		echo "--------------------------------"
		$test_command
		echo "--------------------------------"
		echo
	done
}

run_tests

echo "Done."

