#!/bin/bash
# Glyphs Term Search - Comprehensive localization search tool
# Searches .strings files and NIB files across all Glyphs 3 components
#
# Usage: ./search-glyphs-term.sh [OPTIONS] <term> <language>
#
# Options:
#   -n, --nib-only      Search only in NIB files
#   -s, --strings-only  Search only in .strings files
#   -a, --all-langs     Search across all languages (ignores language parameter)
#   -p, --plugins       Search plugins only
#   -f, --format FORMAT Output format: text (default), json, csv
#   -h, --help          Show this help message
#
# Examples:
#   ./search-glyphs-term.sh "Remove Overlap" "zh-Hant"
#   ./search-glyphs-term.sh --all-langs "Remove Overlap"
#   ./search-glyphs-term.sh --nib-only "Remove Overlap" "en"
#   ./search-glyphs-term.sh --format json "Filter" "ja"

set -e

# Default values
SEARCH_NIB=true
SEARCH_STRINGS=true
ALL_LANGS=false
PLUGINS_ONLY=false
FORMAT="text"

# Parse options
while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--nib-only)
      SEARCH_STRINGS=false
      shift
      ;;
    -s|--strings-only)
      SEARCH_NIB=false
      shift
      ;;
    -a|--all-langs)
      ALL_LANGS=true
      shift
      ;;
    -p|--plugins)
      PLUGINS_ONLY=true
      shift
      ;;
    -f|--format)
      FORMAT="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '2,20p' "$0" | sed 's/^# //'
      exit 0
      ;;
    -*)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

# Get positional arguments
TERM="$1"
LANG="$2"

# Validation
if [ -z "$TERM" ]; then
  echo "Error: Search term required"
  echo "Use --help for usage information"
  exit 1
fi

if [ "$ALL_LANGS" = false ] && [ -z "$LANG" ]; then
  echo "Error: Language code required (or use --all-langs)"
  echo "Use --help for usage information"
  exit 1
fi

# Check Glyphs 3 installation
if [ ! -d "/Applications/Glyphs 3.app" ]; then
  echo "Error: Glyphs 3 not found at /Applications/Glyphs 3.app"
  exit 1
fi

# Define search paths
GLYPHS_APP="/Applications/Glyphs 3.app"
BASE_RESOURCES="$GLYPHS_APP/Contents/Resources"
CORE_FRAMEWORK="$GLYPHS_APP/Contents/Frameworks/GlyphsCore.framework/Versions/A/Resources"
PLUGINS_DIR="$GLYPHS_APP/Contents/PlugIns"

# Determine languages to search
if [ "$ALL_LANGS" = true ]; then
  LANGS=($(ls "$BASE_RESOURCES" | grep lproj | sed 's/.lproj//'))
else
  LANGS=("$LANG")
fi

# Output functions
output_text_header() {
  echo "=========================================="
  echo "Glyphs 3 Localization Search Results"
  echo "=========================================="
  echo "Term: $TERM"
  echo "Languages: ${LANGS[*]}"
  echo ""
}

output_json_header() {
  echo "{"
  echo "  \"term\": \"$TERM\","
  echo "  \"languages\": [\"${LANGS[*]}\"],"
  echo "  \"results\": ["
}

output_csv_header() {
  echo "Language,Source,File,Key,Translation"
}

# Initialize output
case $FORMAT in
  json)
    output_json_header
    FIRST_RESULT=true
    ;;
  csv)
    output_csv_header
    ;;
  text)
    output_text_header
    ;;
  *)
    echo "Error: Invalid format '$FORMAT'. Use: text, json, or csv"
    exit 1
    ;;
esac

# Search function for .strings files
search_strings() {
  local LANG="$1"
  local SEARCH_PATH="$2"
  local SOURCE_NAME="$3"

  if [ ! -d "$SEARCH_PATH" ]; then
    return
  fi

  # Find .strings files containing the term
  local FILES=$(find "$SEARCH_PATH" -name "*.strings" -exec grep -l "$TERM" {} \; 2>/dev/null)

  if [ -z "$FILES" ]; then
    return
  fi

  # Process each file
  # Use while read to handle filenames with spaces
  while IFS= read -r FILE; do
    [[ -z "$FILE" ]] && continue
    local FILENAME=$(basename "$FILE")

    # Search for term in comments and get the next line (the translation)
    # Split into two steps to avoid pipeline issues with set -e
    local COMMENT_SEARCH
    COMMENT_SEARCH=$(grep -A 1 "/\* .*$TERM.* \*/" "$FILE" 2>/dev/null || true)

    local MATCHES
    MATCHES=$(echo "$COMMENT_SEARCH" | grep -v "^--$" || true)

    # Also search for term directly in key-value pairs
    local DIRECT_MATCHES
    DIRECT_MATCHES=$(grep "\".*$TERM.*\" = " "$FILE" 2>/dev/null || true)

    # Combine results and remove comments, keeping only key-value pairs
    local COMBINED
    COMBINED=$(printf "%s\n%s" "$MATCHES" "$DIRECT_MATCHES")
    local ALL_MATCHES
    ALL_MATCHES=$(echo "$COMBINED" | grep -E '^".*" = ' || true)

    if [ -n "$ALL_MATCHES" ]; then
      case $FORMAT in
        json)
          while IFS= read -r LINE; do
            # Skip empty lines
            if [[ -z "$LINE" ]]; then
              continue
            fi

            if [ "$FIRST_RESULT" = false ]; then
              echo ","
            fi
            FIRST_RESULT=false

            KEY=$(echo "$LINE" | sed -n 's/"\([^"]*\)" = .*/\1/p')
            VALUE=$(echo "$LINE" | sed -n 's/.*= "\([^"]*\)";.*/\1/p')

            echo -n "    {\"language\": \"$LANG\", \"source\": \"$SOURCE_NAME\", \"file\": \"$FILENAME\", \"key\": \"$KEY\", \"translation\": \"$VALUE\"}"
          done <<< "$ALL_MATCHES"
          ;;
        csv)
          while IFS= read -r LINE; do
            # Skip empty lines
            if [[ -z "$LINE" ]]; then
              continue
            fi

            KEY=$(echo "$LINE" | sed -n 's/"\([^"]*\)" = .*/\1/p')
            VALUE=$(echo "$LINE" | sed -n 's/.*= "\([^"]*\)";.*/\1/p')

            echo "\"$LANG\",\"$SOURCE_NAME\",\"$FILENAME\",\"$KEY\",\"$VALUE\""
          done <<< "$ALL_MATCHES"
          ;;
        text)
          echo "[$LANG] $SOURCE_NAME ($FILENAME):"
          echo "$ALL_MATCHES"
          echo ""
          ;;
      esac
    fi
  done <<< "$FILES"
}

# Search function for NIB files
search_nib() {
  local LANG="$1"

  local NIB_DIR="$BASE_RESOURCES/Base.lproj"
  if [ ! -d "$NIB_DIR" ]; then
    return
  fi

  local NIB_RESULTS=$(find "$NIB_DIR" -name "*.nib" -exec strings {} \; 2>/dev/null | grep -i "$TERM" || true)

  if [ -n "$NIB_RESULTS" ]; then
    case $FORMAT in
      json)
        while IFS= read -r LINE; do
          if [ "$FIRST_RESULT" = false ]; then
            echo ","
          fi
          FIRST_RESULT=false

          if [[ "$LINE" == *"^"* ]]; then
            KEY=$(echo "$LINE" | cut -d'^' -f1)
            VALUE=$(echo "$LINE" | cut -d'^' -f2)
          else
            KEY="(no key)"
            VALUE="$LINE"
          fi

          echo -n "    {\"language\": \"Base\", \"source\": \"NIB\", \"file\": \"(multiple)\", \"key\": \"$KEY\", \"translation\": \"$VALUE\"}"
        done <<< "$NIB_RESULTS"
        ;;
      csv)
        while IFS= read -r LINE; do
          if [[ "$LINE" == *"^"* ]]; then
            KEY=$(echo "$LINE" | cut -d'^' -f1)
            VALUE=$(echo "$LINE" | cut -d'^' -f2)
          else
            KEY="(no key)"
            VALUE="$LINE"
          fi

          echo "\"Base\",\"NIB\",\"(multiple)\",\"$KEY\",\"$VALUE\""
        done <<< "$NIB_RESULTS"
        ;;
      text)
        echo "[Base] NIB Files:"
        echo "$NIB_RESULTS"
        echo ""
        ;;
    esac
  fi
}

# Main search loop
for CURRENT_LANG in "${LANGS[@]}"; do
  if [ "$SEARCH_STRINGS" = true ] && [ "$PLUGINS_ONLY" = false ]; then
    # Search main app
    search_strings "$CURRENT_LANG" "$BASE_RESOURCES/$CURRENT_LANG.lproj" "Main App"

    # Search GlyphsCore framework
    search_strings "$CURRENT_LANG" "$CORE_FRAMEWORK/$CURRENT_LANG.lproj" "GlyphsCore"
  fi

  if [ "$SEARCH_STRINGS" = true ]; then
    # Search plugins
    for PLUGIN_PATH in "$PLUGINS_DIR"/*.glyph*; do
      if [ -d "$PLUGIN_PATH" ]; then
        PLUGIN_NAME=$(basename "$PLUGIN_PATH")
        PLUGIN_LPROJ="$PLUGIN_PATH/Contents/Resources/$CURRENT_LANG.lproj"
        search_strings "$CURRENT_LANG" "$PLUGIN_LPROJ" "Plugin: $PLUGIN_NAME"
      fi
    done
  fi
done

# Search NIB files (only for Base/en)
if [ "$SEARCH_NIB" = true ] && [ "$PLUGINS_ONLY" = false ]; then
  if [ "$ALL_LANGS" = true ] || [ "$LANG" = "en" ] || [ "$LANG" = "Base" ]; then
    search_nib "Base"
  fi
fi

# Output footer
case $FORMAT in
  json)
    echo ""
    echo "  ]"
    echo "}"
    ;;
  text)
    echo "=========================================="
    echo "Search Complete"
    echo "=========================================="
    ;;
esac
