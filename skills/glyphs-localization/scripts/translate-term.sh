#!/bin/bash
# Glyphs UI Term Translator - Hub-and-Spoke Architecture
# Translates Glyphs 3.app UI terms between any supported languages via English hub
#
# Usage:
#   ./translate-term.sh <term>                    # Auto-translate to English
#   ./translate-term.sh <term> <target_locale>    # Translate to specific locale
#   ./translate-term.sh --rebuild                 # Rebuild cache
#   ./translate-term.sh --list-locales            # List available locales
#
# Examples:
#   ./translate-term.sh "取消"                    # → Cancel (zh-Hant → en)
#   ./translate-term.sh "Cancel" "zh-Hant"        # → 取消 (en → zh-Hant)
#   ./translate-term.sh "移除重疊" "ja"           # → Japanese (zh-Hant → en → ja)

set -euo pipefail

# === Configuration ===
GLYPHS_APP="/Applications/Glyphs 3.app"
CACHE_DIR="/tmp/glyphs-vocab-cache"
CACHE_VERSION="1"

# Three-tier search paths
MAIN_RESOURCES="$GLYPHS_APP/Contents/Resources"
FRAMEWORK_RESOURCES="$GLYPHS_APP/Contents/Frameworks/GlyphsCore.framework/Versions/A/Resources"
PLUGINS_DIR="$GLYPHS_APP/Contents/PlugIns"

# === Utility Functions ===
check_glyphs_installed() {
    if [[ ! -d "$GLYPHS_APP" ]]; then
        echo "error: Glyphs 3 not found at $GLYPHS_APP" >&2
        exit 1
    fi
}

list_available_locales() {
    ls "$MAIN_RESOURCES" 2>/dev/null | grep '\.lproj$' | sed 's/\.lproj$//' | grep -v '^Base$' | sort
}

# === Cache Management ===
get_cache_file() {
    local locale="$1"
    echo "$CACHE_DIR/forward_${locale}.txt"
}

get_reverse_cache() {
    echo "$CACHE_DIR/reverse_index.txt"
}

is_cache_valid() {
    local version_file="$CACHE_DIR/version"
    local reverse_cache
    reverse_cache=$(get_reverse_cache)

    [[ -f "$version_file" ]] && \
    [[ "$(cat "$version_file" 2>/dev/null)" == "$CACHE_VERSION" ]] && \
    [[ -f "$reverse_cache" ]]
}

# Parse a .strings file and output key<TAB>value pairs
parse_strings_file() {
    local file="$1"
    # Handle both "key" = "value"; and multiline formats
    sed -n 's/^[[:space:]]*"\([^"]*\)"[[:space:]]*=[[:space:]]*"\(.*\)";[[:space:]]*$/\1\t\2/p' "$file" 2>/dev/null || true
}

# Build forward index for a locale (key → value mapping)
build_forward_index() {
    local locale="$1"
    local cache_file
    cache_file=$(get_cache_file "$locale")

    : > "$cache_file"  # Clear file

    # 1. Main App .strings
    local main_lproj="$MAIN_RESOURCES/${locale}.lproj"
    if [[ -d "$main_lproj" ]]; then
        find "$main_lproj" -name "*.strings" -type f 2>/dev/null | while read -r f; do
            parse_strings_file "$f"
        done >> "$cache_file"
    fi

    # 2. Framework .strings
    local framework_lproj="$FRAMEWORK_RESOURCES/${locale}.lproj"
    if [[ -d "$framework_lproj" ]]; then
        find "$framework_lproj" -name "*.strings" -type f 2>/dev/null | while read -r f; do
            parse_strings_file "$f"
        done >> "$cache_file"
    fi

    # 3. Plugins .strings
    for plugin in "$PLUGINS_DIR"/*.glyph*; do
        [[ -d "$plugin" ]] || continue
        local plugin_lproj="$plugin/Contents/Resources/${locale}.lproj"
        if [[ -d "$plugin_lproj" ]]; then
            find "$plugin_lproj" -name "*.strings" -type f 2>/dev/null | while read -r f; do
                parse_strings_file "$f"
            done >> "$cache_file"
        fi
    done

    # 4. For English locale, supplement with NIB strings from Base.lproj
    if [[ "$locale" == "en" ]]; then
        local base_lproj="$MAIN_RESOURCES/Base.lproj"
        if [[ -d "$base_lproj" ]]; then
            # Extract NIB strings (format: key^value)
            # Use temporary file to avoid subshell issues with while loop
            local nib_temp="$CACHE_DIR/nib_temp.txt"
            find "$base_lproj" -name "*.nib" -type d 2>/dev/null | while read -r nib; do
                strings "$nib" 2>/dev/null | grep '\^' || true
            done > "$nib_temp"

            while IFS='^' read -r key value; do
                [[ -z "$key" ]] && continue
                # Only add if key not already in cache (avoid duplicates)
                if ! grep -q "^${key}	" "$cache_file" 2>/dev/null; then
                    printf '%s\t%s\n' "$key" "$value"
                fi
            done < "$nib_temp" >> "$cache_file"
            rm -f "$nib_temp"
        fi
    fi
}

# Build reverse index (value.lower → key<TAB>locale<TAB>en_value)
# English values have priority to ensure Hub-and-Spoke correctness
# For non-English locales, we store the corresponding English value (if same key exists)
build_reverse_index() {
    local reverse_cache
    reverse_cache=$(get_reverse_cache)
    local temp_file="$CACHE_DIR/reverse_temp.txt"
    local en_cache
    en_cache=$(get_cache_file "en")

    : > "$temp_file"  # Clear temp file

    # Build key → en_value mapping for quick lookup
    local en_map_file="$CACHE_DIR/en_key_map.txt"
    if [[ -f "$en_cache" ]]; then
        # For English entries, key and en_value are the same concept
        # Store: value_lower<TAB>key<TAB>en<TAB>value (en_value = value for English)
        while IFS=$'\t' read -r key value; do
            [[ -z "$value" ]] && continue
            local value_lower
            value_lower=$(echo "$value" | tr '[:upper:]' '[:lower:]')
            printf '%s\t%s\ten\t%s\n' "$value_lower" "$key" "$value"
        done < "$en_cache" >> "$temp_file"
        # Also create en key mapping
        cp "$en_cache" "$en_map_file"
    fi

    # Process other locales - add ALL entries with English value lookup
    for locale in $(list_available_locales); do
        [[ "$locale" == "en" ]] && continue

        local cache_file
        cache_file=$(get_cache_file "$locale")
        [[ -f "$cache_file" ]] || continue

        while IFS=$'\t' read -r key value; do
            [[ -z "$value" ]] && continue
            local value_lower
            value_lower=$(echo "$value" | tr '[:upper:]' '[:lower:]')
            # Look up English value for this key
            local en_value=""
            if [[ -f "$en_map_file" ]]; then
                en_value=$(grep "^${key}	" "$en_map_file" 2>/dev/null | head -1 | cut -f2 || true)
            fi
            # If no direct key match, use the key itself (might be an English term)
            [[ -z "$en_value" ]] && en_value="$key"
            printf '%s\t%s\t%s\t%s\n' "$value_lower" "$key" "$locale" "$en_value"
        done < "$cache_file" >> "$temp_file"
    done

    # Sort and deduplicate by first column, keeping first occurrence (English priority)
    sort -t$'\t' -k1,1 -s "$temp_file" | awk -F'\t' '!seen[$1]++' > "$reverse_cache"
    rm -f "$temp_file" "$en_map_file"
}

rebuild_cache() {
    echo "Building cache..." >&2
    mkdir -p "$CACHE_DIR"

    # Build forward indices for all locales
    for locale in $(list_available_locales); do
        echo "  Indexing $locale..." >&2
        build_forward_index "$locale"
    done

    # Build reverse index
    echo "  Building reverse index..." >&2
    build_reverse_index

    # Write version file
    echo "$CACHE_VERSION" > "$CACHE_DIR/version"

    local count
    count=$(wc -l < "$(get_reverse_cache)" | tr -d ' ')
    echo "Cache built: $count entries" >&2
}

ensure_cache() {
    if ! is_cache_valid; then
        rebuild_cache
    fi
}

# === Core Translation Functions ===

# Find English key for a term in any locale (reverse lookup)
# Returns: key<TAB>source_locale<TAB>en_value or empty if not found
find_english_key() {
    local term="$1"
    local term_lower
    term_lower=$(echo "$term" | tr '[:upper:]' '[:lower:]')

    local reverse_cache
    reverse_cache=$(get_reverse_cache)

    # Exact match first
    local result
    result=$(grep "^${term_lower}	" "$reverse_cache" 2>/dev/null | head -1)

    if [[ -n "$result" ]]; then
        # Output: key<TAB>locale<TAB>en_value
        echo "$result" | cut -f2,3,4
        return 0
    fi

    # Partial match (term contained in value)
    result=$(grep -i "${term}" "$reverse_cache" 2>/dev/null | head -1)
    if [[ -n "$result" ]]; then
        echo "$result" | cut -f2,3,4
        return 0
    fi

    return 1
}

# Get translation for a key in target locale
get_translation() {
    local key="$1"
    local locale="$2"

    local cache_file
    cache_file=$(get_cache_file "$locale")

    [[ -f "$cache_file" ]] || return 1

    grep "^${key}	" "$cache_file" 2>/dev/null | head -1 | cut -f2
}

# Main translation function (Hub-and-Spoke)
translate() {
    local term="$1"
    local target_locale="${2:-en}"

    # Step 1: Find English key via reverse index
    local key_info
    if key_info=$(find_english_key "$term"); then
        local key source_locale en_value
        key=$(echo "$key_info" | cut -f1)
        source_locale=$(echo "$key_info" | cut -f2)
        en_value=$(echo "$key_info" | cut -f3)

        # Step 2: Get translation in target locale
        # Try with the original key first, then with en_value as key
        local translation
        translation=$(get_translation "$key" "$target_locale") || true

        if [[ -z "$translation" ]] && [[ "$key" != "$en_value" ]]; then
            # Try using en_value as key (for locales that use English terms as keys)
            translation=$(get_translation "$en_value" "$target_locale") || true
        fi

        if [[ -n "$translation" ]]; then
            echo "key: $en_value"
            echo "source: $source_locale"
            echo "target: $target_locale"
            echo "translation: $translation"
            return 0
        else
            # Target locale has no translation, return English value
            echo "key: $en_value"
            echo "source: $source_locale"
            echo "target: $target_locale"
            echo "translation: $en_value"
            echo "note: no translation for $target_locale, showing English"
            return 0
        fi
    fi

    # Term not found - try treating it as an English key directly
    local direct_trans
    if direct_trans=$(get_translation "$term" "$target_locale"); then
        echo "key: $term"
        echo "source: en (key)"
        echo "target: $target_locale"
        echo "translation: $direct_trans"
        return 0
    fi

    # Not found
    echo "key: (not found)"
    echo "source: unknown"
    echo "target: $target_locale"
    echo "translation: $term"
    echo "note: term not in Glyphs vocabulary"
    return 1
}

# === Main ===
check_glyphs_installed

case "${1:-}" in
    --rebuild)
        rebuild_cache
        exit 0
        ;;
    --list-locales)
        list_available_locales
        exit 0
        ;;
    --help|-h)
        sed -n '2,14p' "$0" | sed 's/^# //'
        exit 0
        ;;
    "")
        echo "Usage: $0 <term> [target_locale]" >&2
        echo "       $0 --rebuild" >&2
        echo "       $0 --list-locales" >&2
        exit 1
        ;;
esac

ensure_cache

TERM="$1"
TARGET="${2:-en}"

translate "$TERM" "$TARGET"
