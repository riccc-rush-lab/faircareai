# PDF Generation Setup Guide

## Simple 2-Step Setup (All Platforms)

FairCareAI uses Playwright for PDF generation. Setup is identical on macOS, Windows, and Linux!

### Step 1: Install Python Package
```bash
pip install playwright
```

### Step 2: Install Browser
```bash
python -m playwright install chromium
```

**That's it!** ✅ Works everywhere without system dependencies!

---

## Usage

Generate PDFs from your audit results:

```python
from faircareai import FairCareAudit

# Run audit
audit = FairCareAudit(data=df, pred_col="prob", target_col="outcome")
audit.add_sensitive_attribute(name="race", column="race", reference="White")
results = audit.run()

# Generate PDF reports
results.to_governance_pdf("governance_report.pdf")  # Streamlined 3-5 page report
results.to_pdf("technical_report.pdf")              # Comprehensive technical report
results.to_html("interactive_report.html")           # Interactive web report
```

---

## What You Get

### Governance PDF (3-5 pages)
- **File Size**: ~460 KB (with interactive charts)
- **Charts**: 12 high-quality visualizations (4 overall + 8 subgroup)
- **Content**: Executive summary, key metrics, plain language findings
- **Audience**: Healthcare leadership, governance committees

### Technical PDF (Comprehensive)
- **File Size**: ~210 KB
- **Charts**: Full suite of performance and fairness visualizations
- **Content**: Detailed statistical analysis, confidence intervals, metrics
- **Audience**: Data scientists, statisticians, technical teams

### HTML Report (Interactive)
- **File Size**: ~56 KB
- **Charts**: 12 interactive Plotly charts with zoom/pan/hover
- **Features**: No PDF conversion - pure web interface
- **Use Case**: Interactive exploration, presentations, web dashboards

---

## Platform-Specific Notes

### macOS ✅
```bash
pip install playwright
python -m playwright install chromium
```
Works on both Apple Silicon and Intel Macs!

### Windows ✅
```bash
pip install playwright
python -m playwright install chromium
```
No GTK3 runtime needed!

### Linux ✅
```bash
pip install playwright
python -m playwright install chromium
```
No system packages required!

### Docker ✅
```dockerfile
FROM python:3.12-slim

# Install Playwright
RUN pip install playwright

# Install Chromium browser
RUN python -m playwright install-deps chromium
RUN python -m playwright install chromium

# Install your package
RUN pip install "faircare[export]"

WORKDIR /app
```

---

## Troubleshooting

### Error: "Executable doesn't exist at /path/to/chromium"

**Solution**: Install the Chromium browser
```bash
python -m playwright install chromium
```

### Error: "ImportError: playwright"

**Solution**: Install Playwright package
```bash
pip install playwright
```

### Charts appear blank in PDF

**Cause**: Network timeout loading Plotly.js (rare on slow connections)

**Solution**: Ensure Chromium is fully installed and retry:
```bash
python -m playwright install chromium
```
If the issue persists, [open a GitHub issue](https://github.com/riccc-rush-lab/faircareai/issues) with your platform and Python version.

---

## Why Playwright?

### Before (WeasyPrint)
❌ **macOS**: Requires Homebrew + 4 system libraries + environment variables
❌ **Windows**: Requires GTK3 runtime installer + PATH configuration
❌ **Linux**: Requires system packages via apt/dnf/pacman
❌ **Charts**: Must convert Plotly to static SVG (complexity + quality loss)
❌ **Setup Time**: 10-30 minutes per platform
❌ **Support**: Platform-specific debugging nightmares

### After (Playwright)
✅ **All Platforms**: Same 2 commands everywhere!
✅ **Charts**: Native JavaScript rendering = perfect quality
✅ **Setup Time**: 2 minutes (mostly download time)
✅ **Support**: Works identically on all systems
✅ **Size**: ~200MB one-time browser download (vs managing system libs)

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Chromium Download | 1-2 min | One-time setup |
| PDF Generation | 3-5 sec | Per report |
| HTML Generation | <1 sec | Instant |

---

## Advanced Usage

### Custom PDF Options

Playwright supports custom margins, page size, and other PDF options. These are not yet exposed in the public API — [open an issue](https://github.com/riccc-rush-lab/faircareai/issues) if you need them.

### Headless vs Headed

Playwright runs in headless mode by default (no visible browser window). This is perfect for:
- Server environments
- CI/CD pipelines
- Batch processing
- Docker containers

---

## Package Installation

### Minimal (no PDF export)
```bash
pip install faircareai
```

### With PDF Export
```bash
pip install "faircareai[export]"  # Includes Playwright
python -m playwright install chromium
```

### Full Installation (PDF + PowerPoint)
```bash
pip install "faircareai[export]"
python -m playwright install chromium
```

---

## Comparison: WeasyPrint vs Playwright

| Feature | WeasyPrint | Playwright |
|---------|-----------|------------|
| **Setup (macOS)** | Homebrew + 4 libs + env vars | `pip install` + browser |
| **Setup (Windows)** | GTK3 installer + PATH | `pip install` + browser |
| **Setup (Linux)** | System packages | `pip install` + browser |
| **JavaScript Support** | ❌ No | ✅ Yes |
| **Interactive Charts** | ❌ Must convert to SVG | ✅ Native rendering |
| **Cross-Platform** | ⚠️ Different each OS | ✅ Identical everywhere |
| **Maintenance** | ⚠️ System lib conflicts | ✅ Self-contained |
| **CI/CD Friendly** | ⚠️ Complex setup | ✅ Simple setup |
| **Docker Size** | ~500MB (with system libs) | ~200MB (Chromium only) |

**Winner**: Playwright 🏆

---

## Migration from WeasyPrint

If you were using an older version of FairCareAI with WeasyPrint:

### Uninstall WeasyPrint (Optional)
```bash
pip uninstall weasyprint
```

### Install Playwright
```bash
pip install playwright
python -m playwright install chromium
```

### API Unchanged
```python
# Your existing code works identically!
results.to_governance_pdf("report.pdf")
results.to_pdf("technical.pdf")
```

The API is **100% backward compatible**. Only the underlying engine changed.

---

## FAQ

**Q: Do I need to install Chromium every time I deploy?**
A: Yes, but it's automated: `python -m playwright install chromium`

**Q: Can I use Firefox or WebKit instead?**
A: Chromium is recommended for best PDF rendering. Contact support if you need alternatives.

**Q: Does this work in restricted environments without internet?**
A: Yes! Install Chromium once with internet, then works offline.

**Q: What's the browser cache size?**
A: ~200MB for Chromium. Located in `~/.cache/ms-playwright/`

**Q: Can I uninstall after generating PDFs?**
A: No - Chromium is needed each time you generate a PDF.

**Q: Does this open browser windows on my screen?**
A: No - runs headless (background) by default.

---

## Support

If you encounter issues:

1. **Check Playwright is installed**: `pip show playwright`
2. **Check Chromium is installed**: `python -m playwright install chromium`
3. **Try test script**: `python test_pdf_output.py`
4. **File an issue**: https://github.com/riccc-rush-lab/faircareai/issues

---

**Last Updated**: 2026-04-11
**Tested On**: macOS 15.3, Windows 11, Ubuntu 22.04
**Python**: 3.10+
**Status**: ✅ Production Ready
