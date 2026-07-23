import React from 'react';
import { AnimatePresence, motion } from "motion/react";
import { X, Check, Zap, Crown } from "lucide-react";
import { useSelector } from 'react-redux';
import { verifyPayment } from "../features/verifyPayment";
import { createOrder } from "../features/createOrder";

const PLANS = [
    {
        id: "starter",
        name: "Starter",
        amount: "₹199",
        credits: 500,
        features: ["500 Generation Credits", "Standard Response Speed", "30 Days Validity"]
    },
    {
        id: "pro",
        name: "Pro",
        amount: "₹499",
        credits: 1000,
        popular: true,
        features: ["1000 Generation Credits", "Priority Processing", "All AI Models Enabled", "30 Days Validity"]
    }
];

function BillingDrawer({ open, onClose }) {
    const { userData } = useSelector(state => state.user);
    const credits = userData?.credits ?? 0;
    const totalCredits = userData?.totalCredits || 100;
    const progressPercentage = Math.min(
        100,
        Math.max(0, (credits / (userData?.totalCredits || 1)) * 100)
    );

    const handleUpgrade = async (planId) => {
        try {
            // 1. Call createOrder API with selected plan ID
            const data = await createOrder(planId);
            console.log("📦 Response from createOrder:", data);

            // 2. Configure Razorpay Options
            const options = {
                key: import.meta.env.VITE_RAZORPAY_KEY_ID,
                amount: data.order.amount,
                currency: data.order.currency,
                name: "CortexAI",
                description: `${data.plan.name} Plan`,
                order_id: data.order.id,
                handler: async (response) => {
                    try {
                        console.log("Razorpay Response:", response);

                        // 3. Call verifyPayment API upon successful modal checkout
                        const verifyRes = await verifyPayment({
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature,
                        });

                        if (verifyRes) {
                            alert("🎉 Payment Verified Successfully!");
                            window.location.reload(); // Reload to refresh user credits and plan state
                        }
                    } catch (verifyError) {
                        console.error("❌ Payment verification failed:", verifyError);
                        alert("Payment verification failed. Please contact support.");
                    }
                },
                theme: {
                    color: "#2563EB",
                }
            };

            // 4. Open Razorpay Checkout Modal
            const razorpay = new window.Razorpay(options);
            razorpay.open();

        } catch (error) {
            console.error("❌ Upgrade error:", error);
            alert("Failed to initiate payment order.");
        }
    };

    return (
        <AnimatePresence>
            {open && (
                <>
                    {/* Backdrop overlay */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 0.5 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black z-40"
                    />

                    {/* Slide-over Drawer Panel */}
                    <motion.div
                        initial={{ x: "100%" }}
                        animate={{ x: 0 }}
                        exit={{ x: "100%" }}
                        transition={{ type: "spring", damping: 25, stiffness: 200 }}
                        className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-slate-900 border-l border-slate-800 p-6 z-50 text-white shadow-2xl flex flex-col justify-between overflow-y-auto"
                    >
                        {/* Header */}
                        <div>
                            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                                <div className="flex items-center gap-2">
                                    <Zap className="w-5 h-5 text-blue-500" />
                                    <h2 className="text-xl font-bold">Upgrade Plan</h2>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <p className="text-sm text-slate-400 mt-3 mb-6">
                                Select a subscription plan to refill your credits and unlock premium AI generation features.
                            </p>

                            {/* Current Plan Card */}
                            <div className="rounded-xl bg-white/[0.04] border border-white/10 p-4 mb-6">
                                <div className="flex justify-between items-center">
                                    <div>
                                        <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">
                                            Current Plan
                                        </p>
                                        <h3 className="text-lg font-bold text-white capitalize mt-0.5">
                                            {userData?.plan || 'Free'}
                                        </h3>
                                    </div>
                                    <Crown className="w-6 h-6 text-yellow-500" />
                                </div>

                                <div className="mt-5">
                                    <div className="flex justify-between text-xs text-slate-400 mb-2">
                                        <span>Credits</span>
                                        <span>
                                            {userData?.credits || 0}/{userData?.totalCredits || 100}
                                        </span>
                                    </div>

                                    <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                                        <div
                                            className="h-full bg-indigo-500 transition-all duration-500"
                                            style={{
                                                width: `${progressPercentage}%`
                                            }}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Plans List */}
                            <div className="space-y-4">
                                {PLANS.map((plan) => (
                                    <div
                                        key={plan.id}
                                        className={`relative p-5 rounded-xl border transition ${plan.popular
                                            ? "border-blue-500 bg-blue-500/10"
                                            : "border-slate-800 bg-slate-800/40 hover:border-slate-700"
                                            }`}
                                    >
                                        {plan.popular && (
                                            <span className="absolute -top-3 right-4 bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                                                Most Popular
                                            </span>
                                        )}

                                        <div className="flex justify-between items-baseline mb-2">
                                            <h3 className="text-lg font-semibold">{plan.name}</h3>
                                            <span className="text-2xl font-bold">{plan.amount}</span>
                                        </div>

                                        <p className="text-xs text-blue-400 font-medium mb-3">
                                            +{plan.credits} Credits / month
                                        </p>

                                        <ul className="space-y-2 mb-4">
                                            {plan.features.map((feature, i) => (
                                                <li key={i} className="flex items-center gap-2 text-xs text-slate-300">
                                                    <Check className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                                                    <span>{feature}</span>
                                                </li>
                                            ))}
                                        </ul>

                                        {/* Click Handler */}
                                        <button
                                            onClick={() => handleUpgrade(plan.id)}
                                            className={`w-full py-2.5 rounded-lg text-sm font-semibold transition ${plan.popular
                                                ? "bg-blue-600 hover:bg-blue-500 text-white"
                                                : "bg-slate-700 hover:bg-slate-600 text-white"
                                                }`}
                                        >
                                            Choose {plan.name}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="pt-6 border-t border-slate-800 text-center mt-6">
                            <p className="text-xs text-slate-500">
                                Secured by Razorpay. Cancel or change plans anytime.
                            </p>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}

export default BillingDrawer;