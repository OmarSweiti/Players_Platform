# ADR-0020 — The local object store is Versity S3 Gateway

**Status:** Accepted · 29 September 2026 · **Requirements:** SR-DOC-001…006 · **Owner:** `0.2.1`

## Context
[ADR-0009](0009-object-storage.md) needs private, **versioned** S3-compatible storage. Uploads go to
quarantine through a presigned PUT. A clean file is promoted by a server-side copy of one exact version.
Downloads are presigned GETs pinned to that version. Plan step `0.2.1` chooses and pins the store that
development and the integration tests run against. The production provider remains OPEN (`1.10.1`).

## Evidence
Executed 29 September 2026 on arm64 (colima). The same probe ran against each candidate:

- bucket versioning on, and read back;
- distinct version ids;
- GET, HEAD and ranged GET by version;
- anonymous reads refused;
- presigned PUT, and a presigned GET pinned to a version;
- a server-side copy of one exact version;
- listing versions, and deleting one;
- optionally, an object-lock legal hold that blocks deletion.

| Candidate | Probe | Idle memory | Image | Notes |
|---|---|---|---|---|
| Versity S3 Gateway v1.8.0 | every check passed, legal hold included | 10 MiB | 93 MB | Apache-2.0; one binary; the health endpoint is a flag; configured by environment |
| SeaweedFS 4.47 | every check passed, legal hold included | 64 MiB | 693 MB | Apache-2.0; master, volume, filer and S3 processes; identities from a mounted file |
| RustFS 1.0.0 | every check passed, legal hold included | 27 MiB | 355 MB | Apache-2.0; 1.0 was released on 16 September 2026 |
| MinIO | not run | — | — | `minio/minio` returned "object not found" on Docker Hub, and its GitHub repository is archived (last push 24 April 2026) |

## Decision
Development and the integration tests run **Versity S3 Gateway**, pinned by digest (`v1.8.0` today):

- the posix backend on a named volume, with a separate versioning directory;
- the root credentials from `infra/.env`, development only;
- bound to 127.0.0.1.

`infra/objectstore/bootstrap.py` reruns the required checks on every `just up`, so an image bump that
loses a capability fails on the next `just up`, not in `0.8.x`.

## Alternatives rejected
- **SeaweedFS** passes too, at six times the memory and seven times the image, and runs four processes to
  do one job.
- **RustFS** passes too, but its 1.0 is thirteen days old.
- **MinIO** has no image to pin.
- **An S3 emulator without versioning** (Garage, s3proxy) cannot support ADR-0009 at all.

## Consequences
- The application uses the root credentials locally. Production uses a scoped identity, which the hosting
  decision provides.
- A version id here is the store's own opaque string, as in any S3 provider, so code must never parse one.
- Object lock is available for legal hold, but no step depends on it yet.

## Revisit when
The probe fails on a new release, Versity stops shipping images, or production's provider (`1.10.1`)
needs a behaviour this store does not reproduce.
