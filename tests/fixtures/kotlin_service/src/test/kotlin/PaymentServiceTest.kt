package com.example.payments

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.assertTrue
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`

class PaymentServiceTest {

    private val gateway: StripeGateway = mock(StripeGateway::class.java)
    private val service = PaymentService(gateway)

    @Test
    fun `authorize returns success when gateway accepts`() {
        val request = PaymentRequest("cust_123", 1000, "USD")
        `when`(gateway.charge(1000, "USD")).thenReturn(PaymentResult(true, "pi_123"))
        val result = service.authorize(request)
        assertTrue(result.success)
    }
}
