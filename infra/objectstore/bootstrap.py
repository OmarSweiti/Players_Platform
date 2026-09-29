#!/usr/bin/env python3
"""Prepare the local object store, then prove it does what the storage port needs.

`just up` runs this after every service is healthy. It is idempotent:

1. the buckets `sadara` (development) and `sadara-test` (integration tests) exist,
   private, with versioning enabled (ADR-0009);
2. in a throwaway bucket, it proves each capability plan steps 0.8.1-0.8.4 rely on:
   distinct version ids, reads (GET, HEAD, ranged) pinned to a version, presigned PUT
   and GET, a server-side copy of one exact version, listing and deleting versions, and
   anonymous reads refused. Then it removes that bucket.

A store image that loses one of these fails here, on the next `just up`, not in 0.8.x.
Standard library only: requests are signed with AWS Signature Version 4 by hand.
"""
import datetime
import hashlib
import hmac
import http.client
import os
import sys
import urllib.parse
import uuid
import xml.etree.ElementTree as ET

REGION = "us-east-1"
BUCKETS = ("sadara", "sadara-test")
NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
VERSIONING_ON = (b'<VersioningConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
                 b"<Status>Enabled</Status></VersioningConfiguration>")


def settings():
    """infra/.env, which `just up` creates from infra/.env.example."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    values = {}
    with open(path, encoding="utf-8") as env:
        for line in env:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip()
    return values


def _q(text, safe="-_.~"):
    return urllib.parse.quote(str(text), safe=safe)


class Store:
    def __init__(self, host, access, secret):
        self.host, self.access, self.secret = host, access, secret

    def _signing_key(self, day):
        key = hmac.new(("AWS4" + self.secret).encode(), day.encode(), hashlib.sha256).digest()
        for part in (REGION, "s3", "aws4_request"):
            key = hmac.new(key, part.encode(), hashlib.sha256).digest()
        return key

    @staticmethod
    def _query(params):
        return "&".join("%s=%s" % (_q(k), _q(v)) for k, v in sorted(params.items()))

    def _send(self, method, target, headers=None, body=b""):
        conn = http.client.HTTPConnection(self.host, timeout=30)
        try:
            conn.request(method, target, body=body, headers=headers or {})
            response = conn.getresponse()
            return response.status, {k.lower(): v for k, v in response.getheaders()}, response.read()
        finally:
            conn.close()

    def call(self, method, path, params=None, headers=None, body=b""):
        """A request signed in its Authorization header."""
        params, headers = dict(params or {}), dict(headers or {})
        now = datetime.datetime.now(datetime.timezone.utc)
        stamp, day = now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y%m%d")
        uri, query = _q(path, safe="/-_.~"), self._query(params)
        digest = hashlib.sha256(body).hexdigest()
        headers.update({"host": self.host, "x-amz-date": stamp, "x-amz-content-sha256": digest})
        items = sorted((k.lower(), str(v).strip()) for k, v in headers.items())
        signed = ";".join(k for k, _ in items)
        canonical = "\n".join([method, uri, query, "".join("%s:%s\n" % kv for kv in items), signed, digest])
        scope = "%s/%s/s3/aws4_request" % (day, REGION)
        to_sign = "\n".join(["AWS4-HMAC-SHA256", stamp, scope, hashlib.sha256(canonical.encode()).hexdigest()])
        signature = hmac.new(self._signing_key(day), to_sign.encode(), hashlib.sha256).hexdigest()
        headers["Authorization"] = "AWS4-HMAC-SHA256 Credential=%s/%s, SignedHeaders=%s, Signature=%s" % (
            self.access, scope, signed, signature)
        return self._send(method, uri + ("?" + query if query else ""), headers, body)

    def presign(self, method, path, params=None, expires=60):
        """A URL signed in its query string, as the API will hand one to a browser."""
        params = dict(params or {})
        now = datetime.datetime.now(datetime.timezone.utc)
        stamp, day = now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y%m%d")
        scope = "%s/%s/s3/aws4_request" % (day, REGION)
        params.update({"X-Amz-Algorithm": "AWS4-HMAC-SHA256", "X-Amz-Credential": "%s/%s" % (self.access, scope),
                       "X-Amz-Date": stamp, "X-Amz-Expires": str(expires), "X-Amz-SignedHeaders": "host"})
        uri, query = _q(path, safe="/-_.~"), self._query(params)
        canonical = "\n".join([method, uri, query, "host:%s\n" % self.host, "host", "UNSIGNED-PAYLOAD"])
        to_sign = "\n".join(["AWS4-HMAC-SHA256", stamp, scope, hashlib.sha256(canonical.encode()).hexdigest()])
        signature = hmac.new(self._signing_key(day), to_sign.encode(), hashlib.sha256).hexdigest()
        return "%s?%s&X-Amz-Signature=%s" % (uri, query, signature)

    def anonymous(self, method, target, headers=None, body=b""):
        return self._send(method, target, headers, body)

    def ensure_versioned_bucket(self, bucket):
        status, _, body = self.call("PUT", "/" + bucket)
        if status not in (200, 409):  # 409: it already exists
            raise RuntimeError("cannot create bucket %s: HTTP %s %s" % (bucket, status, body[:200]))
        status, _, body = self.call("PUT", "/" + bucket, {"versioning": ""}, {"content-type": "application/xml"},
                                    VERSIONING_ON)
        if status != 200:
            raise RuntimeError("cannot enable versioning on %s: HTTP %s %s" % (bucket, status, body[:200]))

    def versioning_enabled(self, bucket):
        status, _, body = self.call("GET", "/" + bucket, {"versioning": ""})
        return status == 200 and b"<Status>Enabled</Status>" in body

    def remove_bucket(self, bucket):
        """Every version and delete marker, then the bucket itself."""
        status, _, body = self.call("GET", "/" + bucket, {"versions": ""})
        if status == 200:
            for entry in ET.fromstring(body):
                if entry.tag in (NS + "Version", NS + "DeleteMarker"):
                    self.call("DELETE", "/%s/%s" % (bucket, entry.findtext(NS + "Key")),
                              {"versionId": entry.findtext(NS + "VersionId")})
        self.call("DELETE", "/" + bucket)


def prove(store, bucket):
    """(name, passed, detail) for each capability, in a bucket this run owns."""
    results = []

    def check(name, passed, detail=""):
        results.append((name, bool(passed), detail))

    key = "tenants/probe/quarantine/" + uuid.uuid4().hex
    _, first, _ = store.call("PUT", "/%s/%s" % (bucket, key), body=b"version-one")
    _, second, _ = store.call("PUT", "/%s/%s" % (bucket, key), body=b"version-two")
    v1, v2 = first.get("x-amz-version-id"), second.get("x-amz-version-id")
    check("each PUT gets its own version id", v1 and v2 and v1 != v2 and "null" not in (v1, v2), (v1, v2))

    status, _, body = store.call("GET", "/%s/%s" % (bucket, key), {"versionId": v1})
    check("GET reads the version it names", status == 200 and body == b"version-one", status)
    status, head, _ = store.call("HEAD", "/%s/%s" % (bucket, key), {"versionId": v1})
    check("HEAD reads the version it names", status == 200 and head.get("content-length") == "11", status)
    status, _, body = store.call("GET", "/%s/%s" % (bucket, key), {"versionId": v1}, {"range": "bytes=0-6"})
    check("a ranged GET reads the version it names", status == 206 and body == b"version", status)

    status, _, _ = store.anonymous("GET", "/%s/%s" % (bucket, key))
    check("an anonymous read is refused", status in (401, 403), status)

    status, _, body = store.anonymous("GET", store.presign("GET", "/%s/%s" % (bucket, key), {"versionId": v1}))
    check("a presigned GET stays pinned to its version", status == 200 and body == b"version-one", status)

    upload = "tenants/probe/quarantine/" + uuid.uuid4().hex
    status, headers, _ = store.anonymous("PUT", store.presign("PUT", "/%s/%s" % (bucket, upload)),
                                         {"content-length": "8"}, b"uploaded")
    check("a presigned PUT uploads and returns a version id", status == 200 and headers.get("x-amz-version-id"),
          status)

    promoted = "tenants/probe/objects/" + uuid.uuid4().hex
    source = "%s?versionId=%s" % (_q("%s/%s" % (bucket, key), safe="/-_.~"), v1)
    status, headers, _ = store.call("PUT", "/%s/%s" % (bucket, promoted), headers={"x-amz-copy-source": source})
    copied = headers.get("x-amz-version-id")
    _, _, body = store.call("GET", "/%s/%s" % (bucket, promoted), {"versionId": copied} if copied else {})
    check("a server-side copy takes one exact version", status == 200 and copied and body == b"version-one",
          status)

    status, _, body = store.call("GET", "/" + bucket, {"versions": "", "prefix": key})
    listed = body.count(b"<Version>") if status == 200 else 0
    check("the versions of a key are listed", listed >= 2, listed)

    status, _, _ = store.call("DELETE", "/%s/%s" % (bucket, key), {"versionId": v1})
    gone, _, _ = store.call("GET", "/%s/%s" % (bucket, key), {"versionId": v1})
    kept, _, body = store.call("GET", "/%s/%s" % (bucket, key), {"versionId": v2})
    check("deleting one version leaves the others", status == 204 and gone in (400, 404)
          and kept == 200 and body == b"version-two", (status, gone, kept))
    return results


def main():
    env = settings()
    store = Store("127.0.0.1:%s" % env.get("OBJECT_STORE_PORT", "7070"),
                  env["OBJECT_STORE_ACCESS_KEY"], env["OBJECT_STORE_SECRET_KEY"])
    failed = 0
    for bucket in BUCKETS:
        store.ensure_versioned_bucket(bucket)
        enabled = store.versioning_enabled(bucket)
        failed += not enabled
        print("%s  bucket %s is versioned" % ("ok  " if enabled else "FAIL", bucket))

    probe = "sadara-probe-" + uuid.uuid4().hex[:12]
    store.ensure_versioned_bucket(probe)
    try:
        for name, passed, detail in prove(store, probe):
            failed += not passed
            print("%s  %s%s" % ("ok  " if passed else "FAIL", name, "" if passed else "  (%s)" % (detail,)))
    finally:
        store.remove_bucket(probe)

    if failed:
        print("objectstore: %d capability check(s) failed — this store cannot back the storage port" % failed)
        return 1
    print("objectstore: ready — %s versioned; every storage-port capability proven" % " and ".join(BUCKETS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
