# Webhooks: Signature Verification (3.1.5.1)

## About This Module

This module focuses on **signature verification for incoming webhook requests**.
It explains why webhook authentication is required, how signatures are constructed, and how a receiver can verify that an event truly originates from a trusted provider.

The goal of this lesson is to treat **authenticity verification** as a mandatory boundary step in HTTP integrations, not as an optional security add-on.

All examples are intentionally minimal, explicit, and aligned with real-world webhook provider behavior.

---

## Why Webhook Signatures Matter

Webhook endpoints are **public HTTP endpoints by design**.
Without verification, anyone who knows the URL could:

* forge events,
* trigger false state changes,
* simulate payments, deliveries, or user actions.

Signature verification ensures that:

> **every accepted event was sent by a trusted provider and was not modified in transit**.

This makes authenticity a prerequisite for any further processing.

---

## Authenticity vs Authorization

An important distinction emphasized in this module:

* **Authentication** answers: *Who sent this request?*
* **Authorization** answers: *Are they allowed to do this?*

Webhook signatures solve the **authentication** problem.
They do not replace authorization or business rules.

---

## Core Signature Model

Most webhook providers follow the same conceptual model:

1. The provider and receiver share a **secret key**.
2. The provider computes a cryptographic signature from:

   * the raw request body,
   * the shared secret.
3. The signature is sent in an HTTP header.
4. The receiver recomputes the signature locally.
5. The request is accepted **only if signatures match**.

The most common algorithm is **HMAC-SHA256**.

---

## What Is Signed (and Why)

A critical detail demonstrated in this module:

* the signature is computed over the **raw request body**,
* not over parsed JSON,
* not over selected fields.

This guarantees:

* integrity of the full payload,
* protection against field reordering or injection,
* consistent verification across languages and frameworks.

---

## Failure Handling

If signature verification fails, the correct behavior is:

* reject the request immediately,
* return a `4xx` error (typically `401` or `400`),
* **do not execute any business logic**.

Invalid signatures are considered **permanent failures** and must not trigger retries.

---

## Relationship to Retries and Deduplication

Signature verification is the **first gate** in the webhook pipeline:

1. Signature verification → authenticity
2. Retry handling → delivery guarantees
3. Deduplication → execution safety

Events that fail signature verification:

* must not be retried,
* must not be deduplicated,
* must not be processed.

This strict ordering prevents both security issues and wasted resources.

---

## What This Module Does NOT Cover

To keep the lesson focused, the following topics are excluded:

* provider-specific header formats,
* timestamp-based replay protection,
* asymmetric signatures (public/private keys),
* IP allowlists and network-level filtering.

These concerns build on top of the signature verification foundation shown here.

---

## Educational Focus

This module emphasizes:

* explicit trust boundaries,
* rejecting unauthenticated input early,
* understanding cryptographic intent rather than library usage.

The examples are designed to be read as **security-critical code**, not as framework configuration.

---

## Position in the Course

This lesson establishes the **authenticity layer** of webhook integrations.

Together with:

* retries (delivery reliability),
* deduplication (execution safety),

it completes the foundational triad required for **secure and reliable webhook-based systems**.
