"""Create clubs, events, and registrations tables with seed data.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-10-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Enums ---
    club_category = postgresql.ENUM(
        "TECH", "ARTS", "SPORTS", "ACADEMIC", "SOCIAL", "CULTURAL",
        name="clubcategory", create_type=True
    )
    event_status = postgresql.ENUM(
        "DRAFT", "PUBLISHED", "COMPLETED", "CANCELLED",
        name="eventstatus", create_type=True
    )
    registration_status = postgresql.ENUM(
        "CONFIRMED", "CANCELLED",
        name="registrationstatus", create_type=True
    )

    # --- Clubs table ---
    op.create_table(
        "clubs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", club_category, nullable=False, server_default="SOCIAL"),
        sa.Column("lead_email", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("slug", name="uq_clubs_slug"),
    )
    op.create_index("ix_clubs_id", "clubs", ["id"])
    op.create_index("ix_clubs_slug", "clubs", ["slug"], unique=True)

    # --- Events table ---
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("club_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("event_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("registered_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("status", event_status, nullable=False, server_default="DRAFT"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_events_id", "events", ["id"])
    op.create_index("ix_events_club_id", "events", ["club_id"])

    # --- Registrations table ---
    op.create_table(
        "registrations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("student_name", sa.String(length=200), nullable=False),
        sa.Column("student_email", sa.String(length=255), nullable=False),
        sa.Column("student_id", sa.String(length=50), nullable=True),
        sa.Column("status", registration_status, nullable=False, server_default="CONFIRMED"),
        sa.Column(
            "registered_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "event_id", "student_email", name="uq_registration_event_student"
        ),
    )
    op.create_index("ix_registrations_id", "registrations", ["id"])
    op.create_index("ix_registrations_event_id", "registrations", ["event_id"])

    # --- Seed data ---
    op.execute("""
        INSERT INTO clubs (name, slug, description, category, lead_email) VALUES
        ('CodeCraft Society', 'codecraft-society', 'Competitive programming and open-source contributions', 'TECH', 'codecraft@campus.edu'),
        ('Drama & Theatre Guild', 'drama-theatre-guild', 'Stage performances, improv nights, and script workshops', 'ARTS', 'drama@campus.edu'),
        ('Campus Football Club', 'campus-football-club', 'Weekly matches, tournaments, and fitness sessions', 'SPORTS', 'football@campus.edu'),
        ('Robotics & AI Lab', 'robotics-ai-lab', 'Autonomous systems, ML projects, and hackathon teams', 'TECH', 'robotics@campus.edu'),
        ('Photography Circle', 'photography-circle', 'Weekly shoots, darkroom sessions, and photo exhibitions', 'ARTS', 'photo@campus.edu'),
        ('Debate & Oratory Club', 'debate-oratory-club', 'Parliamentary debates, MUN preparation, and public speaking', 'ACADEMIC', 'debate@campus.edu')
    """)

    op.execute("""
        INSERT INTO events (club_id, title, description, location, event_date, capacity, registered_count, category, status)
        SELECT
            c.id,
            'Hackathon 2026: Build for Good',
            'A 24-hour hackathon to build tech solutions for social impact. Form teams of 2-4.',
            'Engineering Block, Lab 301',
            NOW() + INTERVAL '7 days',
            80,
            12,
            'TECH',
            'PUBLISHED'::eventstatus
        FROM clubs c WHERE c.slug = 'codecraft-society'
        UNION ALL
        SELECT
            c.id,
            'Open Mic Night: Season Finale',
            'Showcase your talent - poetry, music, stand-up comedy, and spoken word welcome.',
            'Amphitheatre, Main Quad',
            NOW() + INTERVAL '3 days',
            200,
            45,
            'ARTS',
            'PUBLISHED'::eventstatus
        FROM clubs c WHERE c.slug = 'drama-theatre-guild'
        UNION ALL
        SELECT
            c.id,
            'Intra-College Football Tournament',
            'Round-robin group stage leading to knockout finals. Register your team of 11.',
            'Sports Ground, North Campus',
            NOW() + INTERVAL '14 days',
            120,
            33,
            'SPORTS',
            'PUBLISHED'::eventstatus
        FROM clubs c WHERE c.slug = 'campus-football-club'
        UNION ALL
        SELECT
            c.id,
            'Intro to Robotics Workshop',
            'Hands-on session: build and program a line-following robot. Beginners welcome.',
            'Innovation Hub, Room 204',
            NOW() + INTERVAL '5 days',
            40,
            28,
            'TECH',
            'PUBLISHED'::eventstatus
        FROM clubs c WHERE c.slug = 'robotics-ai-lab'
        UNION ALL
        SELECT
            c.id,
            'Golden Hour Photo Walk',
            'Guided campus photo walk at sunset. Bring your DSLR or phone camera.',
            'Meet at Main Gate',
            NOW() + INTERVAL '2 days',
            30,
            22,
            'ARTS',
            'PUBLISHED'::eventstatus
        FROM clubs c WHERE c.slug = 'photography-circle'
        UNION ALL
        SELECT
            c.id,
            'Inter-College Debate Championship',
            'Compete against teams from 8 colleges on global policy motions. Registration mandatory.',
            'Seminar Hall A',
            NOW() + INTERVAL '10 days',
            60,
            15,
            'ACADEMIC',
            'PUBLISHED'::eventstatus
        FROM clubs c WHERE c.slug = 'debate-oratory-club'
    """)


def downgrade() -> None:
    op.drop_table("registrations")
    op.drop_table("events")
    op.drop_table("clubs")
    op.execute("DROP TYPE IF EXISTS registrationstatus")
    op.execute("DROP TYPE IF EXISTS eventstatus")
    op.execute("DROP TYPE IF EXISTS clubcategory")
