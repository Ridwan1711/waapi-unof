import crypto from "node:crypto";

import { describe, expect, it } from "vitest";

import { signPayload } from "./signing";

describe("signPayload", () => {
  it("matches a manually computed HMAC", () => {
    const secret = "secret";
    const timestamp = "1700000000000";
    const body = "hello-body";
    const expected = crypto
      .createHmac("sha256", secret)
      .update(`${timestamp}.`)
      .update(body)
      .digest("hex");

    expect(signPayload(secret, timestamp, body)).toBe(expected);
  });

  it("is deterministic and body-sensitive", () => {
    expect(signPayload("s", "1", "a")).toBe(signPayload("s", "1", "a"));
    expect(signPayload("s", "1", "a")).not.toBe(signPayload("s", "1", "b"));
  });
});
