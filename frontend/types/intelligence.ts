export type IntelligenceSeverity =
  | "low"
  | "medium"
  | "high"
  | "critical"
  | string;

export type PortfolioStatus =
  | "excellent"
  | "good"
  | "fair"
  | "weak"
  | "critical"
  | string;

export type IntelligenceInsight = {
  priority?: number;
  category?: string;
  severity?: IntelligenceSeverity;
  title?: string;
  message?: string;
  evidence?: string[];
  suggested_action?: string;
  affected_symbols?: string[];
};

export type IntelligenceListItem =
  | string
  | {
      title?: string;
      message?: string;
      description?: string;
      severity?: IntelligenceSeverity;
      symbol?: string;
      suggested_action?: string;
      affected_symbols?: string[];
    };

export type HoldingToWatch = {
  symbol?: string;
  name?: string;
  allocation_percent?: number;
  profit?: number;
  profit_percent?: number;
  reason?: string;
};

export type PortfolioIntelligenceResponse = {
  portfolio_status?: PortfolioStatus;
  executive_summary?: string;
  priority_insights?: IntelligenceInsight[];
  strengths?: IntelligenceListItem[];
  risks?: IntelligenceListItem[];
  opportunities?: IntelligenceListItem[];
  holdings_to_watch?: HoldingToWatch[];
  recent_changes?: string[];
  recommended_questions?: string[];
  disclaimer?: string;
  status?: string;
};
