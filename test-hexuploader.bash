#!/usr/bin/env bash
# Test script for HexUploader.py
# Written by Julian

echo "Test: no args"
echo
python3 HexUploader.py
echo

echo "Test: invalid subcommand"
echo
python3 HexUploader.py askdjfnjk
echo

echo "Test: listports no args"
echo
python3 HexUploader.py listports
echo

echo "Test: read no args"
echo
python3 HexUploader.py read
echo

echo "Test: send no args"
echo
python3 HexUploader.py send
echo

echo "Test: upload no args"
echo
python3 HexUploader.py upload
echo

echo "Test: read with invalid port"
echo
python3 HexUploader.py read -p sfjkbfkjbjk
echo

echo "Done."
