import os
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from worker.config import settings
from worker.tools.base import BaseTool, ToolResult

class FileSearchTool(BaseTool):
    name = "file_search"
    description = "Searches the document repository for vendor invoices and identifies candidate or latest files."

    async def execute(self, vendor_name: Optional[str] = None, find_latest: bool = True) -> ToolResult:
        try:
            invoices_dir = settings.INVOICES_DIR
            if not os.path.exists(invoices_dir):
                return ToolResult(
                    success=False,
                    output=f"Invoices directory does not exist: {invoices_dir}",
                    error="DIRECTORY_NOT_FOUND"
                )

            all_files = os.listdir(invoices_dir)
            matched_files = []

            clean_vendor = re.sub(r'[^a-zA-Z0-9]', '', vendor_name.lower()) if vendor_name else ""

            for filename in all_files:
                if not (filename.endswith(".pdf") or filename.endswith(".txt")):
                    continue

                clean_fname = re.sub(r'[^a-zA-Z0-9]', '', filename.lower())
                
                # Check vendor match
                if not clean_vendor or (clean_vendor in clean_fname):
                    filepath = os.path.join(invoices_dir, filename)
                    stat = os.stat(filepath)
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    
                    # Score priority: filenames with "latest" rank higher
                    score = 100 if "latest" in filename.lower() else 50
                    
                    matched_files.append({
                        "filename": filename,
                        "filepath": filepath,
                        "size_bytes": stat.st_size,
                        "modified_at": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                        "priority_score": score
                    })

            if not matched_files:
                return ToolResult(
                    success=False,
                    output=f"No invoice files found matching vendor '{vendor_name}' in {invoices_dir}.",
                    error="NO_FILES_FOUND"
                )

            # Sort by priority score first, then by modified timestamp descending
            matched_files.sort(key=lambda x: (x["priority_score"], x["modified_at"]), reverse=True)

            if find_latest:
                latest = matched_files[0]
                return ToolResult(
                    success=True,
                    output=f"Located latest invoice for '{vendor_name}': {latest['filename']} (Path: {latest['filepath']})",
                    data={
                        "latest_file": latest,
                        "all_matches": matched_files,
                        "count": len(matched_files)
                    }
                )

            return ToolResult(
                success=True,
                output=f"Found {len(matched_files)} matching files for '{vendor_name}'.",
                data={"matches": matched_files, "count": len(matched_files)}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Failed to search invoice files: {str(e)}",
                error=str(e)
            )
