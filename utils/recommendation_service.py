class RecommendationService:
    @staticmethod
    def generate_recommendation(profile, prediction, trend="neutral"):
        if not profile:
            return "No customer financial profile found."

        risk = profile.get("risk_tolerance", "medium")
        budget = float(profile.get("investment_budget", 0))

        if trend == "bullish":
            if risk == "low":
                return f"Positive trend detected, but invest cautiously. Keep exposure small within your ${budget:.2f} budget."
            if risk == "medium":
                return f"This stock may fit a balanced strategy. Consider moderate investment within your ${budget:.2f} budget."
            return f"This stock may suit a higher-risk profile. You can consider stronger exposure within your ${budget:.2f} budget."

        if trend == "bearish":
            return "Current trend looks weak. Consider waiting or reducing risk before investing."

        return "Trend is neutral. Watch the stock and avoid making large moves without more confirmation."