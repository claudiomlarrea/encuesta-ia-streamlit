"use client";

import { useState } from "react";
import { PayPalButtons, PayPalScriptProvider } from "@paypal/react-paypal-js";
import { Button } from "@/components/ui/button";
import { CreditCard } from "lucide-react";

interface PaymentButtonsProps {
  courseId: string;
  courseTitle: string;
  amount: number;
  currency: string;
}

export function PaymentButtons({ courseId, courseTitle, amount, currency }: PaymentButtonsProps) {
  const [loading, setLoading] = useState(false);

  async function handleMercadoPago() {
    setLoading(true);
    try {
      const res = await fetch("/api/payments/mercadopago", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ courseId, courseTitle, amount, currency }),
      });
      const data = await res.json();
      if (data.init_point) {
        window.location.href = data.init_point;
      }
    } catch {
      alert("Error al procesar el pago con Mercado Pago.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <Button
        onClick={handleMercadoPago}
        disabled={loading}
        className="w-full"
        variant="secondary"
      >
        <CreditCard className="mr-2 h-4 w-4" />
        {loading ? "Procesando..." : "Pagar con Mercado Pago"}
      </Button>

      {process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID && (
        <PayPalScriptProvider
          options={{
            clientId: process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID,
            currency,
          }}
        >
          <PayPalButtons
            style={{ layout: "vertical", label: "pay" }}
            createOrder={async () => {
              const res = await fetch("/api/payments/paypal", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ courseId, amount, currency }),
              });
              const data = await res.json();
              return data.orderId;
            }}
            onApprove={async (data) => {
              await fetch("/api/payments/paypal/capture", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ orderId: data.orderID, courseId }),
              });
              window.location.href = "/dashboard/cursos";
            }}
          />
        </PayPalScriptProvider>
      )}
    </div>
  );
}
