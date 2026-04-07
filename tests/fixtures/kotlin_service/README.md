# Payment Gateway Service

A Kotlin Spring Boot service that processes payment authorizations via Stripe.

## Architecture

- **PaymentController**: REST endpoint `POST /api/v1/payments`
- **StripeGateway**: Wraps the Stripe Java SDK for payment authorization
- **PaymentRepository**: Persists transaction records to PostgreSQL via JPA

## Tech Stack

Kotlin 1.9, Spring Boot 3.2, Stripe SDK, PostgreSQL, Testcontainers, JUnit 5
