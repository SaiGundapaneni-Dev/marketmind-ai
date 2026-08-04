export type PortfolioScoreCategory = {
  score: number;
  rating: string;
  summary: string;
  factors: string[];
  suggested_action: string;
};

export type PortfolioScoreResponse = {
  overall_score: number;
  rating: string;
  summary: string;
  scores: {
    diversification: PortfolioScoreCategory;
    concentration: PortfolioScoreCategory;
    performance: PortfolioScoreCategory;
    portfolio_health: PortfolioScoreCategory;
    market_exposure: PortfolioScoreCategory;
  };
  strengths: string[];
  weaknesses: string[];
  improvement_suggestions: string[];
  disclaimer: string;
};
