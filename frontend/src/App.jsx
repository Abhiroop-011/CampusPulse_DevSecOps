import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Calendar,
  Clock,
  MapPin,
  Users,
  CheckCircle2,
  AlertCircle,
  X,
  Search,
  Plus,
  RefreshCw,
  Sparkles,
  Building2,
  Ticket,
  ChevronRight,
  Trash2,
} from 'lucide-react';
import * as api from './api';

export default function App() {
  // Navigation
  const [activeTab, setActiveTab] = useState('events'); // 'events' | 'clubs'

  // Data state
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);
  const [clubs, setClubs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [backendOnline, setBackendOnline] = useState(false);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClub, setSelectedClub] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');

  // Modals
  const [registerModalEvent, setRegisterModalEvent] = useState(null);
  const [createEventModal, setCreateEventModal] = useState(false);
  const [attendeesModalEvent, setAttendeesModalEvent] = useState(null);
  const [attendeesList, setAttendeesList] = useState([]);
  const [loadingAttendees, setLoadingAttendees] = useState(false);

  // Form states
  const [regForm, setRegForm] = useState({
    student_name: '',
    student_email: '',
    student_id: '',
  });
  const [submittingReg, setSubmittingReg] = useState(false);

  const [newEvent, setNewEvent] = useState({
    title: '',
    club_id: '',
    description: '',
    location: '',
    event_date: '',
    capacity: 50,
    category: 'TECH',
    status: 'PUBLISHED',
  });
  const [submittingNewEvent, setSubmittingNewEvent] = useState(false);

  // Notifications
  const [toast, setToast] = useState(null); // { type: 'success' | 'error', message: string }

  const showToast = useCallback((type, message) => {
    setToast({ type, message });
    setTimeout(() => {
      setToast((prev) => (prev?.message === message ? null : prev));
    }, 4500);
  }, []);

  // Initial load & refresh
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      // Check health
      try {
        const healthRes = await fetch('/api/stats');
        setBackendOnline(healthRes.ok);
      } catch {
        setBackendOnline(false);
      }

      const [statsData, eventsData, clubsData] = await Promise.all([
        api.getStats().catch(() => null),
        api.getEvents().catch(() => []),
        api.getClubs().catch(() => []),
      ]);

      setStats(statsData);
      setEvents(eventsData);
      setClubs(clubsData);
      if (clubsData.length > 0) {
        setNewEvent((prev) => (prev.club_id ? prev : { ...prev, club_id: clubsData[0].id }));
      }
    } catch (err) {
      showToast('error', `Failed to load campus data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    let ignore = false;
    const fetchInitial = async () => {
      if (!ignore) {
        await loadData();
      }
    };
    fetchInitial();
    return () => {
      ignore = true;
    };
  }, [loadData]);

  // Filtered Events
  const filteredEvents = useMemo(() => {
    return events.filter((ev) => {
      const matchesSearch =
        searchQuery === '' ||
        ev.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (ev.description && ev.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (ev.location && ev.location.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (ev.club_name && ev.club_name.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesClub =
        selectedClub === 'ALL' || String(ev.club_id) === String(selectedClub);

      const matchesStatus =
        selectedStatus === 'ALL' || ev.status === selectedStatus;

      return matchesSearch && matchesClub && matchesStatus;
    });
  }, [events, searchQuery, selectedClub, selectedStatus]);

  // Handle Event Registration
  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    if (!registerModalEvent) return;
    setSubmittingReg(true);
    try {
      const payload = {
        student_name: regForm.student_name.trim(),
        student_email: regForm.student_email.trim(),
        student_id: regForm.student_id.trim() || undefined,
      };

      await api.registerForEvent(registerModalEvent.id, payload);
      showToast('success', `Registered successfully for "${registerModalEvent.title}"!`);
      setRegisterModalEvent(null);
      setRegForm({ student_name: '', student_email: '', student_id: '' });
      await loadData();
    } catch (err) {
      showToast('error', err.message || 'Registration failed');
    } finally {
      setSubmittingReg(false);
    }
  };

  // Open Attendees Modal
  const openAttendeesModal = async (event) => {
    setAttendeesModalEvent(event);
    setLoadingAttendees(true);
    try {
      const data = await api.getRegistrations(event.id);
      setAttendeesList(data);
    } catch (err) {
      showToast('error', `Could not load attendees: ${err.message}`);
      setAttendeesList([]);
    } finally {
      setLoadingAttendees(false);
    }
  };

  // Handle Cancel Registration
  const handleCancelRegistration = async (eventId, regId, studentName) => {
    if (!window.confirm(`Cancel registration for ${studentName}?`)) return;
    try {
      await api.cancelRegistration(eventId, regId);
      showToast('success', `Cancelled registration for ${studentName}`);
      // Refresh attendees modal
      const data = await api.getRegistrations(eventId);
      setAttendeesList(data);
      await loadData();
    } catch (err) {
      showToast('error', `Cancel failed: ${err.message}`);
    }
  };

  // Handle Create Event
  const handleCreateEvent = async (e) => {
    e.preventDefault();
    setSubmittingNewEvent(true);
    try {
      const payload = {
        title: newEvent.title.trim(),
        club_id: parseInt(newEvent.club_id, 10),
        description: newEvent.description.trim() || undefined,
        location: newEvent.location.trim() || undefined,
        event_date: new Date(newEvent.event_date).toISOString(),
        capacity: parseInt(newEvent.capacity, 10),
        category: newEvent.category,
        status: newEvent.status,
      };

      await api.createEvent(payload);
      showToast('success', `Event "${payload.title}" created successfully!`);
      setCreateEventModal(false);
      setNewEvent({
        title: '',
        club_id: clubs[0]?.id || '',
        description: '',
        location: '',
        event_date: '',
        capacity: 50,
        category: 'TECH',
        status: 'PUBLISHED',
      });
      await loadData();
    } catch (err) {
      showToast('error', `Create event failed: ${err.message}`);
    } finally {
      setSubmittingNewEvent(false);
    }
  };

  // Helper date formatters
  const formatEventDate = (dateStr) => {
    try {
      const d = new Date(dateStr);
      return {
        month: d.toLocaleString('en-US', { month: 'short' }),
        day: d.getDate(),
        full: d.toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        }),
        time: d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      };
    } catch {
      return { month: 'TBD', day: '--', full: dateStr, time: '' };
    }
  };

  // Capacity calculation helper
  const getCapacityFillClass = (reg, cap) => {
    if (!cap || cap === 0) return 'capacity-fill-low';
    const pct = (reg / cap) * 100;
    if (pct >= 100) return 'capacity-fill-full';
    if (pct >= 80) return 'capacity-fill-high';
    if (pct >= 50) return 'capacity-fill-medium';
    return 'capacity-fill-low';
  };

  return (
    <div className="app-layout">
      {/* ── Navbar ─────────────────────────────────────────────── */}
      <header className="navbar">
        <div className="navbar-inner">
          <div className="navbar-brand">
            <div className="navbar-logo">CP</div>
            <div>
              <div className="navbar-title">CampusPulse</div>
              <div className="navbar-subtitle">Campus Events & Club Management</div>
            </div>
          </div>

          <nav className="navbar-nav">
            <button
              className={`nav-btn ${activeTab === 'events' ? 'active' : ''}`}
              onClick={() => setActiveTab('events')}
            >
              Events
            </button>
            <button
              className={`nav-btn ${activeTab === 'clubs' ? 'active' : ''}`}
              onClick={() => setActiveTab('clubs')}
            >
              Clubs
            </button>
          </nav>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div className="navbar-status" title={backendOnline ? 'Backend API is running' : 'Backend is unreachable'}>
              <div
                className="status-dot"
                style={{
                  backgroundColor: backendOnline ? 'var(--accent-green)' : 'var(--accent-red)',
                }}
              />
              <span>{backendOnline ? 'API Connected' : 'Connecting...'}</span>
            </div>

            <button
              className="btn btn-primary btn-sm"
              onClick={() => setCreateEventModal(true)}
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Plus size={14} />
              <span>Create Event</span>
            </button>

            <button
              className="btn btn-ghost btn-sm"
              onClick={loadData}
              title="Refresh platform data"
              disabled={loading}
              style={{ color: 'var(--brown-200)', border: '1px solid var(--brown-700)' }}
            >
              <RefreshCw size={14} className={loading ? 'spinner' : ''} />
            </button>
          </div>
        </div>
      </header>

      {/* ── Toast Alert ────────────────────────────────────────── */}
      {toast && (
        <div style={{ maxWidth: '1280px', margin: '16px auto 0', padding: '0 24px', width: '100%' }}>
          <div className={`alert ${toast.type === 'success' ? 'alert-success' : 'alert-error'}`}>
            {toast.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
            <span style={{ flex: 1 }}>{toast.message}</span>
            <button
              onClick={() => setToast(null)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}
            >
              <X size={16} />
            </button>
          </div>
        </div>
      )}

      {/* ── Main Content ───────────────────────────────────────── */}
      <main className="main-content">
        {/* Page Hero */}
        <section className="page-hero">
          <div style={{ position: 'relative', zIndex: 1 }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                background: 'rgba(255,255,255,0.12)',
                color: 'var(--brown-200)',
                padding: '4px 12px',
                borderRadius: '999px',
                fontSize: '0.75rem',
                fontWeight: 600,
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
                marginBottom: '12px',
              }}
            >
              <Sparkles size={13} color="var(--brown-300)" />
              Campus Activity Hub · DevSecOps Platform
            </span>
            <h1 className="page-hero-title">Experience Campus Life in Full Rhythm</h1>
            <p className="page-hero-subtitle">
              Discover official club workshops, hackathons, seminars, and sports meets.
              Reserve your spot instantly with live seat tracking.
            </p>
          </div>
        </section>

        {/* Stats Grid */}
        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-card-header">
              <span className="stat-label">Total Events</span>
              <div className="stat-icon brown">
                <Calendar size={20} />
              </div>
            </div>
            <div className="stat-value">{stats ? stats.total_events : '—'}</div>
            <div className="stat-sub">
              {stats ? `${stats.published_events} currently published` : 'Loading metrics...'}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-card-header">
              <span className="stat-label">Active Clubs</span>
              <div className="stat-icon terra">
                <Building2 size={20} />
              </div>
            </div>
            <div className="stat-value">{stats ? stats.total_clubs : '—'}</div>
            <div className="stat-sub">Student organizations & teams</div>
          </div>

          <div className="stat-card">
            <div className="stat-card-header">
              <span className="stat-label">Confirmed Seats</span>
              <div className="stat-icon amber">
                <Ticket size={20} />
              </div>
            </div>
            <div className="stat-value">{stats ? stats.total_registrations : '—'}</div>
            <div className="stat-sub">Student registrations logged</div>
          </div>

          <div className="stat-card">
            <div className="stat-card-header">
              <span className="stat-label">Avg Utilization</span>
              <div className="stat-icon green">
                <Users size={20} />
              </div>
            </div>
            <div className="stat-value">
              {stats ? `${stats.average_capacity_utilization}%` : '—'}
            </div>
            <div className="stat-sub">Capacity fill rate across campus</div>
          </div>
        </section>

        {/* Tab Navigation */}
        <div className="tabs">
          <button
            className={`tab-btn ${activeTab === 'events' ? 'active' : ''}`}
            onClick={() => setActiveTab('events')}
          >
            <Calendar size={16} />
            <span>Campus Events</span>
            <span className="tab-count">{events.length}</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'clubs' ? 'active' : ''}`}
            onClick={() => setActiveTab('clubs')}
          >
            <Building2 size={16} />
            <span>Student Clubs</span>
            <span className="tab-count">{clubs.length}</span>
          </button>
        </div>

        {/* ── EVENTS TAB ────────────────────────────────────────── */}
        {activeTab === 'events' && (
          <div>
            {/* Filter Bar */}
            <div className="filter-bar">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: '1 1 240px' }}>
                <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', marginLeft: '12px' }} />
                <input
                  type="text"
                  placeholder="Search events, clubs, venues..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                  style={{ paddingLeft: '36px', width: '100%' }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                <span className="filter-label">Club:</span>
                <button
                  className={`filter-btn ${selectedClub === 'ALL' ? 'active' : ''}`}
                  onClick={() => setSelectedClub('ALL')}
                >
                  All
                </button>
                {clubs.slice(0, 4).map((c) => (
                  <button
                    key={c.id}
                    className={`filter-btn ${selectedClub === String(c.id) ? 'active' : ''}`}
                    onClick={() => setSelectedClub(String(c.id))}
                  >
                    {c.name.split(' ')[0]}
                  </button>
                ))}

                <span className="filter-label" style={{ marginLeft: '8px' }}>Status:</span>
                {['ALL', 'PUBLISHED', 'DRAFT'].map((st) => (
                  <button
                    key={st}
                    className={`filter-btn ${selectedStatus === st ? 'active' : ''}`}
                    onClick={() => setSelectedStatus(st)}
                  >
                    {st === 'ALL' ? 'All' : st}
                  </button>
                ))}
              </div>
            </div>

            {/* Events Grid */}
            {loading ? (
              <div className="loading-wrap">
                <div className="spinner" />
                <p>Loading events from database...</p>
              </div>
            ) : filteredEvents.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📅</div>
                <div className="empty-state-title">No events match your criteria</div>
                <div className="empty-state-msg">
                  Try clearing search filters or create a new event.
                </div>
              </div>
            ) : (
              <div className="events-grid">
                {filteredEvents.map((ev) => {
                  const dateInfo = formatEventDate(ev.event_date);
                  const isFull = ev.spots_remaining !== null && ev.spots_remaining <= 0;
                  const pct = ev.capacity > 0 ? Math.min(100, Math.round((ev.registered_count / ev.capacity) * 100)) : 0;
                  const fillClass = getCapacityFillClass(ev.registered_count, ev.capacity);

                  return (
                    <article key={ev.id} className="event-card">
                      <div className="event-card-top">
                        <div className="event-date-badge">
                          <div className="event-date-month">{dateInfo.month}</div>
                          <div className="event-date-day">{dateInfo.day}</div>
                        </div>

                        <span className={`event-status-badge badge-${ev.status.toLowerCase()}`}>
                          {ev.status}
                        </span>
                      </div>

                      <div className="event-club-pill">
                        <Building2 size={12} />
                        <span>{ev.club_name || 'Campus Club'}</span>
                      </div>

                      <h3 className="event-title">{ev.title}</h3>

                      {ev.description && (
                        <p
                          style={{
                            fontSize: '0.85rem',
                            color: 'var(--text-secondary)',
                            lineHeight: 1.45,
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                          }}
                        >
                          {ev.description}
                        </p>
                      )}

                      <div className="event-meta">
                        <div className="event-meta-row">
                          <Clock size={14} />
                          <span>{dateInfo.full} · {dateInfo.time}</span>
                        </div>
                        {ev.location && (
                          <div className="event-meta-row">
                            <MapPin size={14} />
                            <span>{ev.location}</span>
                          </div>
                        )}
                      </div>

                      {/* Capacity Progress Bar */}
                      <div className="capacity-bar-wrap">
                        <div className="capacity-label">
                          <span>Capacity ({pct}%)</span>
                          <span>{ev.registered_count} / {ev.capacity}</span>
                        </div>
                        <div className="capacity-bar">
                          <div
                            className={`capacity-bar-fill ${fillClass}`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>

                      {/* Footer Actions */}
                      <div className="event-card-footer">
                        <div className={`spots-remaining ${isFull ? 'full' : ''}`}>
                          {isFull ? (
                            <span style={{ color: 'var(--accent-red)', fontWeight: 600 }}>Event Full</span>
                          ) : (
                            <span>{ev.spots_remaining} spots open</span>
                          )}
                        </div>

                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => openAttendeesModal(ev)}
                            title="View registered attendees"
                          >
                            <Users size={14} />
                          </button>

                          <button
                            className="btn btn-primary btn-sm"
                            disabled={isFull || ev.status !== 'PUBLISHED'}
                            onClick={() => {
                              setRegisterModalEvent(ev);
                              setRegForm({ student_name: '', student_email: '', student_id: '' });
                            }}
                          >
                            {isFull ? 'Full' : 'Register'}
                          </button>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ── CLUBS TAB ─────────────────────────────────────────── */}
        {activeTab === 'clubs' && (
          <div>
            <div className="section-header">
              <div>
                <h2 className="section-title">Official Student Organizations</h2>
                <div className="section-subtitle">
                  Browse recognized university clubs across tech, arts, sports, and academics.
                </div>
              </div>
            </div>

            <div className="clubs-grid">
              {clubs.map((club) => {
                const catClass = `cat-${club.category || 'SOCIAL'}`;
                return (
                  <article key={club.id} className="club-card">
                    <div className="club-card-header">
                      <div className="club-avatar" style={{ background: 'var(--brown-100)', color: 'var(--brown-800)' }}>
                        <Building2 size={22} />
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <h3 className="club-name">{club.name}</h3>
                        <span className={`club-category-tag ${catClass}`}>
                          {club.category}
                        </span>
                      </div>
                    </div>

                    <p className="club-description">{club.description || 'No description provided.'}</p>

                    <div className="club-stats-row">
                      <div className="club-stat">
                        <Calendar size={13} />
                        <span>{club.event_count || 0} events scheduled</span>
                      </div>
                    </div>

                    <div style={{ marginTop: 'auto', paddingTop: '12px', borderTop: '1px solid var(--border-light)' }}>
                      <button
                        className="btn btn-secondary btn-sm"
                        style={{ width: '100%' }}
                        onClick={() => {
                          setSelectedClub(String(club.id));
                          setActiveTab('events');
                        }}
                      >
                        <span>View Club Events</span>
                        <ChevronRight size={14} />
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        )}
      </main>

      {/* ── MODAL: Register for Event ──────────────────────────── */}
      {registerModalEvent && (
        <div className="modal-overlay" onClick={() => setRegisterModalEvent(null)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Event Registration</h3>
              <button className="modal-close" onClick={() => setRegisterModalEvent(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-event-summary">
              <div className="modal-event-summary-title">{registerModalEvent.title}</div>
              <div className="modal-event-summary-meta">
                {formatEventDate(registerModalEvent.event_date).full} · {registerModalEvent.location}
              </div>
              <div style={{ marginTop: '6px', fontSize: '0.8rem', color: 'var(--accent-primary)', fontWeight: 600 }}>
                {registerModalEvent.spots_remaining} spots remaining
              </div>
            </div>

            <form onSubmit={handleRegisterSubmit}>
              <div className="form-group">
                <label className="form-label">Full Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Alex Morgan"
                  className="form-input"
                  value={regForm.student_name}
                  onChange={(e) => setRegForm({ ...regForm, student_name: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Student Email *</label>
                <input
                  type="email"
                  required
                  placeholder="alex.morgan@university.edu"
                  className="form-input"
                  value={regForm.student_email}
                  onChange={(e) => setRegForm({ ...regForm, student_email: e.target.value })}
                />
                <div className="form-hint">Confirmation pass will be linked to this email.</div>
              </div>

              <div className="form-group">
                <label className="form-label">Student ID (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. CS-2026-891"
                  className="form-input"
                  value={regForm.student_id}
                  onChange={(e) => setRegForm({ ...regForm, student_id: e.target.value })}
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => setRegisterModalEvent(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submittingReg}
                >
                  {submittingReg ? 'Confirming...' : 'Confirm Registration'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── MODAL: Attendees List ──────────────────────────────── */}
      {attendeesModalEvent && (
        <div className="modal-overlay" onClick={() => setAttendeesModalEvent(null)}>
          <div className="modal-box" style={{ maxWidth: '580px' }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3 className="modal-title">Registered Attendees</h3>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {attendeesModalEvent.title}
                </div>
              </div>
              <button className="modal-close" onClick={() => setAttendeesModalEvent(null)}>
                <X size={18} />
              </button>
            </div>

            {loadingAttendees ? (
              <div className="loading-wrap" style={{ padding: '32px 0' }}>
                <div className="spinner" />
                <p>Loading attendee list...</p>
              </div>
            ) : attendeesList.length === 0 ? (
              <div className="empty-state" style={{ padding: '32px 0' }}>
                <div className="empty-state-icon">🎟️</div>
                <div className="empty-state-title">No registrations yet</div>
                <div className="empty-state-msg">Be the first student to reserve a seat!</div>
              </div>
            ) : (
              <div style={{ maxHeight: '360px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {attendeesList.map((att) => (
                  <div
                    key={att.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 14px',
                      background: 'var(--bg-subtle)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-light)',
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                        {att.student_name}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        {att.student_email} {att.student_id ? `· ${att.student_id}` : ''}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span
                        style={{
                          fontSize: '0.72rem',
                          padding: '2px 8px',
                          borderRadius: '999px',
                          fontWeight: 600,
                          backgroundColor:
                            att.status === 'CONFIRMED'
                              ? 'var(--accent-green-bg)'
                              : 'var(--brown-100)',
                          color:
                            att.status === 'CONFIRMED'
                              ? 'var(--accent-green)'
                              : 'var(--text-secondary)',
                        }}
                      >
                        {att.status}
                      </span>
                      {att.status === 'CONFIRMED' && (
                        <button
                          className="btn btn-ghost btn-sm"
                          style={{ color: 'var(--accent-red)', padding: '4px' }}
                          title="Cancel Registration"
                          onClick={() => handleCancelRegistration(attendeesModalEvent.id, att.id, att.student_name)}
                        >
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="modal-actions" style={{ marginTop: '20px' }}>
              <button className="btn btn-secondary" onClick={() => setAttendeesModalEvent(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── MODAL: Create Event ────────────────────────────────── */}
      {createEventModal && (
        <div className="modal-overlay" onClick={() => setCreateEventModal(false)}>
          <div className="modal-box" style={{ maxWidth: '520px' }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Create Campus Event</h3>
              <button className="modal-close" onClick={() => setCreateEventModal(false)}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateEvent}>
              <div className="form-group">
                <label className="form-label">Event Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Annual Campus Hackathon 2026"
                  className="form-input"
                  value={newEvent.title}
                  onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label className="form-label">Host Club *</label>
                  <select
                    className="form-input"
                    value={newEvent.club_id}
                    onChange={(e) => setNewEvent({ ...newEvent, club_id: e.target.value })}
                    required
                  >
                    {clubs.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Category</label>
                  <select
                    className="form-input"
                    value={newEvent.category}
                    onChange={(e) => setNewEvent({ ...newEvent, category: e.target.value })}
                  >
                    <option value="TECH">Technology</option>
                    <option value="ARTS">Arts</option>
                    <option value="SPORTS">Sports</option>
                    <option value="ACADEMIC">Academic</option>
                    <option value="SOCIAL">Social</option>
                    <option value="CULTURAL">Cultural</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Date & Time *</label>
                <input
                  type="datetime-local"
                  required
                  className="form-input"
                  value={newEvent.event_date}
                  onChange={(e) => setNewEvent({ ...newEvent, event_date: e.target.value })}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label className="form-label">Venue / Location</label>
                  <input
                    type="text"
                    placeholder="e.g. Student Auditorium Hall A"
                    className="form-input"
                    value={newEvent.location}
                    onChange={(e) => setNewEvent({ ...newEvent, location: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Capacity *</label>
                  <input
                    type="number"
                    min="1"
                    max="5000"
                    required
                    className="form-input"
                    value={newEvent.capacity}
                    onChange={(e) => setNewEvent({ ...newEvent, capacity: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  rows="3"
                  className="form-input"
                  placeholder="Provide event details, prerequisites, or schedules..."
                  value={newEvent.description}
                  onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                  style={{ resize: 'vertical' }}
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => setCreateEventModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submittingNewEvent}
                >
                  {submittingNewEvent ? 'Publishing...' : 'Publish Event'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Footer ─────────────────────────────────────────────── */}
      <footer
        style={{
          borderTop: '1px solid var(--border-light)',
          background: 'var(--brown-900)',
          color: 'var(--brown-200)',
          padding: '28px 24px',
          marginTop: 'auto',
          fontSize: '0.85rem',
        }}
      >
        <div
          style={{
            maxWidth: '1280px',
            margin: '0 auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div>
            <strong style={{ color: '#fff' }}>CampusPulse</strong> — Production DevSecOps Architecture Capstone
          </div>
          <div style={{ color: 'var(--brown-300)', fontSize: '0.8rem' }}>
            Built with React 19, FastAPI, PostgreSQL, Docker, Helm, Trivy & Argo CD
          </div>
        </div>
      </footer>
    </div>
  );
}
