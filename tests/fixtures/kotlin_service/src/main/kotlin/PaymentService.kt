package com.example.payments

import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service

data class PaymentRequest(val customerId: String, val amountCents: Int, val currency: String)
data class PaymentResult(val success: Boolean, val paymentIntentId: String?)

interface StripeGateway {
    fun charge(amountCents: Int, currency: String): PaymentResult
}

@Service
class PaymentService(private val gateway: StripeGateway) {

    private val log = LoggerFactory.getLogger(javaClass)

    fun authorize(request: PaymentRequest): PaymentResult {
        log.info("Authorizing payment for customer {}", request.customerId)
        return gateway.charge(request.amountCents, request.currency)
    }
}
