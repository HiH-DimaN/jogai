from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # telegram_id
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    language_code: Mapped[str | None] = mapped_column(String(10))
    locale: Mapped[str] = mapped_column(String(10), default="pt_BR")
    geo: Mapped[str] = mapped_column(String(5), default="BR")
    preferred_games: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    preferred_deposit: Mapped[str | None] = mapped_column(String(50))
    preferred_payment: Mapped[str | None] = mapped_column(String(50))
    jogai_coins: Mapped[int] = mapped_column(Integer, default=0)
    is_pro: Mapped[bool] = mapped_column(Boolean, default=False)
    pro_expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    referred_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id")
    )
    referral_code: Mapped[str | None] = mapped_column(String(20), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    referrer: Mapped["User | None"] = relationship(
        "User", remote_side="User.id", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_users_locale", "locale"),
        Index("idx_users_geo", "geo"),
        Index("idx_users_referral_code", "referral_code"),
    )


class Casino(Base):
    __tablename__ = "casinos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(Text)
    description_pt: Mapped[str | None] = mapped_column(Text)
    description_es: Mapped[str | None] = mapped_column(Text)
    min_deposit: Mapped[float | None] = mapped_column(Numeric(10, 2))
    pix_supported: Mapped[bool] = mapped_column(Boolean, default=True)
    spei_supported: Mapped[bool] = mapped_column(Boolean, default=False)
    crypto_supported: Mapped[bool] = mapped_column(Boolean, default=False)
    withdrawal_time: Mapped[str | None] = mapped_column(String(100))
    affiliate_program: Mapped[str | None] = mapped_column(String(100))
    affiliate_link_template: Mapped[str | None] = mapped_column(Text)
    ref_id: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    geo: Mapped[list[str]] = mapped_column(ARRAY(Text), default=["BR"])
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    bonuses: Mapped[list["Bonus"]] = relationship(
        "Bonus", back_populates="casino", lazy="selectin"
    )


class Bonus(Base):
    __tablename__ = "bonuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    casino_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("casinos.id")
    )
    title_pt: Mapped[str | None] = mapped_column(String(500))
    title_es: Mapped[str | None] = mapped_column(String(500))
    bonus_percent: Mapped[int | None] = mapped_column(Integer)
    max_bonus_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    max_bonus_currency: Mapped[str] = mapped_column(String(5), default="BRL")
    wagering_multiplier: Mapped[float | None] = mapped_column(Numeric(5, 1))
    wagering_deadline_days: Mapped[int | None] = mapped_column(Integer)
    max_bet: Mapped[float | None] = mapped_column(Numeric(10, 2))
    free_spins: Mapped[int] = mapped_column(Integer, default=0)
    no_deposit: Mapped[bool] = mapped_column(Boolean, default=False)
    jogai_score: Mapped[float | None] = mapped_column(Numeric(3, 1))
    verdict_key: Mapped[str | None] = mapped_column(String(50))
    expected_loss: Mapped[float | None] = mapped_column(Numeric(10, 2))
    profit_probability: Mapped[float | None] = mapped_column(Numeric(5, 2))
    affiliate_link: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    geo: Mapped[list[str]] = mapped_column(ARRAY(Text), default=["BR"])
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    casino: Mapped["Casino | None"] = relationship(
        "Casino", back_populates="bonuses", lazy="selectin"
    )

    __table_args__ = (
        Index(
            "idx_bonuses_active_geo",
            "is_active",
            "geo",
            postgresql_where=(is_active.is_(True)),
        ),
        Index("idx_bonuses_score", jogai_score.desc()),
    )


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id")
    )
    bonus_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("bonuses.id")
    )
    casino_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("casinos.id")
    )
    source: Mapped[str | None] = mapped_column(String(50))
    locale: Mapped[str | None] = mapped_column(String(10))
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    __table_args__ = (Index("idx_clicks_locale", "locale"),)


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id")
    )
    input_text: Mapped[str | None] = mapped_column(Text)
    input_type: Mapped[str] = mapped_column(String(20), default="text")
    parsed_bonus_percent: Mapped[int | None] = mapped_column(Integer)
    parsed_wagering: Mapped[float | None] = mapped_column(Numeric(5, 1))
    parsed_deadline: Mapped[int | None] = mapped_column(Integer)
    parsed_max_bet: Mapped[float | None] = mapped_column(Numeric(10, 2))
    jogai_score: Mapped[float | None] = mapped_column(Numeric(3, 1))
    verdict_key: Mapped[str | None] = mapped_column(String(50))
    ai_response: Mapped[str | None] = mapped_column(Text)
    locale: Mapped[str] = mapped_column(String(10), default="pt_BR")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class Bet(Base):
    __tablename__ = "bets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id")
    )
    casino_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("casinos.id")
    )
    game_type: Mapped[str | None] = mapped_column(String(50))
    game_name: Mapped[str | None] = mapped_column(String(255))
    bet_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    bet_currency: Mapped[str] = mapped_column(String(5), default="BRL")
    result_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    profit: Mapped[float | None] = mapped_column(Numeric(10, 2))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_type: Mapped[str | None] = mapped_column(String(50))
    title: Mapped[str | None] = mapped_column(String(500))
    content_pt: Mapped[str | None] = mapped_column(Text)
    content_es: Mapped[str | None] = mapped_column(Text)
    media_url: Mapped[str | None] = mapped_column(Text)
    bonus_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("bonuses.id")
    )
    casino_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("casinos.id")
    )
    telegram_message_id: Mapped[int | None] = mapped_column(BigInteger)
    telegram_channel: Mapped[str | None] = mapped_column(String(50))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    geo: Mapped[str] = mapped_column(String(5), default="BR")
    status: Mapped[str] = mapped_column(String(20), default="draft")

    __table_args__ = (Index("idx_posts_geo", "geo"),)


class SportPick(Base):
    __tablename__ = "sport_picks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    match_name: Mapped[str | None] = mapped_column(String(500))
    league: Mapped[str | None] = mapped_column(String(100))
    pick_description_pt: Mapped[str | None] = mapped_column(Text)
    pick_description_es: Mapped[str | None] = mapped_column(Text)
    odds: Mapped[float | None] = mapped_column(Numeric(5, 2))
    analysis_pt: Mapped[str | None] = mapped_column(Text)
    analysis_es: Mapped[str | None] = mapped_column(Text)
    casino_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("casinos.id")
    )
    affiliate_link: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str | None] = mapped_column(String(20))
    match_date: Mapped[datetime | None] = mapped_column(DateTime)
    geo: Mapped[list[str]] = mapped_column(ARRAY(Text), default=["BR"])
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    __table_args__ = (Index("idx_sport_picks_geo", "geo"),)


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referrer_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id")
    )
    referred_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id")
    )
    coins_awarded: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
