# Fraud Detection Guide

## Types of Payment Fraud in Fitness Businesses
1. Stolen credit card memberships
2. Chargebacks after using services
3. Account sharing (one membership, multiple users)
4. Fake referral abuse
5. Multiple failed payment attempts

## Fraud Warning Signals
- Multiple failed payments from different cards in short period
- New member with immediate payment failure
- Unusual payment amounts (different from tier price)
- Multiple accounts from same email domain
- Payment from unusual geographic location
- Rapid succession of payment attempts

## Normal Payment Patterns
- One payment per month per member
- Amount matches tier: Basic=$29, Standard=$59, Premium=$99
- Payment failure rate should be below 5%
- Most failures happen on first attempt of month

## Anomaly Detection Thresholds
- Flag if: more than 3 failed payments in 30 days
- Flag if: payment amount differs from tier price
- Flag if: more than 2 payments in same month
- Flag if: payment failure rate exceeds 10% in any week

## Response Protocol
1. Automatic flag in system
2. Freeze account pending review
3. Email member for verification
4. Manual review within 24 hours
5. Report to payment processor if confirmed fraud