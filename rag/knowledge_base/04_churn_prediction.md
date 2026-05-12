# Churn Prediction Guide

## What is Churn Prediction?
Churn prediction uses machine learning to identify members who are 
likely to cancel their membership before they actually do.
This gives the business time to intervene and retain them.

## Churn Risk Factors (in order of importance)
1. Payment failures — strongest predictor of churn
2. Reduced class attendance — member losing engagement
3. Basic tier membership — less investment = easier to leave
4. New member (less than 3 months) — honeymoon period risk
5. Long gap since last booking — losing habit
6. Age (18-25) — more likely to churn than 30-45 age group

## Risk Score Calculation
- Payment failure: +30 points
- Multiple payment failures (3+): +20 additional points
- No booking in 60+ days: +25 points
- New member under 3 months: +15 points
- Basic tier: +10 points
- Maximum score: 100 points

## Risk Levels
- 0-30: Low risk — monitor monthly
- 31-60: Medium risk — proactive outreach
- 61-100: High risk — immediate intervention

## Model Performance Benchmarks
- Good model accuracy: above 80%
- Good precision: above 75%
- Good recall: above 70%
- We want HIGH recall — better to flag too many than miss real churners