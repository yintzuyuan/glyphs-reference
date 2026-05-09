#!/bin/bash
# NIB Strings Extractor - Extract and process strings from Glyphs 3 NIB files
#
# Usage: ./extract-nib-strings.sh [OPTIONS]
#
# Options:
#   -t, --term TERM      Extract only strings matching TERM
#   -o, --output FILE    Output to FILE instead of stdout
#   -f, --format FORMAT  Output format: text (default), csv, json
#   -k, --keys-only      Extract only Interface Builder keys
#   -v, --values-only    Extract only string values (no keys)
#   -l, --lang LANG      Compare with translations in LANG
#   -h, --help           Show this help message
#
# Examples:
#   ./extract-nib-strings.sh
#   ./extract-nib-strings.sh --term "Remove Overlap"
#   ./extract-nib-strings.sh --format csv --output nib_strings.csv
#   ./extract-nib-strings.sh --lang zh-Hant --format json

set -e

# Default values
TERM=""
OUTPUT_FILE=""
FORMAT="text"
KEYS_ONLY=false
VALUES_ONLY=false
COMPARE_LANG=""

# Parse options
while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--term)
      TERM="$2"
      shift 2
      ;;
    -o|--output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    -f|--format)
      FORMAT="$2"
      shift 2
      ;;
    -k|--keys-only)
      KEYS_ONLY=true
      shift
      ;;
    -v|--values-only)
      VALUES_ONLY=true
      shift
      ;;
    -l|--lang)
      COMPARE_LANG="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '2,17p' "$0" | sed 's/^# //'
      exit 0
      ;;
    -*)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
    *)
      echo "Unexpected argument: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check Glyphs 3 installation
if [ ! -d "/Applications/Glyphs 3.app" ]; then
  echo "Error: Glyphs 3 not found at /Applications/Glyphs 3.app" >&2
  exit 1
fi

BASE_LPROJ="/Applications/Glyphs 3.app/Contents/Resources/Base.lproj"
RESOURCES_DIR="/Applications/Glyphs 3.app/Contents/Resources"

if [ ! -d "$BASE_LPROJ" ]; then
  echo "Error: Base.lproj not found" >&2
  exit 1
fi

# Setup output redirection
if [ -n "$OUTPUT_FILE" ]; then
  exec > "$OUTPUT_FILE"
fi

# Output headers
case $FORMAT in
  csv)
    if [ -n "$COMPARE_LANG" ]; then
      echo "NIB File,Key,English,Translation ($COMPARE_LANG)"
    else
      echo "NIB File,Key,Value"
    fi
    ;;
  json)
    echo "{"
    echo "  \"source\": \"Glyphs 3 NIB Files\","
    echo "  \"base_path\": \"$BASE_LPROJ\","
    if [ -n "$COMPARE_LANG" ]; then
      echo "  \"comparison_language\": \"$COMPARE_LANG\","
    fi
    echo "  \"strings\": ["
    FIRST_ENTRY=true
    ;;
  text)
    echo "=========================================="
    echo "Glyphs 3 NIB Strings Extraction"
    echo "=========================================="
    echo "Source: $BASE_LPROJ"
    if [ -n "$TERM" ]; then
      echo "Filter: $TERM"
    fi
    if [ -n "$COMPARE_LANG" ]; then
      echo "Comparing with: $COMPARE_LANG"
    fi
    echo ""
    ;;
esac

# Find translation for a key in target language
find_translation() {
  local KEY="$1"
  local LANG="$2"

  if [ -z "$LANG" ]; then
    echo ""
    return
  fi

  local LANG_DIR="$RESOURCES_DIR/$LANG.lproj"
  if [ ! -d "$LANG_DIR" ]; then
    echo "(language not available)"
    return
  fi

  local TRANSLATION=$(grep "\"$KEY\"" "$LANG_DIR"/*.strings 2>/dev/null | sed -n 's/.*= "\(.*\)";/\1/p' | head -1)

  if [ -z "$TRANSLATION" ]; then
    echo "(not translated)"
  else
    echo "$TRANSLATION"
  fi
}

# Process each NIB file
find "$BASE_LPROJ" -name "*.nib" -type d | sort | while read -r NIB_PATH; do
  NIB_NAME=$(basename "$NIB_PATH")

  # Extract strings from NIB
  if [ -n "$TERM" ]; then
    NIB_STRINGS=$(strings "$NIB_PATH" 2>/dev/null | grep -i "$TERM" | grep -v "^$" || true)
  else
    NIB_STRINGS=$(strings "$NIB_PATH" 2>/dev/null | grep -v "^$" | grep -v "^NS" || true)
  fi

  if [ -z "$NIB_STRINGS" ]; then
    continue
  fi

  # Process each string
  while IFS= read -r LINE; do
    if [ -z "$LINE" ]; then
      continue
    fi

    # Check if line contains key^value format
    if [[ "$LINE" == *"^"* ]]; then
      KEY=$(echo "$LINE" | cut -d'^' -f1)
      VALUE=$(echo "$LINE" | cut -d'^' -f2-)

      if [ "$KEYS_ONLY" = true ]; then
        OUTPUT="$KEY"
      elif [ "$VALUES_ONLY" = true ]; then
        OUTPUT="$VALUE"
      else
        OUTPUT="$KEY = $VALUE"
      fi
    else
      # No key, just value
      KEY="(no key)"
      VALUE="$LINE"

      if [ "$KEYS_ONLY" = true ]; then
        continue  # Skip entries without keys
      elif [ "$VALUES_ONLY" = true ]; then
        OUTPUT="$VALUE"
      else
        OUTPUT="$VALUE"
      fi
    fi

    # Output in requested format
    case $FORMAT in
      csv)
        if [ -n "$COMPARE_LANG" ]; then
          TRANSLATION=$(find_translation "$KEY" "$COMPARE_LANG")
          echo "\"$NIB_NAME\",\"$KEY\",\"$VALUE\",\"$TRANSLATION\""
        else
          echo "\"$NIB_NAME\",\"$KEY\",\"$VALUE\""
        fi
        ;;
      json)
        if [ "$FIRST_ENTRY" = false ]; then
          echo ","
        fi
        FIRST_ENTRY=false

        echo -n "    {\"nib\": \"$NIB_NAME\", \"key\": \"$KEY\", \"english\": \"$VALUE\""

        if [ -n "$COMPARE_LANG" ]; then
          TRANSLATION=$(find_translation "$KEY" "$COMPARE_LANG")
          echo -n ", \"translation\": \"$TRANSLATION\""
        fi

        echo -n "}"
        ;;
      text)
        if [ -n "$COMPARE_LANG" ]; then
          TRANSLATION=$(find_translation "$KEY" "$COMPARE_LANG")
          echo "[$NIB_NAME]"
          echo "  Key: $KEY"
          echo "  English: $VALUE"
          echo "  $COMPARE_LANG: $TRANSLATION"
          echo ""
        else
          echo "[$NIB_NAME] $OUTPUT"
        fi
        ;;
    esac
  done <<< "$NIB_STRINGS"
done

# Output footers
case $FORMAT in
  json)
    echo ""
    echo "  ]"
    echo "}"
    ;;
  text)
    echo "=========================================="
    echo "Extraction Complete"
    echo "=========================================="
    ;;
esac

# Notify about output file
if [ -n "$OUTPUT_FILE" ]; then
  echo "Output written to: $OUTPUT_FILE" >&2
fi
