class RecommendationService:
    @staticmethod
    def generate_recommendation(profile, prediction_df, trend):
        if not profile:
            return "No customer financial profile found. Recommendation is based only on prediction trend."

        risk = profile.get("risk_tolerance", "medium")
        budget = float(profile.get("investment_budget", 0))

        if trend == "bullish":
            if risk == "low":
                return (
                    f"The stock trend looks positive, but this user has low risk tolerance. "
                    f"Recommendation: consider a small investment within the ${budget:.2f} budget."
                )
            elif risk == "medium":
                return (
                    f"The stock trend looks positive and matches a moderate risk profile. "
                    f"Recommendation: consider a balanced investment within the ${budget:.2f} budget."
                )
            else:
                return (
                    f"The stock trend looks positive and the user has high risk tolerance. "
                    f"Recommendation: this may be suitable for stronger exposure within the ${budget:.2f} budget."
                )

        elif trend == "bearish":
            return (
                "The predicted trend looks weak. Recommendation: wait, monitor the stock, "
                "or avoid increasing investment right now."
            )

        return "The stock trend is neutral. Recommendation: hold and continue monitoring."