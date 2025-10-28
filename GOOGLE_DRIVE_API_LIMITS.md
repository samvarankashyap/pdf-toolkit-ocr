# Google Drive API Limits and Usage Guide

## Overview

This document explains Google Drive API quotas, limits, and best practices for OCR processing. Understanding these limits will help you use the PDF Toolkit effectively without hitting rate limits or quota errors.

---

## API Quotas and Limits

### Request Rate Limits

**Per-Minute Quotas (Most Important):**
- **12,000 queries per 60 seconds** (per project)
- **12,000 queries per 60 seconds per user** (per OAuth token)

**Daily Quotas:**
- **No daily limit** as long as you stay within per-minute quotas
- Effectively unlimited if you respect rate limits

**What this means for OCR processing:**
- You can process hundreds of documents per day
- The main constraint is the 12,000 requests per minute rate
- Each OCR operation involves multiple API calls (upload, export, delete)

---

### File Size and Upload Limits

**Upload Limits:**
- **Daily upload limit:** 750 GB per day per user
- **Maximum single file size:** 5 TB
- **Maximum file copy size:** 750 GB

**OCR-Specific Limits:**
- **Maximum OCR file size:** 2 MB per file (for direct OCR)
- **PDF pages processed:** First 10 pages only (for search/indexing)
- **Supported formats:** PDF, JPEG, PNG, GIF (2 MB max each)

**Important Notes:**
- If a file exceeds 2 MB, you may need to split it or reduce quality
- PDF Toolkit automatically chunks large PDFs (default: 10 pages per chunk)
- Each chunk should be under 2 MB for optimal OCR results

---

## Error Codes and Rate Limiting

### Common Error Responses

**403: User rate limit exceeded**
```
{
  "error": {
    "code": 403,
    "message": "User rate limit exceeded"
  }
}
```
- You've exceeded the 12,000 requests/minute quota
- Solution: Implement exponential backoff and retry

**429: Too many requests**
```
{
  "error": {
    "code": 429,
    "message": "Too many requests"
  }
}
```
- Backend rate limiting triggered
- Solution: Wait and retry with exponential backoff

**403: Daily limit exceeded**
```
{
  "error": {
    "code": 403,
    "message": "Daily limit exceeded"
  }
}
```
- Unlikely unless you've exceeded 750 GB uploads
- Solution: Wait 24 hours for quota reset

---

## OCR Processing Costs (API Calls)

### API Calls Per Document

**For a single PDF file OCR:**

1. **Upload (1 call)**
   - `files.create()` - Upload PDF to Google Drive

2. **Export OCR (1 call per chunk)**
   - `files.export()` - Export as Google Doc with OCR
   - For 100-page PDF with 10 pages/chunk = 10 export calls

3. **Download Text (1 call per chunk)**
   - `files.export()` - Export Google Doc as plain text
   - For 100-page PDF with 10 pages/chunk = 10 download calls

4. **Delete (1-2 calls per chunk)**
   - `files.delete()` - Remove temporary files
   - For 100-page PDF with 10 pages/chunk = 10-20 delete calls

**Total for 100-page PDF:**
- Upload: 1 call
- Create chunks: ~10 files
- Export to Google Docs: 10 calls
- Export as text: 10 calls
- Delete files: 20 calls
- **Total: ~41 API calls**

### Batch Processing Estimates

**How many documents can you process?**

Assuming average 50-page PDFs:
- API calls per document: ~21 calls
- Rate limit: 12,000 calls per minute
- **Theoretical max:** ~571 documents per minute
- **Practical limit:** ~200-300 documents per minute (with overhead)

**Daily processing capacity:**
- Minutes per day: 1,440
- Documents per minute: ~250
- **Daily capacity:** ~360,000 documents (50 pages each)

**Realistically:**
- With delays, retries, and processing time
- **Safe estimate:** 10,000-50,000 pages per day
- **Documents:** 200-1,000 documents per day (50 pages each)

---

## Best Practices

### 1. Optimize Chunk Size

**Default Settings:**
```python
PAGES_PER_CHUNK = 10  # Default in PDF Toolkit
```

**Recommendations:**
- **Small PDFs (< 50 pages):** Use larger chunks (15-20 pages)
- **Large PDFs (> 100 pages):** Stick with 10 pages per chunk
- **Image-heavy PDFs:** Use smaller chunks (5-8 pages) to stay under 2 MB

**Adjust chunk size:**
```bash
python pdf_toolkit.py ocr document.pdf --chunk-size 15
```

### 2. Implement Retry Logic

The tool should handle rate limits automatically, but if you encounter errors:

**Exponential Backoff Strategy:**
```python
import time

def retry_with_backoff(func, max_retries=5):
    for i in range(max_retries):
        try:
            return func()
        except HttpError as e:
            if e.resp.status in [403, 429]:
                wait_time = (2 ** i) + random.random()
                print(f"Rate limited. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")
```

### 3. Batch Processing Strategies

**For processing many documents:**

**Strategy 1: Sequential Processing**
```bash
# Process one at a time (safest)
python pdf_toolkit.py ocr-batch --dir ./documents
```

**Strategy 2: Rate-Limited Processing**
- Process in batches with delays
- Monitor API quota usage
- Add delays between batches if needed

**Strategy 3: Distributed Processing**
- Use multiple Google accounts (each has separate quota)
- Distribute documents across accounts
- Each account can process independently

### 4. Monitor Quota Usage

**Check your quota usage:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" → "Dashboard"
3. Select "Google Drive API"
4. View "Quotas & System Limits"

**Set up quota alerts:**
1. Go to "Monitoring" → "Alerting"
2. Create alert for Drive API quotas
3. Get notified before hitting limits

### 5. Optimize File Sizes

**Reduce API calls by optimizing PDFs:**

**Before OCR:**
```bash
# Convert to high-quality image PDF (reduces file size often)
python pdf_toolkit.py convert large.pdf -o optimized.pdf --dpi 200 --quality 85

# Then OCR the optimized version
python pdf_toolkit.py ocr optimized.pdf
```

**Benefits:**
- Image PDFs often have better OCR accuracy
- Compressed images reduce upload/download time
- Smaller files = faster processing

### 6. Clean Up Temporary Files

**The tool automatically cleans up, but you can disable for debugging:**

```bash
# Keep intermediate files for inspection
python pdf_toolkit.py ocr document.pdf --keep-chunks

# Default: automatically deletes chunks after processing
python pdf_toolkit.py ocr document.pdf
```

---

## Quota Management

### Free Tier vs Paid

**Free Tier (Default):**
- 12,000 requests per minute
- 750 GB uploads per day
- No cost for Drive API usage

**Requesting Higher Quotas:**
- Google may grant higher quotas for free
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Navigate to "APIs & Services" → "Quotas"
- Click "Edit Quotas" and request increase
- Provide justification for increase

**Note:** There's no charge for increased Drive API quotas

### Multiple Projects

**For very high volume:**
- Create multiple Google Cloud projects
- Each project has separate quotas
- Distribute load across projects
- Each project can process 12,000 req/min

---

## Practical Examples

### Example 1: Small Document (10 pages)

**Scenario:** OCR a 10-page PDF

**API Calls:**
- Upload: 1 call
- Export to Google Doc: 1 call
- Export as text: 1 call
- Delete: 2 calls
- **Total: 5 calls**

**Time estimate:** ~10-30 seconds

### Example 2: Medium Document (100 pages)

**Scenario:** OCR a 100-page PDF (10 pages per chunk)

**API Calls:**
- Upload chunks: 10 calls
- Export to Google Docs: 10 calls
- Export as text: 10 calls
- Delete: 20 calls
- **Total: 50 calls**

**Time estimate:** 3-5 minutes

### Example 3: Batch Processing (50 documents, 50 pages each)

**Scenario:** Batch OCR 50 PDFs (50 pages each)

**API Calls:**
- Calls per document: ~26 calls
- Total documents: 50
- **Total: 1,300 calls**

**Rate limit check:**
- 1,300 calls < 12,000/min ✅
- Can process entire batch in < 1 minute (API calls only)

**Actual time estimate:** 30-60 minutes (including processing time)

### Example 4: Large Batch (1,000 documents)

**Scenario:** Batch OCR 1,000 PDFs (50 pages each)

**API Calls:**
- Calls per document: ~26 calls
- Total documents: 1,000
- **Total: 26,000 calls**

**Rate limit management:**
- 26,000 calls / 12,000 per minute = 2.17 minutes minimum
- Add delays between batches
- Process in chunks of 400 documents

**Estimated time:** 10-20 hours (including processing time and delays)

---

## Troubleshooting

### Issue: Rate Limit Exceeded

**Symptoms:**
```
Error 403: User rate limit exceeded
```

**Solutions:**
1. **Add delays between operations:**
   ```python
   import time
   time.sleep(1)  # 1 second delay between documents
   ```

2. **Process fewer documents simultaneously**

3. **Request quota increase** (usually approved quickly)

### Issue: File Too Large for OCR

**Symptoms:**
```
Error: File exceeds 2 MB limit for OCR
```

**Solutions:**
1. **Reduce image quality:**
   ```bash
   python pdf_toolkit.py ocr document.pdf --dpi 150 --quality 75
   ```

2. **Increase chunk size** (fewer pages per chunk):
   ```bash
   python pdf_toolkit.py ocr document.pdf --chunk-size 5
   ```

3. **Compress PDF before OCR:**
   ```bash
   # Use external tool to compress PDF first
   ```

### Issue: Slow Processing

**Symptoms:**
- OCR takes very long
- Uploads/downloads are slow

**Solutions:**
1. **Check internet connection** (bandwidth matters)

2. **Optimize file sizes** (reduce DPI/quality)

3. **Use local caching** (avoid re-processing)

4. **Process during off-peak hours** (less network congestion)

### Issue: Daily Upload Limit

**Symptoms:**
```
Error 403: Daily upload limit exceeded (750 GB)
```

**Solutions:**
1. **Wait 24 hours** for quota reset

2. **Use multiple Google accounts** (each has 750 GB/day)

3. **Optimize file sizes** to reduce upload volume

4. **Process fewer documents** per day

---

## Monitoring and Logging

### Track Your Usage

**Add logging to your workflow:**

```python
import logging

logging.basicConfig(
    filename='ocr_usage.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Log each operation
logging.info(f"Processing: {filename} - Pages: {num_pages} - Chunks: {num_chunks}")
```

**Monitor quota in Google Cloud Console:**
1. Go to APIs & Services → Dashboard
2. Click "Google Drive API"
3. View "Quotas" tab
4. Check "Queries per 60 seconds per user"

### Estimate Before Processing

**Calculate before starting:**

```python
def estimate_api_calls(num_pages, pages_per_chunk=10):
    num_chunks = (num_pages + pages_per_chunk - 1) // pages_per_chunk
    upload_calls = num_chunks
    export_calls = num_chunks * 2  # To Google Docs + to text
    delete_calls = num_chunks * 2
    total_calls = upload_calls + export_calls + delete_calls
    return total_calls

# Example
pages = 100
calls = estimate_api_calls(pages)
print(f"Estimated API calls: {calls}")
# Output: Estimated API calls: 50
```

---

## Summary

### Key Takeaways

✅ **12,000 requests per minute** is the main limit
✅ **2 MB max file size** for OCR operations
✅ **750 GB daily upload limit** per account
✅ **No daily request limit** if you respect rate limits
✅ **Exponential backoff** for handling rate limits
✅ **Chunking large PDFs** helps stay within limits

### Recommended Settings

**For typical usage:**
```bash
python pdf_toolkit.py ocr document.pdf \
  --chunk-size 10 \
  --dpi 200 \
  --quality 90
```

**For high-volume batch:**
```bash
python pdf_toolkit.py ocr-batch \
  --dir ./documents \
  --chunk-size 10 \
  --dpi 150 \
  --quality 85
```

### When You Need More

**If you regularly hit limits:**
1. Request quota increase (free)
2. Use multiple Google accounts
3. Optimize chunk sizes and file sizes
4. Add delays between batches
5. Consider Google Cloud Vision API (different quotas)

---

## Additional Resources

- [Google Drive API Limits](https://developers.google.com/drive/api/guides/limits)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Drive API Reference](https://developers.google.com/drive/api/v3/reference)
- [Quota Management Guide](https://cloud.google.com/apis/docs/capping-api-usage)

---

**Need help?** Check the [README.md](README.md) for usage examples or [open an issue](https://github.com/samvarankashyap/pdf-toolkit-ocr/issues) on GitHub.
