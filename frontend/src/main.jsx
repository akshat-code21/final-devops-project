import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  LayoutDashboard,
  Receipt,
  Wallet,
  LineChart,
  Clock,
  CircleCheck,
  BadgeCheck,
  ArrowRight,
  Plane,
  CirclePlus,
  Rocket,
  MoreHorizontal,
  Plus,
  X,
} from 'lucide-react';
import './styles.css';

const API = '/api';
const STATUSES = ['ALL', 'PENDING', 'APPROVED', 'PAID'];

function App() {
  const [expenses, setExpenses] = useState([]);
  const [stats, setStats] = useState({ total: 0, pending: 0, approved: 0, paid: 0, total_spend: 0 });
  const [filter, setFilter] = useState('ALL');
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      setError('');
      const [listRes, statsRes] = await Promise.all([
        fetch(`${API}/expenses`),
        fetch(`${API}/expenses/stats`),
      ]);
      if (!listRes.ok || !statsRes.ok) throw new Error('Backend unavailable');
      setExpenses(await listRes.json());
      setStats(await statsRes.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const visible = filter === 'ALL' ? expenses : expenses.filter((e) => e.status === filter);

  const advanceStatus = async (expense) => {
    const next =
      expense.status === 'PENDING' ? 'APPROVED' : expense.status === 'APPROVED' ? 'PAID' : 'PENDING';
    await fetch(`${API}/expenses/${expense.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...expense, status: next }),
    });
    load();
  };

  const createExpense = async (e) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    await fetch(`${API}/expenses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: form.get('title'),
        notes: form.get('notes') || '',
        amount: parseFloat(form.get('amount')) || 0,
        category: form.get('category'),
        paid_by: form.get('paid_by') || 'Self',
        status: 'PENDING',
      }),
    });
    e.currentTarget.reset();
    setShowForm(false);
    load();
  };

  const fmt = (n) => 'Rs.' + Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 });

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">E</span>
          <div><b>ExpensePilot</b><small>DevOps Capstone</small></div>
        </div>
        <nav>
          <a className="active"><LayoutDashboard size={17} /> <span>Dashboard</span></a>
          <a><Receipt size={17} /> <span>My Expenses</span></a>
          <a><Wallet size={17} /> <span>Budgets</span></a>
          <a><LineChart size={17} /> <span>Activity</span></a>
        </nav>
        <div className="side-bottom">
          <div className="upgrade">
            <strong>Spend with confidence.</strong>
            <p>Track, approve and audit every rupee.</p>
          </div>
          <div className="profile">
            <div className="avatar">AP</div>
            <div><b>Akshat Sipany</b><small>Finance Admin</small></div>
            <MoreHorizontal size={16} />
          </div>
        </div>
      </aside>
      <main className="main">
        <header>
          <div>
            <p className="eyebrow">FINANCE / OVERVIEW</p>
            <h1>Good morning, Akshat</h1>
            <p className="muted">Here is what your team is spending today.</p>
          </div>
          <button className="primary" onClick={() => setShowForm(true)}><Plus size={14} /> New expense</button>
        </header>
        {error && <div className="alert">Backend unavailable. Start the backend and PostgreSQL, then refresh.</div>}
        <section className="stats">
          <Stat label="Total spend" value={fmt(stats.total_spend)} icon={<Wallet size={17} />} />
          <Stat label="Pending" value={stats.pending} icon={<Clock size={17} />} />
          <Stat label="Approved" value={stats.approved} icon={<CircleCheck size={17} />} />
          <Stat label="Paid" value={stats.paid} icon={<BadgeCheck size={17} />} />
        </section>
        <section className="content-grid">
          <div className="panel tasks-panel">
            <div className="panel-head">
              <div>
                <h2>Expenses</h2>
                <p className="muted">Track spending across the team.</p>
              </div>
              <div className="filters">
                {STATUSES.map((s) => (
                  <button key={s} className={filter === s ? 'selected' : ''} onClick={() => setFilter(s)}>
                    {s === 'ALL' ? 'All' : s}
                  </button>
                ))}
              </div>
            </div>
            {loading ? (
              <div className="empty">Loading expenses...</div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr><th>Expense</th><th>Paid by</th><th>Category</th><th>Amount</th><th>Status</th><th></th></tr>
                  </thead>
                  <tbody>
                    {visible.map((t) => (
                      <tr key={t.id}>
                        <td>
                          <div className="task-title">
                            <span className={`dot ${t.status.toLowerCase()}`}></span>
                            <div><b>{t.title}</b><small>{t.notes}</small></div>
                          </div>
                        </td>
                        <td>{t.paid_by}</td>
                        <td><span className={`priority ${t.category.toLowerCase()}`}>{t.category}</span></td>
                        <td><b>{fmt(t.amount)}</b></td>
                        <td><span className={`status ${t.status.toLowerCase()}`}>{t.status}</span></td>
                        <td>
                          <button className="icon-btn" onClick={() => advanceStatus(t)} title="Advance status">
                            <ArrowRight size={15} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {!visible.length && <div className="empty">No expenses in this filter.</div>}
              </div>
            )}
          </div>
          <aside className="panel activity">
            <div className="panel-head">
              <div>
                <h2>Recent activity</h2>
                <p className="muted">Latest finance events.</p>
              </div>
            </div>
            <Activity icon={<CircleCheck size={14} />} text="AWS bill marked as paid" time="12 min ago" />
            <Activity icon={<Plane size={14} />} text="Flight to Mumbai approved" time="38 min ago" />
            <Activity icon={<CirclePlus size={14} />} text="New team lunch expense added" time="1 hr ago" />
            <Activity icon={<Rocket size={14} />} text="Deployment pipeline passed" time="2 hrs ago" />
            <div className="pipeline"><span>CI</span><i></i><span>Build</span><i></i><span>Scan</span><i></i><span>Deploy</span></div>
          </aside>
        </section>
        {showForm && (
          <div className="modal-backdrop">
            <form className="modal" onSubmit={createExpense}>
              <div className="modal-head">
                <div>
                  <p className="eyebrow">LOG EXPENSE</p>
                  <h2>Add a new expense</h2>
                </div>
                <button type="button" className="close" onClick={() => setShowForm(false)}><X size={18} /></button>
              </div>
              <label>Expense title<input name="title" required placeholder="e.g. Flight to Mumbai" /></label>
              <label>Notes<textarea name="notes" placeholder="What was this spend for?" /></label>
              <div className="form-row">
                <label>Amount (Rs.)<input name="amount" type="number" min="0" step="0.01" required placeholder="e.g. 2500" /></label>
                <label>Category
                  <select name="category">
                    <option>FOOD</option>
                    <option>TRAVEL</option>
                    <option>BILLS</option>
                    <option>OTHER</option>
                  </select>
                </label>
              </div>
              <div className="form-row">
                <label>Paid by<input name="paid_by" defaultValue="Akshat Sipany" /></label>
                <label>Note<small style={{ fontWeight: 400 }}>Starts as PENDING</small></label>
              </div>
              <button className="primary full">Log expense</button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}

function Stat({ label, value, icon }) {
  return (
    <div className="stat">
      <div className="stat-icon">{icon}</div>
      <div>
        <small>{label}</small>
        <strong>{value}</strong>
        <span>Updated just now</span>
      </div>
    </div>
  );
}

function Activity({ icon, text, time }) {
  return (
    <div className="activity-row">
      <span className="activity-icon">{icon}</span>
      <div>
        <b>{text}</b>
        <small>{time}</small>
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
