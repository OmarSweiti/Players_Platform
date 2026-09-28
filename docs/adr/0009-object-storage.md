# ADR-0009 — Private objects: quarantine, scan, immutable versions

**Status:** Accepted · 28 September 2026 · **Requirements:** SR-DOC-001…006, SR-DB-008 ·
**Owners:** `0.8.1`–`0.8.5`, each domain's binding step

## Context
Files would go to the API's local disk under a caller-influenced path; eight columns store file URLs; the
`Document` table references its owner polymorphically, with no integrity. A presigned upload URL stays
valid for minutes and could replace an object after it was scanned.

## Decision
Private, versioned S3-compatible storage behind a port. Uploads go to a **quarantine** key through a
short-lived presigned PUT; completion checks size, magic bytes and name; ClamAV scans; a clean file is
**promoted by server-side copy to an immutable key**, recording its `sha256` and object `versionId`;
downloads are authorized, 60-second presigned GETs **pinned to that version**. `FileObject` and
`UploadSession` hold the metadata; each domain binds files with a typed, tenant-safe relation. No URL is
ever stored.

## Alternatives rejected
Local disk (does not survive a second instance; path handling); public buckets; scanning the upload key in
place (a replayed PUT could swap the bytes after the scan); proxying every download through the API
(bandwidth, for no gain over version pinning).

## Consequences
A worker job per upload; downloads need a READY, clean file; retention and legal hold act on versions.

## Revisit when
Immediate revocation of an issued download becomes a requirement (then proxy downloads for that class).
