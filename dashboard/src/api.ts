// Mock data types and API functions for local development (polling simulation).

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";
export type Action = "HOLD" | "REDUCE" | "CLOSE";

export interface ScoutedTick {
  instrument: string;
  bid: number;
  ask: number;
  timestamp: number;
  scoutProcessedAt: number;
}

export interface ExecutedTrade {
  instrument: string;
  side: "BUY" | "SELL";
  size: number;
  price: number;
  timestamp: number;
}

export interface RiskAlert {
  instrument: string;
  riskLevel: RiskLevel;
  recommendedAction: Action;
  timestamp: number;
}

export interface SizeSignal {
  instrument: string;
  size: number;
  timestamp: number;
}

export interface FilterParamPoint {
  time: number;
  volThreshold: number;
  momentumWindow: number;
}

// Helper to simulate network latency
const wait = (ms: number) => new Promise(res => setTimeout(res, ms));

// Sample static data (will be randomized slightly on each fetch for realism)
const sampleInstruments = [
  "BTC-30JUN25-30000-C",
  "ETH-30JUN25-2000-C",
  "BTC-30JUN25-25000-P",
];

// Maintain some state between calls (for executed trades accumulation)
let executedTradesData: ExecutedTrade[] = [
  {
    instrument: "BTC-30JUN25-30000-C",
    side: "BUY",
    size: 1,
    price: 0.105,
    timestamp: Date.now() - 30000,
  },
  {
    instrument: "ETH-30JUN25-2000-C",
    side: "BUY",
    size: 5,
    price: 0.052,
    timestamp: Date.now() - 45000,
  },
];

// Pre-generate RL parameter trend data (e.g., 10 time points)
const rlParametersData: FilterParamPoint[] = Array.from({ length: 10 }, (_, i) => ({
  time: i + 1,
  volThreshold: 0.5 + 0.03 * i,    // gradually increasing
  momentumWindow: 10 + 1 * i,     // gradually increasing
}));

/** Fetch scouted candidates (ticks.scouted feed) */
export async function fetchScoutedCandidates(): Promise<ScoutedTick[]> {
  await wait(500); // simulate latency
  const now = Date.now();
  // Generate 3 sample scouted tick entries with slight randomization
  const data: ScoutedTick[] = sampleInstruments.map((instr, idx) => ({
    instrument: instr,
    bid: parseFloat((0.1 + Math.random() * 0.02).toFixed(3)),  // random bid
    ask: parseFloat((0.12 + Math.random() * 0.02).toFixed(3)), // random ask, slightly above bid
    timestamp: now - idx * 1000,           // stagger timestamps by 1s
    scoutProcessedAt: now - idx * 1000 + 50 // processed shortly after timestamp
  }));
  return data;
}

/** Fetch executed trades (executed orders feed) */
export async function fetchExecutedTrades(): Promise<ExecutedTrade[]> {
  await wait(500);
  // For simplicity, return the static list. In a real app, new trades could be appended here.
  return executedTradesData;
}

/** Fetch risk alerts (risk.alerts feed) */
export async function fetchRiskAlerts(): Promise<RiskAlert[]> {
  await wait(500);
  // Sample: one HIGH and one MEDIUM risk alert
  const now = Date.now();
  const alerts: RiskAlert[] = [
    {
      instrument: "BTC-30JUN25-30000-C",
      riskLevel: "HIGH",
      recommendedAction: "CLOSE",
      timestamp: now - 10000,
    },
    {
      instrument: "ETH-30JUN25-2000-C",
      riskLevel: "MEDIUM",
      recommendedAction: "REDUCE",
      timestamp: now - 15000,
    },
  ];
  return alerts;
}

/** Fetch RL-tuned filter parameters (from Redis or backend) */
export async function fetchRLParameters(): Promise<FilterParamPoint[]> {
  await wait(500);
  // Return the static trend data. A real API might return latest values or time-series.
  return rlParametersData;
}

/** Fetch sizing signals (size.signals feed) */
export async function fetchSizingSignals(): Promise<SizeSignal[]> {
  await wait(500);
  const now = Date.now();
  const signals: SizeSignal[] = [
    {
      instrument: "BTC-30JUN25-30000-C",
      size: 1,
      timestamp: now - 30000,
    },
    {
      instrument: "ETH-30JUN25-2000-C",
      size: 5,
      timestamp: now - 45000,
    },
  ];
  return signals;
}
