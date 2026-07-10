# Sprint 8 - Market News Search and Sentiment

## Features Completed

- Added News Search API
- Integrated Yahoo Finance news data
- Added relevance filtering to remove unrelated articles
- Added basic sentiment analysis
- Added sentiment confidence and reason
- Added formatted published timestamps
- Added frontend News page
- Added sentiment summary cards
- Added recent news searches
- Added quick recent-search buttons
- Stored recent searches in PostgreSQL
- Added unique constraint to prevent duplicate search history

## Backend Endpoints

### GET /news/search/{symbol}

Returns relevance-filtered stock news with sentiment labels.

### GET /news/recent

Returns recent unique stock news searches.

## Current Scope

- US stocks only
- Basic keyword-based sentiment
- Yahoo Finance as initial news provider

## Future Improvements

- Add multiple news providers
- Improve sentiment using LLM or financial NLP model
- Add article summarization
- Add portfolio-level news monitoring
- Add alerts for high-impact news