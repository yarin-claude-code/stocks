# Project Summary

**Name:** Smart Stock Ranker
**Goal:** Quantitative stock ranking app — math correctness > UI polish.
**Milestone:** v1.0 Smart Stock Ranker
**Current Phase:** 02 — Ranking Algorithm

## What it does
- Fetches OHLCV data for a seeded list of stocks via yfinance (batch, every 5 min)
- Computes a composite score per stock using 5 weighted factors
- Ranks stocks within their domain (sector/peer group)
- Exposes rankings via REST API

## Status
- Phase 01 complete: data pipeline + Supabase Postgres migration
- Phase 02 in progress: ranking engine (pure Python, no I/O)
- Phase 03 future: React frontend
