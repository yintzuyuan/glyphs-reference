# Glyphs 3 Language Codes

## Supported Locales

| Code | Language | Native Name |
|------|----------|-------------|
| `en` | English | English |
| `de` | German | Deutsch |
| `fr` | French | Français |
| `es` | Spanish | Español |
| `it` | Italian | Italiano |
| `pt` | Portuguese | Português |
| `ru` | Russian | Русский |
| `cs` | Czech | Čeština |
| `zh-Hant` | Traditional Chinese | 繁體中文 |
| `zh-Hans` | Simplified Chinese | 简体中文 |
| `ja` | Japanese | 日本語 |
| `ko` | Korean | 한국어 |
| `ar` | Arabic | العربية |
| `tr` | Turkish | Türkçe |

## Search Paths

### Main Application
```
/Applications/Glyphs 3.app/Contents/Resources/{LANG}.lproj/
```

### GlyphsCore Framework
```
/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Resources/{LANG}.lproj/
```

### Built-in Plugins
```
/Applications/Glyphs 3.app/Contents/PlugIns/{PLUGIN}/Contents/Resources/{LANG}.lproj/
```

## Quick Commands

```bash
# List available locales
ls -1 "/Applications/Glyphs 3.app/Contents/Resources/" | grep lproj | sed 's/.lproj//'

# Check if locale exists
ls "/Applications/Glyphs 3.app/Contents/Resources/zh-Hant.lproj/" 2>/dev/null && echo "exists"
```
