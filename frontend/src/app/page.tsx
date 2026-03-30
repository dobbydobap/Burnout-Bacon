import Link from "next/link";
import {
  Flame,
  BarChart3,
  Calendar,
  Timer,
  ShieldAlert,
  TrendingUp,
  ArrowRight,
} from "lucide-react";
import styles from "./page.module.css";

const features = [
  {
    icon: <Calendar size={24} />,
    title: "Smart Planning",
    description:
      "Auto-distribute study sessions across your week. Never overload a single day again.",
  },
  {
    icon: <Timer size={24} />,
    title: "Focus Tracking",
    description:
      "Track deep work sessions with a built-in timer. Compare planned vs actual study time.",
  },
  {
    icon: <ShieldAlert size={24} />,
    title: "Burnout Detection",
    description:
      "Rule-based risk scoring detects unhealthy patterns before they become serious.",
  },
  {
    icon: <BarChart3 size={24} />,
    title: "Productivity Analytics",
    description:
      "Heatmaps, charts, and trends help you understand when and how you work best.",
  },
  {
    icon: <TrendingUp size={24} />,
    title: "Smart Recommendations",
    description:
      "Get personalized suggestions to optimize your schedule and prevent burnout.",
  },
  {
    icon: <Flame size={24} />,
    title: "Auto-Rescheduling",
    description:
      "Missed a session? The system automatically redistributes work to keep you on track.",
  },
];

export default function LandingPage() {
  return (
    <div className={styles.landing}>
      <nav className={styles.nav}>
        <div className={styles.navLogo}>
          <div className={styles.navIcon}>
            <Flame size={20} />
          </div>
          <span className={styles.navTitle}>Burnout Beacon</span>
        </div>
        <div className={styles.navLinks}>
          <Link href="/login" className={styles.navLink}>
            Sign In
          </Link>
          <Link href="/signup" className={styles.navCta}>
            Get Started
          </Link>
        </div>
      </nav>

      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>
            Study smarter.
            <br />
            <span className={styles.heroHighlight}>Avoid burnout.</span>
          </h1>
          <p className={styles.heroText}>
            Burnout Beacon is the smart productivity platform that helps you plan
            work, track focus sessions, detect burnout risk, and automatically
            adjust your schedule.
          </p>
          <div className={styles.heroCtas}>
            <Link href="/signup" className={styles.heroBtn}>
              Start Free <ArrowRight size={18} />
            </Link>
            <Link href="/login" className={styles.heroBtnSecondary}>
              Sign In
            </Link>
          </div>
        </div>
        <div className={styles.heroVisual}>
          <div className={styles.heroCard}>
            <div className={styles.heroCardHeader}>
              <div className={styles.heroDot} style={{ background: "var(--color-accent-green)" }} />
              <div className={styles.heroDot} style={{ background: "var(--color-accent-gold)" }} />
              <div className={styles.heroDot} style={{ background: "var(--color-accent-red)" }} />
            </div>
            <div className={styles.heroMockStats}>
              <div className={styles.heroStat}>
                <span className={styles.heroStatValue}>12.5h</span>
                <span className={styles.heroStatLabel}>Focus Time</span>
              </div>
              <div className={styles.heroStat}>
                <span className={styles.heroStatValue}>87%</span>
                <span className={styles.heroStatLabel}>Completion</span>
              </div>
              <div className={styles.heroStat}>
                <span className={styles.heroStatValue} style={{ color: "var(--color-accent-green)" }}>Low</span>
                <span className={styles.heroStatLabel}>Burnout Risk</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.features}>
        <h2 className={styles.featuresTitle}>Everything you need to stay productive</h2>
        <div className={styles.featureGrid}>
          {features.map((f) => (
            <div key={f.title} className={styles.featureCard}>
              <div className={styles.featureIcon}>{f.icon}</div>
              <h3 className={styles.featureTitle}>{f.title}</h3>
              <p className={styles.featureDesc}>{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.cta}>
        <h2 className={styles.ctaTitle}>Ready to take control?</h2>
        <p className={styles.ctaText}>
          Join students and professionals who use Burnout Beacon to stay
          productive without burning out.
        </p>
        <Link href="/signup" className={styles.heroBtn}>
          Get Started Free <ArrowRight size={18} />
        </Link>
      </section>

      <footer className={styles.footer}>
        <p>Burnout Beacon &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}
