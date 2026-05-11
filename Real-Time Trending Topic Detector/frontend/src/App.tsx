import { useState, useEffect, useCallback } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

interface TrendingArticle {
  title: string;
  edit_count: number;
  unique_editors: number;
  total_bytes_changed: number;
  avg_bytes_changed: number;
  velocity: number;
  trend: "trending" | "not trending" | "stable";
  first_edit: string;
  last_edit: string;
  time_computed: string;
}

interface Stats {
  total_edits: number;
  edits_per_minute: number;
  articles_tracked: number;
  last_aggregation: string;
}

type Tab = "trending" | "rising" | "not trending" | "stats";

const REFRESH_INTERVAL = 30;

const trendColor = (trend: string) => {
  if (trend === "trending") return "#00e676";
  if (trend === "not trending") return "#ff5252";
  return "#ffab40";
};

const trendIcon = (trend: string) => {
  if (trend === "trending") return "▲";
  if (trend === "not trending") return "▼";
  return "—";
};

const fmt = (n: number) => n?.toLocaleString() ?? "—";
const fmtBytes = (n: number) => {
  if (!n) return "0 B";
  const abs = Math.abs(n);
  if (abs >= 1000) return `${(n / 1000).toFixed(1)}KB`;
  return `${n}B`;
};
const timeAgo = (iso: string) => {
  const normalized = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
  const diff = Math.floor((Date.now() - new Date(normalized).getTime()) / 1000);
  if (diff < 0) return "just now";
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
};

export default function App() {
  const [tab, setTab] = useState<Tab>("trending");
  const [articles, setArticles] = useState<TrendingArticle[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(REFRESH_INTERVAL);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const fetchTrending = useCallback(async (currentTab: Tab) => {
    setLoading(true);
    setError(null);
    try {
      if (currentTab === "stats") {
        const res = await axios.get(`${API_BASE}/stats`);
        setStats(res.data);
      } else {
        const endpoint =
          currentTab === "rising"
            ? "/trending/rising"
            : currentTab === "not trending"
            ? "/trending/not trending"
            : "/trending";
        const res = await axios.get<TrendingArticle[]>(`${API_BASE}${endpoint}`, {
          params: { limit: 20 },
        });
        setArticles(res.data);
      }
      setLastUpdated(new Date().toLocaleTimeString());
      setCountdown(REFRESH_INTERVAL);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? "Failed to fetch data. Is the pipeline running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTrending(tab);
  }, [tab, fetchTrending]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((c) => {
        if (c <= 1) {
          fetchTrending(tab);
          return REFRESH_INTERVAL;
        }
        return c - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [tab, fetchTrending]);

  const tabs: { key: Tab; label: string; desc: string }[] = [
    { key: "trending", label: "All Topics", desc: "ranked by velocity × edits" },
    { key: "rising", label: "Rising", desc: "accelerating now" },
    { key: "not trending", label: "not trending", desc: "losing momentum" },
    { key: "stats", label: "Pipeline Stats", desc: "system health" },
  ];

  return (
    <div style={styles.root}>
      <div style={styles.header}>
        <div>
          <div style={styles.headerTop}>
            <span style={styles.dot} />
            <span style={styles.logo}>WIKISTREAM</span>
            <span style={styles.badge}>LIVE</span>
          </div>
          <p style={styles.subtitle}>Real-time Wikipedia edit trend detector</p>
        </div>
        <div style={styles.headerRight}>
          {lastUpdated && (
            <span style={styles.updated}>Updated {lastUpdated}</span>
          )}
          <div style={styles.refreshRing}>
            <svg width="32" height="32" viewBox="0 0 32 32">
              <circle cx="16" cy="16" r="13" fill="none" stroke="#222" strokeWidth="2" />
              <circle
                cx="16" cy="16" r="13" fill="none"
                stroke="#00e676" strokeWidth="2"
                strokeDasharray={`${(countdown / REFRESH_INTERVAL) * 81.7} 81.7`}
                strokeLinecap="round"
                transform="rotate(-90 16 16)"
                style={{ transition: "stroke-dasharray 1s linear" }}
              />
            </svg>
            <span style={styles.countdown}>{countdown}s</span>
          </div>
          <button style={styles.refreshBtn} onClick={() => fetchTrending(tab)}>
            ↻ Refresh
          </button>
        </div>
      </div>

      <div style={styles.tabs}>
        {tabs.map((t) => (
          <button
            key={t.key}
            style={{ ...styles.tab, ...(tab === t.key ? styles.tabActive : {}) }}
            onClick={() => setTab(t.key)}
          >
            <span style={styles.tabLabel}>{t.label}</span>
            <span style={styles.tabDesc}>{t.desc}</span>
          </button>
        ))}
      </div>

      <div style={styles.content}>
        {error && (
          <div style={styles.error}>
            <span style={{ color: "#ff5252" }}>⚠</span> {error}
          </div>
        )}

        {loading && !error && (
          <div style={styles.loading}>
            <span style={styles.loadingDots}>● ● ●</span>
            <span>Fetching from pipeline...</span>
          </div>
        )}

        {!loading && !error && tab !== "stats" && articles.length === 0 && (
          <div style={styles.empty}>
            <p style={{ color: "#555", fontFamily: "monospace" }}>
              No data yet — pipeline may still be warming up.
            </p>
            <p style={{ color: "#333", fontSize: "13px" }}>
              Check that producer, consumer, and aggregation.py are all running.
            </p>
          </div>
        )}

        {!loading && !error && tab !== "stats" && articles.length > 0 && (
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={{ ...styles.th, width: "32px" }}>#</th>
                  <th style={styles.th}>Article</th>
                  <th style={{ ...styles.th, textAlign: "right" }}>Edits</th>
                  <th style={{ ...styles.th, textAlign: "right" }}>Editors</th>
                  <th style={{ ...styles.th, textAlign: "right" }}>Velocity</th>
                  <th style={{ ...styles.th, textAlign: "right" }}>Bytes Δ</th>
                  <th style={{ ...styles.th, textAlign: "right" }}>Avg/Edit</th>
                  <th style={{ ...styles.th, textAlign: "center" }}>Status</th>
                  <th style={{ ...styles.th, textAlign: "right" }}>Last Edit</th>
                </tr>
              </thead>
              <tbody>
                {articles.map((a, i) => (
                  <tr key={a.title} style={styles.tr}>
                    <td style={{ ...styles.td, color: "#444", fontSize: "12px" }}>{i + 1}</td>
                    <td style={styles.td}>
                      <a
                        href={`https://en.wikipedia.org/wiki/${encodeURIComponent(a.title)}`}
                        target="_blank"
                        rel="noreferrer"
                        style={styles.articleLink}
                      >
                        {a.title}
                      </a>
                    </td>
                    <td style={{ ...styles.tdMono, textAlign: "right" }}>{fmt(a.edit_count)}</td>
                    <td style={{ ...styles.tdMono, textAlign: "right", color: "#888" }}>{fmt(a.unique_editors)}</td>
                    <td style={{ ...styles.tdMono, textAlign: "right", color: trendColor(a.trend) }}>
                      {a.velocity > 0 ? "+" : ""}{fmt(a.velocity)}
                    </td>
                    <td style={{ ...styles.tdMono, textAlign: "right", color: a.total_bytes_changed >= 0 ? "#00e676" : "#ff5252" }}>
                      {a.total_bytes_changed >= 0 ? "+" : ""}{fmtBytes(a.total_bytes_changed)}
                    </td>
                    <td style={{ ...styles.tdMono, textAlign: "right", color: "#666" }}>
                      {fmtBytes(Math.round(a.avg_bytes_changed))}
                    </td>
                    <td style={{ ...styles.td, textAlign: "center" }}>
                      <span style={{ ...styles.pill, background: trendColor(a.trend) + "22", color: trendColor(a.trend) }}>
                        {trendIcon(a.trend)} {a.trend}
                      </span>
                    </td>
                    <td style={{ ...styles.tdMono, textAlign: "right", color: "#555", fontSize: "12px" }}>
                      {timeAgo(a.last_edit)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && !error && tab === "stats" && (
          <div>
            {stats ? (
              <div style={styles.statsGrid}>
                <StatCard label="Total Edits Processed" value={fmt(stats.total_edits)} unit="events" color="#00e676" />
                <StatCard label="Edits Per Minute" value={fmt(stats.edits_per_minute)} unit="eps" color="#40c4ff" />
                <StatCard label="Articles Tracked" value={fmt(stats.articles_tracked)} unit="articles" color="#ffab40" />
                <StatCard label="Last Aggregation" value={timeAgo(stats.last_aggregation)} unit="refresh" color="#ce93d8" />
              </div>
            ) : (
              <div style={styles.empty}>
                <p style={{ color: "#555" }}>No stats available. Is aggregation.py running?</p>
              </div>
            )}
          </div>
        )}
      </div>

      <div style={styles.footer}>
        <span>Wikipedia SSE → Kafka → PostgreSQL → FastAPI</span>
        <span style={{ color: "#333" }}>enwiki · human edits only · bots filtered</span>
      </div>
    </div>
  );
}

function StatCard({ label, value, unit, color }: { label: string; value: string; unit: string; color: string }) {
  return (
    <div style={{ ...styles.statCard, borderColor: color + "33" }}>
      <span style={{ ...styles.statUnit, color }}>{unit}</span>
      <span style={{ ...styles.statValue, color }}>{value}</span>
      <span style={styles.statLabel}>{label}</span>
    </div>
  );
}

type CSSStyles = { [key: string]: React.CSSProperties };

const styles: CSSStyles = {
  root: {
    minHeight: "100vh",
    background: "#080808",
    color: "#e0e0e0",
    fontFamily: "'IBM Plex Sans', 'Helvetica Neue', sans-serif",
    display: "flex",
    flexDirection: "column",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    padding: "28px 32px 20px",
    borderBottom: "1px solid #1a1a1a",
  },
  headerTop: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "6px",
  },
  dot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    background: "#00e676",
    boxShadow: "0 0 8px #00e676",
    display: "inline-block",
    animation: "pulse 2s infinite",
  },
  logo: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "20px",
    fontWeight: 600,
    letterSpacing: "0.15em",
    color: "#fff",
  },
  badge: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 600,
    letterSpacing: "0.1em",
    color: "#00e676",
    border: "1px solid #00e67644",
    background: "#00e67611",
    padding: "2px 8px",
    borderRadius: "3px",
  },
  subtitle: {
    fontSize: "13px",
    color: "#555",
    margin: 0,
    letterSpacing: "0.02em",
  },
  headerRight: {
    display: "flex",
    alignItems: "center",
    gap: "16px",
  },
  updated: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "12px",
    color: "#444",
  },
  refreshRing: {
    position: "relative",
    width: "32px",
    height: "32px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  countdown: {
    position: "absolute",
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "9px",
    color: "#555",
  },
  refreshBtn: {
    background: "transparent",
    border: "1px solid #222",
    color: "#666",
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "12px",
    padding: "6px 14px",
    borderRadius: "4px",
    cursor: "pointer",
    letterSpacing: "0.05em",
  },
  tabs: {
    display: "flex",
    gap: "4px",
    padding: "12px 32px",
    borderBottom: "1px solid #111",
    background: "#0a0a0a",
  },
  tab: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    gap: "2px",
    background: "transparent",
    border: "1px solid transparent",
    color: "#444",
    padding: "8px 16px",
    borderRadius: "6px",
    cursor: "pointer",
    transition: "all 0.15s ease",
  },
  tabActive: {
    background: "#111",
    border: "1px solid #1e1e1e",
    color: "#e0e0e0",
  },
  tabLabel: {
    fontSize: "13px",
    fontWeight: 500,
    letterSpacing: "0.02em",
  },
  tabDesc: {
    fontSize: "11px",
    color: "#444",
    fontFamily: "'IBM Plex Mono', monospace",
  },
  content: {
    flex: 1,
    padding: "24px 32px",
  },
  error: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "13px",
    color: "#ff5252",
    background: "#ff525211",
    border: "1px solid #ff525233",
    borderRadius: "6px",
    padding: "12px 16px",
    marginBottom: "16px",
  },
  loading: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "12px",
    padding: "60px 0",
    color: "#333",
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "13px",
  },
  loadingDots: {
    color: "#00e676",
    fontSize: "20px",
    letterSpacing: "8px",
    animation: "pulse 1.5s infinite",
  },
  empty: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "60px 0",
    gap: "8px",
    textAlign: "center",
  },
  tableWrapper: {
    overflowX: "auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontFamily: "'IBM Plex Sans', sans-serif",
    fontSize: "13px",
  },
  th: {
    textAlign: "left",
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 500,
    letterSpacing: "0.1em",
    color: "#444",
    textTransform: "uppercase",
    padding: "8px 12px",
    borderBottom: "1px solid #111",
    whiteSpace: "nowrap",
  },
  tr: {
    borderBottom: "1px solid #0f0f0f",
    transition: "background 0.1s ease",
  },
  td: {
    padding: "10px 12px",
    color: "#bbb",
    verticalAlign: "middle",
    whiteSpace: "nowrap",
  },
  tdMono: {
    padding: "10px 12px",
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "13px",
    color: "#bbb",
    verticalAlign: "middle",
    whiteSpace: "nowrap",
  },
  articleLink: {
    color: "#90caf9",
    textDecoration: "none",
    fontWeight: 500,
    fontSize: "13px",
    maxWidth: "280px",
    display: "inline-block",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    verticalAlign: "bottom",
  },
  pill: {
    display: "inline-flex",
    alignItems: "center",
    gap: "4px",
    padding: "2px 10px",
    borderRadius: "3px",
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "11px",
    fontWeight: 600,
    letterSpacing: "0.05em",
    whiteSpace: "nowrap",
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "16px",
    marginTop: "8px",
  },
  statCard: {
    background: "#0d0d0d",
    border: "1px solid #1a1a1a",
    borderRadius: "8px",
    padding: "20px 24px",
    display: "flex",
    flexDirection: "column",
    gap: "6px",
  },
  statUnit: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "10px",
    fontWeight: 600,
    letterSpacing: "0.12em",
    textTransform: "uppercase",
  },
  statValue: {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "32px",
    fontWeight: 600,
    letterSpacing: "-0.02em",
    lineHeight: 1,
  },
  statLabel: {
    fontSize: "12px",
    color: "#444",
    marginTop: "4px",
  },
  footer: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "14px 32px",
    borderTop: "1px solid #111",
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: "11px",
    color: "#333",
    letterSpacing: "0.04em",
  },
};
